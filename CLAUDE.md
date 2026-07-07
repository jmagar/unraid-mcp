# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An Unraid plugin that runs [Incus](https://linuxcontainers.org/incus/) system containers ("jails"/"dev containers") for isolated coding-agent and stdio-MCP workspaces. Each container gets a dedicated NAT bridge that is firewalled off from the LAN (egress deny-list) while keeping Internet access, so an agent — or a compromised dependency in its toolchain — can't reach the NAS, routers, or other internal services.

The repo has three pieces that must be understood together:

1. **`incus.plg` + `source/usr/local/emhttp/plugins/incus/`** — the classic Unraid OS plugin (XML manifest + shell). Ships a private-prefixed, repackaged Incus runtime (from `packages/*.txz`), the daemon lifecycle (`rc.incus`), and array start/stop hooks. This is the only piece that can actually install/run `incusd` — the API plugin below has no way to do OS-level work.
2. **`source/.../scripts/incus-init.sh`** — config-driven, idempotent preseed run on every array start (and via the settings page's Apply button, see below). Reads `/boot/config/plugins/incus/incus.cfg` and ensures the storage pool, the `agent-block-lan` network ACL, the `agentbr0` bridge, and the `agent-jail` profile all exist and match config. Safe to re-run; never hardcodes policy.
3. **`unraid-api-plugin-incus/`** — a NestJS/GraphQL plugin for Unraid's newer `unraid-api` system, plus a `web/` Vue 3 frontend compiled to a custom element embedded in the classic settings page. Manages containers/images at runtime by speaking the Incus REST API directly over its unix socket — never shells out to the `incus` CLI for anything the API can do.

`incus.cfg` is the single source of truth for both the shell init and the API plugin; the API plugin mirrors it into `incus.json` and keeps both in sync (`config-sync.service.ts`).

## Build & typecheck

There is no automated test suite in this repo. Verification is: typecheck → build → deploy to a real Unraid box → verify live (see "Deploying" below). Do all of this before considering backend or frontend work done.

**Backend** (`unraid-api-plugin-incus/`):
```bash
cd unraid-api-plugin-incus
npx tsc --noEmit   # typecheck
npx tsc            # build → dist/
```
`node_modules` here is mostly symlinks into a sibling clone of the real `unraid-api` monorepo's pnpm store (`../upstream/unraid-api/node_modules/.pnpm/...`), which is how this package gets real `@nestjs/*`, `@unraid/shared`, `class-validator`, etc. to typecheck against without vendoring them. If a typecheck fails with a missing module, the fix is usually symlinking the missing package from that pnpm store, not `npm install`. If that sibling clone isn't available (e.g. CI, or a fresh machine), `npm install --no-save` the real published `@nestjs/common`/`@nestjs/config`/`@nestjs/graphql`/`class-transformer`/`class-validator` packages plus the local `@unraid/shared@file:.ci-stubs/unraid-shared` stub instead — see `.github/workflows/api-plugin-ci.yml`, which does exactly this. It's a best-effort proxy for whatever version the real host actually runs, not a guarantee of an identical typecheck.

**Frontend** (`unraid-api-plugin-incus/web/`):
```bash
cd unraid-api-plugin-incus/web
npx vue-tsc --noEmit   # typecheck
npm run build           # builds BOTH bundles (chains build:settings + build:dashboard):
                        #   ../dist-web/incus-settings.{js,css}     (full settings app)
                        #   ../dist-web-dashboard/incus-dashboard.js (small Main/Dashboard widget)
```
This builds a single-file Vue 3 custom element (`<incus-settings-app>`) — no code-splitting, everything inlined. It inherits Unraid's own CSS variables (`--primary` etc., driven by the host page's light/dark mode) rather than shipping its own palette; don't introduce a separate color system.

## CI

`.github/workflows/api-plugin-ci.yml` typechecks and builds the `unraid-api-plugin-incus` backend and `web/` frontend on every push/PR touching that directory (peerDependencies are installed from real published npm packages for the typecheck, plus a local `.ci-stubs/unraid-shared` stand-in for `@unraid/shared` — the one peer with no public package, since it's Unraid's internal monorepo). It does **not** cover the classic `.txz` OS package — see below for why that one isn't currently scriptable.

## Deploying to a real box

Both the classic `.plg`/shell layer and the `unraid-api-plugin-incus` backend/frontend are deployed independently and by hand — CI only typechecks/builds the backend and frontend (see above), it doesn't deploy anything, and the `.txz` OS package isn't built by CI at all:

- **Classic `.plg` / OS package**: the `packages/incus-unraid-*.txz` is a plain tar of everything under `source/`, laid down at `/usr/local/incus/` on the target (private-prefixed — nothing pollutes system paths). `upgradepkg --install-new` silently no-ops if the package name/version/build string is unchanged, so every content change requires bumping the build number in the txz filename and `incus.plg`'s `md5`/`txz` entities. When repackaging, always start from the *previous* build's extracted contents and overlay only what changed — rebuilding from `source/` alone drops the actual `incusd`/`lxcfs` binaries and bundled libs that live under `/usr/local/incus/{bin,lib,libexec}` in the already-deployed package, which is a destructive mistake (verify `tar -tJf` file counts match before installing).
- **`unraid-api-plugin-incus` backend**: lives at `/usr/local/unraid-api/node_modules/unraid-api-plugin-incus/` on the target, as just `dist/` + `package.json` (its own `ws`/`graphql-subscriptions` deps are already hoisted there from a prior deploy). Sync `dist/`, then `unraid-api restart` (pm2-managed) to reload — check `/var/log/graphql-api.log` for `IncusPluginModule` init and no errors.
- **Frontend**: the built `dist-web/incus-settings.{js,css}` get copied into `source/usr/local/emhttp/plugins/incus/web/` before repackaging the OS `.txz` — it ships as part of the classic plugin, not the API plugin.

## Architecture notes that aren't obvious from reading one file

- **Incus REST API, not CLI.** All three services in `src/` (`incus.service.ts`, `incus-exec.service.ts`, `incus-image-builder.service.ts`'s image-store calls) talk to `$INCUS_DIR/unix.socket` directly via `node:http`. Async operations return a generic "Operation" envelope reused for every endpoint — the operation-type-specific payload is nested **two levels deep** (`response.metadata.metadata.<field>`, not `response.metadata.<field>`). Launching from a locally-built image needs `source: { type: "image", alias }` with **no** `protocol`/`server` fields; those fields are only for remote simplestreams references (`images:debian/trixie/cloud` etc.) and launching a local alias with them set makes Incus look for it on the public remote instead.
- **The GraphQL schema has two sources that must stay in sync.** Most types/resolvers are decorator-based (`@ObjectType`, `@Resolver`), but `index.ts` also hand-maintains a `graphqlSchemaExtension` SDL string for `extend type Query`/`Mutation` fields (and some object types). When adding a query/mutation, update both the resolver *and* this string, or the field won't resolve.
- **`class-validator` decorators are mandatory on every `@InputType` field.** `unraid-api`'s global `ValidationPipe` runs in whitelist mode — a GraphQL `@Field()` alone isn't enough; a field missing `@IsString()`/`@IsOptional()`/etc. gets silently stripped with a "property X should not exist" rejection at the whitelist layer, not a helpful type error.
- **The exec/terminal feature rides GraphQL subscriptions**, not a custom WebSocket gateway — `graph.module.ts` already wires `graphql-ws` on the same `/graphql` endpoint, and subscriptions go through the same `AuthenticationGuard` a custom gateway wouldn't at handshake time.
- **Package/tool imports are all client-side, best-effort translators**, not new backend surface: devcontainer.json, mise.toml, and `.tool-versions` import (in `web/src/App.vue`) parse the file, map what has a confident mapping onto the existing distro/package/post-install-command fields, and explicitly report what they couldn't map rather than guessing or dropping it silently. `mise.toml`/`.tool-versions` tool pins aren't OS packages — they're realized by baking `mise` itself into the image via its official installer as a post-install action, installed system-wide (not under the build's root user's home) so the container's actual runtime user can use it.
- **`incus-init.sh` and `rc.incus` must redirect stdin from `/dev/null`** on every bare `incus` CLI invocation — several subcommands (confirmed: `profile create`) hang forever waiting on stdin otherwise, even in a non-interactive script context.
- **`incusd` needs `nft` and `unsquashfs` on `PATH`, bundled or the ACL/build steps hang** (not fail — hang indefinitely) rather than erroring. `incus-preflight.sh` checks for these; if it's green but something still hangs, suspect a missing bundled binary a preflight check doesn't yet cover.
- **Terminology**: user-facing copy says "dev containers" / "container", not "jail" — but internal identifiers (GraphQL `Jail` type, `JailAction` enum, `jailBridge`/`JAIL_*` config keys, `launchJail`/`deleteJail` mutations) intentionally still say "jail" throughout the codebase. This is a deliberate scope decision — don't rename the internals to match the UI copy.
