# incus-unraid — Quickstart

**incus-unraid** is a plugin for Unraid that runs coding agents and stdio MCP servers inside LAN-banned Incus system-container "jails". Each jail gets a dedicated NAT bridge firewalled off from your LAN while keeping Internet access — so an agent, or a compromised dependency in its toolchain, can't reach your NAS, routers, or internal services.

## What this project does

This repository contains a complete Unraid plugin that:

1. **Installs and manages Incus** — a container runtime (like LXD) repackaged from Debian 7.0.0-5 LTS
2. **Creates isolated jails** — each jail is a system container with its own network namespace
3. **Firewalls jails from the LAN** — using managed network ACLs to block all local network access while allowing Internet
4. **Provides a GraphQL API** — for managing jails (launch/list/stop/delete, repoint workspace) via Unraid's new API system

The plugin is modeled on the pattern from [weisser-zwerg.dev's Incus Codex Jail](https://weisser-zwerg.dev/posts/incus-codex-jail/), adapted for Unraid's plugin system and RAM-booted Slackware environment.

## Repository structure

```
incus-unraid/
├── incus.plg                           # Unraid plugin manifest
├── packages/incus-unraid-*.txz         # Repackaged Incus runtime (private prefix)
├── source/usr/local/emhttp/plugins/incus/
│   ├── incus.cfg                       # Canonical config (shell variable format)
│   ├── scripts/
│   │   ├── rc.incus                    # Service control (start/stop/status)
│   │   ├── incus-init.sh               # Idempotent jail environment setup
│   │   ├── incus-preflight.sh          # Host capability check (read-only)
│   │   └── incus-env.sh                # Library path scoping
│   ├── event/
│   │   ├── disks_mounted               # Array-start hook (start daemon + init)
│   │   └── unmounting_disks            # Array-stop hook (graceful shutdown)
│   └── templates/
│       └── agent-jail-profile.yaml.tmpl  # Jail profile (cloud-init, limits)
└── unraid-api-plugin-incus/            # NestJS/GraphQL API plugin
    ├── index.ts                        # Plugin entrypoint
    ├── src/
    │   ├── incus.service.ts            # Incus REST API client (unix socket)
    │   ├── incus.resolver.ts           # GraphQL resolvers (jail operations)
    │   ├── config-sync.service.ts      # bidirectional config sync
    │   └── config.entity.ts            # TypeScript config types
    └── package.json
```

## Key concepts

### The three pieces

1. **`incus.plg` + `source/`** — Classic Unraid plugin. Lays down the repackaged Incus runtime (`packages/*.txz`), the daemon lifecycle (`rc.incus`), and array up/down hooks. Does the OS-level work the API plugin can't: ship the daemon, run it, persist its state.

2. **`incus-init.sh` (config-driven preseed)** — On every array start, reads `incus.cfg` and idempotently ensures: the ZFS/dir storage pool, the `agent-block-lan` ACL, the `agentbr0` bridge, and the `agent-jail` profile. Re-running is safe (check-then-create). **All policy lives in `incus.cfg`** — nothing is hardcoded.

3. **`unraid-api-plugin-incus/`** — NestJS/GraphQL plugin for Unraid's new API system. Manages jails at runtime (launch/list/stop/delete, repoint workspace) by speaking the **Incus REST API over its unix socket** — no CLI scraping.

### Configuration is the source of truth

`/boot/config/plugins/incus/incus.cfg` (shell variable format) is the single source of truth for both the shell init and the API plugin. The shell init sources it directly, while the API plugin watches and syncs it bidirectionally with `incus.json`.

Key configuration defaults:

| Key | Default | Notes |
|---|---|---|
| `SERVICE` | `disabled` | Set to `enabled` to autostart on array start |
| `STORAGE_DRIVER` / `STORAGE_SOURCE` | `zfs` / `nvme/incus` | Dedicated ZFS dataset; created if missing |
| `JAIL_BRIDGE` / `JAIL_SUBNET` | `agentbr0` / `198.18.0.1/15` | RFC 2544 range, won't collide with home LAN |
| `ACL_BLOCK` | `10/8,172.16/12,192.168/16,169.254/16` | LAN ban. **Tailscale `100.64/10` NOT blocked** |
| `ACL_ALLOW` | *(empty)* | Allow-holes punched before the block list |
| `JAIL_IMAGE` | `images:debian/trixie/cloud` | Must be a `/cloud` variant for cloud-init |
| `JAIL_NESTING` | `false` | `true` = nested docker/incus inside the jail |
| `JAIL_CPU` / `JAIL_MEMORY` | `2` / `4GiB` | Empty = no cap |

### Safety model

- **No system-lib pollution** — Incus runs from `/usr/local/incus/` with a scoped `LD_LIBRARY_PATH`; nothing else on the box sees its libraries.
- **Preflight gate** — Won't start if the host can't run it; changes nothing on failure.
- **RAM-boot escape hatch** — Unraid rebuilds `/usr` from flash on every boot; a bad state is cleared by reboot.
- **Pure userspace** — Zero kernel modules shipped; relies on the running kernel's userns/cgroup2/veth/netfilter.

## How to use this documentation

### For new contributors

1. Start here — read this quickstart to understand what the project is
2. Review `/README.md` — detailed architecture, install instructions, and examples
3. Browse the relevant section:
   - Plugin development and installation: see `/README.md`
   - API plugin structure: see `unraid-api-plugin-incus/` source files

### For operations

- Install instructions: See `/README.md` → "Install" section
- Configuration reference: See `source/usr/local/emhttp/plugins/incus/incus.cfg`
- Runtime management: See `/README.md` → "Launch a Jail" section

### For debugging

- Plugin lifecycle: `source/usr/local/emhttp/plugins/incus/scripts/rc.incus`
- Init process: `source/usr/local/emhttp/plugins/incus/scripts/incus-init.sh`
- Preflight checks: `source/usr/local/emhttp/plugins/incus/scripts/incus-preflight.sh`
- API client: `unraid-api-plugin-incus/src/incus.service.ts`

## Development and testing

The repository includes:

- **Repackaged Incus runtime** — `packages/incus-unraid-7.0.0-5-x86_64-1.txz` (Debian trixie, 7.0.0-5 LTS)
- **Shell scripts** — `source/usr/local/emhttp/plugins/incus/scripts/` (init, preflight, service control)
- **TypeScript API plugin** — `unraid-api-plugin-incus/` (builds to `dist/`)

No automated tests are present in the repository. Testing is manual via Unraid installation and jail operations.

## Related files

- `/README.md` — Comprehensive user and developer documentation
- `/MANIFEST.md` — Repackaging details and library closure
- `/LICENSE` — MIT license
- `/.github/workflows/openwiki-update.yml` — Scheduled OpenWiki documentation updates

## Getting started

1. **Review the architecture** — Read `/README.md` for the full system diagram and component breakdown
2. **Understand the configuration** — Examine `source/usr/local/emhttp/plugins/incus/incus.cfg` for all tunable parameters
3. **Trace the lifecycle** — Follow `source/usr/local/emhttp/plugins/incus/event/disks_mounted` → `rc.incus` → `incus-init.sh`
4. **Explore the API** — Review `unraid-api-plugin-incus/src/incus.service.ts` for how the REST API client works
