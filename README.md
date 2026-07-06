# incus-unraid — LAN-Banned Agent Jails for Unraid

Run coding agents and stdio MCP servers inside Incus system-container "jails" on
Unraid. Each jail gets a dedicated NAT bridge that is **firewalled off from your
LAN** (egress deny-list) while keeping **Internet access** — so an agent, or a
compromised dependency in its toolchain, can't reach your NAS, routers, or
internal services.

Modeled on the pattern from [weisser-zwerg.dev's Incus Codex Jail](https://weisser-zwerg.dev/posts/incus-codex-jail/), adapted for Unraid's plugin system and RAM-booted Slackware environment.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                     Unraid Host                      │
│                                                      │
│  incus.plg ─── installs ──→ /usr/local/incus/        │
│       │                     (binaries + bundled libs) │
│       │                                              │
│       ├── rc.incus ─────→ start/stop incusd          │
│       │                                              │
│       ├── incus-init.sh ─→ storage pool              │
│       │                    agent-block-lan ACL        │
│       │                    agentbr0 bridge            │
│       │                    agent-jail profile         │
│       │                                              │
│  unraid-api-plugin-incus                             │
│       └── NestJS module ──→ Incus REST API           │
│                             (unix socket, no CLI)    │
│                                                      │
│  ┌─── agentbr0 (198.18.0.0/15) ───┐                │
│  │  agent1   agent2   agent3  ...  │                │
│  │  ✓ Internet  ✗ LAN  ✗ NAS      │                │
│  └─────────────────────────────────┘                │
└──────────────────────────────────────────────────────┘
```

## The Three Pieces

1. **`incus.plg` + `source/`** — Classic Unraid plugin. Lays down the
   repackaged Incus runtime (`packages/*.txz`), the daemon lifecycle
   (`rc.incus`), and array up/down hooks. Does the OS-level work the API plugin
   can't: ship the daemon, run it, persist its state.

2. **`incus-init.sh` (config-driven preseed)** — On every array start, reads
   `incus.cfg` and idempotently ensures: the ZFS/dir storage pool, the
   `agent-block-lan` ACL, the `agentbr0` bridge, and the `agent-jail` profile.
   Re-running is safe (check-then-create). **All policy lives in `incus.cfg`** —
   nothing is hardcoded.

3. **`unraid-api-plugin-incus/`** — NestJS/GraphQL plugin for Unraid's new API
   system. Manages jails at runtime (launch/list/stop/delete, repoint workspace)
   by speaking the **Incus REST API over its unix socket** — no CLI scraping.

## Configuration (`/boot/config/plugins/incus/incus.cfg`)

Single source of truth for both the shell init and the API plugin. Key defaults:

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

## Install

1. Place `packages/incus-unraid-7.0.0-5-x86_64-1.txz` at the `gitURL` location.
2. Install the `.plg` (Community Apps or direct plugin URL).
3. Edit `/boot/config/plugins/incus/incus.cfg`: set `SERVICE=enabled`, adjust
   `STORAGE_SOURCE` to your actual ZFS pool/dataset.
4. Start the array (or manually: `/etc/rc.d/rc.incus start && /usr/local/emhttp/plugins/incus/scripts/incus-init.sh`).
5. Preflight gates the daemon — check `/var/log/incusd.log` if it refuses.

## Launch a Jail

```bash
# CLI (uses the private-prefixed incus binary)
/usr/local/incus/bin/incus launch images:debian/trixie/cloud agent1 \
  --profile default --profile agent-jail

# Verify the LAN ban
incus exec agent1 -- nc -vz -w2 1.1.1.1 443        # ✓ Internet
incus exec agent1 -- nc -vz -w2 192.168.1.1 22     # ✗ BLOCKED
```

Or via GraphQL once the API plugin is loaded:
```graphql
mutation { launchJail(name: "agent1") }
```

## Safety Model

- **No system-lib pollution** — Incus runs from `/usr/local/incus/` with a
  scoped `LD_LIBRARY_PATH`; nothing else on the box sees its libraries.
- **Preflight gate** — Won't start if the host can't run it; changes nothing on failure.
- **RAM-boot escape hatch** — Reboot restores a pristine OS; only `INCUS_DIR`
  (on the array) persists.
- **Jail egress is deny-listed** via Incus network ACLs (nftables under the hood).

## Repository Structure

```
incus-unraid/
├── incus.plg                         # Unraid plugin manifest (XML)
├── packages/
│   └── incus-unraid-*.txz            # Repackaged Incus binaries
├── source/usr/local/emhttp/plugins/incus/
│   ├── scripts/
│   │   ├── rc.incus                  # Daemon lifecycle
│   │   ├── incus-env.sh              # LD_LIBRARY_PATH scoping
│   │   ├── incus-preflight.sh        # Host capability check
│   │   └── incus-init.sh             # Config-driven preseed
│   ├── event/
│   │   ├── disks_mounted             # Array-start hook
│   │   └── unmounting_disks          # Array-stop hook
│   ├── templates/
│   │   └── agent-jail-profile.yaml.tmpl
│   └── incus.cfg                     # Default config
└── unraid-api-plugin-incus/          # NestJS/GraphQL API plugin
    ├── index.ts                      # Plugin entry point
    ├── src/
    │   ├── incus.service.ts           # Incus REST API client
    │   ├── incus.resolver.ts          # GraphQL resolvers
    │   └── config.entity.ts           # Config entity
    ├── package.json
    └── tsconfig.json
```

## License

MIT — see [LICENSE](./LICENSE).

Not affiliated with the LinuxContainers/Incus project or Unraid.
