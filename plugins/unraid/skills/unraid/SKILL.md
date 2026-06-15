---
name: unraid
description: >
  Query and monitor an Unraid NAS/homelab server — array health, disk temperatures,
  Docker containers, virtual machines, system metrics, notifications, alerts, shares,
  UPS status, log files, network, plugins, parity history, registration, rclone
  backups, remote access, and Unraid Connect. Use this skill whenever the user asks
  about their Unraid server, array state, disk health, SMART status, parity check,
  Docker containers running on Unraid, Unraid VMs, Unraid memory or CPU usage,
  Unraid notifications or alerts, Unraid shares, UPS battery on Unraid, Unraid logs,
  or anything related to an Unraid system. Always invoke this skill when the user
  mentions "unraid", "array", "parity", "Unraid docker", "Unraid metrics", or asks
  about NAS health on an Unraid box — even if they don't use the word "skill".
---

# Unraid Server Skill

Read-only access to an Unraid NAS server. Three access tiers in priority order:
1. **MCP tool** `unraid` (preferred when available)
2. **CLI binary** `unraid` (fallback)
3. **Direct GraphQL curl** (last resort)

All 24 data actions are read-only — nothing modifies the server.

---

## Tier 1 — MCP Tool (preferred)

The MCP server exposes a single tool named `unraid` that accepts an `action` parameter.

```
unraid(action="<action>")
```

### All actions

| Action | What it returns | Required params | Optional params |
|--------|----------------|-----------------|-----------------|
| `array` | Array state, capacity (TB), parity status, data disks, cache pools | — | — |
| `disks` | All physical disks: SMART status, temp, size, interface, partitions | — | — |
| `docker` | All containers: name, state, status, ports, update availability | — | — |
| `docker_logs` | Container log lines | `id` (container ID) | `tail` (default 100) |
| `vms` | Virtual machines and their state | — | — |
| `server` | Server name, LAN/WAN IP, local/remote URL, GUID, online status | — | — |
| `info` | OS, CPU (brand/cores/threads/speed), memory layout, Unraid + kernel versions | — | — |
| `shares` | User shares: name, size/used/free (KB), cache setting, allocator | — | — |
| `notifications` | Unread counts by severity + active warnings and alerts with detail | — | — |
| `log_files` | List of available log files with path, size, modified date | — | — |
| `log_file` | Contents of one log file | `path` | `lines`, `start_line` |
| `services` | System services: name, online status, version, uptime | — | — |
| `network` | Network access URLs: type, name, IPv4, IPv6 | — | — |
| `ups` | UPS devices: battery %, runtime estimate, health, input/output voltage, load | — | — |
| `ups_config` | UPS monitoring config: service, cable, type, device, shutdown thresholds | — | — |
| `metrics` | Live CPU %, per-core %, memory used/total/swap, temperature sensors | — | — |
| `plugins` | Installed community plugins with name and version | — | — |
| `parity_history` | All past parity check results: date, duration, speed, errors | — | — |
| `vars` | System config variables: timezone, model, protocol enables, reg state | — | — |
| `registration` | License type, state, expiration date | — | — |
| `flash` | USB flash drive vendor and product (guid omitted — null at runtime) | — | — |
| `rclone` | Rclone backup remotes (name, type) and drives | — | — |
| `remote_access` | WAN access type, port forwarding config | — | — |
| `connect` | Unraid Connect dynamic remote access: enabled/running type, settings | — | — |
| `help` | Built-in tool documentation (no auth required) | — | — |

### Common queries

```
# Array health + disk status
unraid(action="array")

# Live CPU/memory/temperature dashboard
unraid(action="metrics")

# All Docker containers
unraid(action="docker")

# Logs for a specific container (get id from docker action first)
unraid(action="docker_logs", id="abc123def456", tail=50)

# Active warnings/alerts
unraid(action="notifications")

# Physical disk SMART status and temperatures
unraid(action="disks")

# Unraid shares with sizes
unraid(action="shares")

# UPS battery and power
unraid(action="ups")

# List log files, then read one
unraid(action="log_files")
unraid(action="log_file", path="/var/log/syslog", lines=100)

# System info (OS, CPU, memory layout, versions)
unraid(action="info")

# Parity check history
unraid(action="parity_history")
```

---

## Tier 2 — CLI Binary

Binary: `/home/jmagar/workspace/unrust/target/release/runraid`

All commands accept `--json` for machine-readable output.

```bash
UNRAID_BIN=/home/jmagar/workspace/unrust/target/release/runraid

# Core queries
$UNRAID_BIN array
$UNRAID_BIN disks
$UNRAID_BIN docker
$UNRAID_BIN docker logs <container_id> [--tail N]
$UNRAID_BIN vms
$UNRAID_BIN server
$UNRAID_BIN info
$UNRAID_BIN shares
$UNRAID_BIN notifications
$UNRAID_BIN metrics

# Logs
$UNRAID_BIN log-files              # or: log files
$UNRAID_BIN log <path> [--lines N] [--start-line N]
$UNRAID_BIN log-file <path>        # alias

# System
$UNRAID_BIN services
$UNRAID_BIN network
$UNRAID_BIN vars
$UNRAID_BIN registration
$UNRAID_BIN flash
$UNRAID_BIN plugins

# UPS
$UNRAID_BIN ups
$UNRAID_BIN ups-config             # or: ups config

# Storage / backup
$UNRAID_BIN parity-history         # or: parity history
$UNRAID_BIN rclone

# Remote access
$UNRAID_BIN remote-access          # or: remote access
$UNRAID_BIN connect

# JSON output (any command)
$UNRAID_BIN metrics --json
$UNRAID_BIN array --json
```

The CLI requires `UNRAID_API_URL` and `UNRAID_API_KEY` environment variables to be set.

---

## Tier 3 — Direct GraphQL curl

Use when both MCP and CLI are unavailable.

```bash
# Auth: x-api-key header; endpoint from UNRAID_API_URL env var
curl -s -X POST "$UNRAID_API_URL" \
  -H "x-api-key: $UNRAID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"query { server { id name status lanip wanip localurl remoteurl } }"}'

# Array state
curl -s -X POST "$UNRAID_API_URL" \
  -H "x-api-key: $UNRAID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"query { array { state capacity { kilobytes { free used total } } parities { id name status temp } disks { id name status temp numErrors } caches { id name status } } }"}'

# Docker containers
curl -s -X POST "$UNRAID_API_URL" \
  -H "x-api-key: $UNRAID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"query { docker { containers { id names image state status autoStart isUpdateAvailable webUiUrl } } }"}'

# Live metrics
curl -s -X POST "$UNRAID_API_URL" \
  -H "x-api-key: $UNRAID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"query { metrics { cpu { percentTotal } memory { total used available percentTotal } temperature { summary { average warningCount criticalCount } } } }"}'

# Notifications / alerts
curl -s -X POST "$UNRAID_API_URL" \
  -H "x-api-key: $UNRAID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"query { notifications { overview { unread { warning alert info total } } warningsAndAlerts { id title subject description importance timestamp } } }"}'

# Physical disks (SMART)
curl -s -X POST "$UNRAID_API_URL" \
  -H "x-api-key: $UNRAID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"query { disks { id device type name vendor size serialNum interfaceType smartStatus temperature isSpinning partitions { name fsType size } } }"}'
```

---

## Important gotchas

### BigInt fields arrive as JSON strings
Memory sizes in `metrics` (total, used, free, swapTotal, swapUsed, swapFree, available) come
back as quoted strings like `"34359738368"`, not JSON numbers. Parse with `parseInt()` / `int()`
before doing arithmetic.

### Temperature unit is a GraphQL enum
The `metrics.temperature.sensors[].current.unit` field is `CELSIUS`, `FAHRENHEIT`, or `KELVIN`
— an enum string, not a symbol. Map it yourself: `FAHRENHEIT → F`, `KELVIN → K`, `CELSIUS → C`.

### `flash.guid` can be null at runtime
The Unraid GraphQL schema declares `guid` as non-nullable, but it returns null on real servers.
The `flash` action intentionally omits `guid` from the query to avoid a GraphQL error.

### Container IDs for `docker_logs`
Use `action="docker"` first to get container IDs, then pass one to `docker_logs`. The `id` must
be the container's Docker ID (e.g., `"abc123def456"`), not its name.

### Log file paths for `log_file`
Use `action="log_files"` first to discover available paths, then pass a `path` to `log_file`.
The path must be exact (e.g., `/var/log/syslog`).

### Auth modes
- MCP server running on loopback (`127.x.x.x`) automatically uses no-auth mode.
- HTTP mode requires either a bearer token (`UNRAID_MCP_TOKEN`) or OAuth.
- Required scope for all data actions: `unraid:read` (or `unraid:admin` which satisfies it).
- `help` action has no scope requirement.

---

## Workflow patterns

### Check server health at a glance
```
1. unraid(action="server")        — identity and connectivity
2. unraid(action="array")         — array state and disk errors
3. unraid(action="notifications") — active alerts
4. unraid(action="metrics")       — CPU/memory/temp
```

### Investigate a disk issue
```
1. unraid(action="array")   — which disk has errors or bad status
2. unraid(action="disks")   — SMART status and temperature for that disk
```

### Debug a Docker container
```
1. unraid(action="docker")              — find container ID and current state
2. unraid(action="docker_logs", id="<container_id>", tail=200)
```

### Check UPS health
```
1. unraid(action="ups")        — battery %, runtime estimate, load
2. unraid(action="ups_config") — shutdown thresholds
```

### Audit system configuration
```
1. unraid(action="vars")         — protocol enables, config validity, reg state
2. unraid(action="registration") — license type and expiry
3. unraid(action="plugins")      — installed community plugins
```
