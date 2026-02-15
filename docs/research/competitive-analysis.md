# Competitive Analysis: Unraid Integration Projects

> **Date:** 2026-02-07
> **Purpose:** Identify features and capabilities that competing Unraid integration projects offer that our `unraid-mcp` server (10 tools, 90 actions, GraphQL-based) currently lacks.

## Table of Contents

- [Executive Summary](#executive-summary)
- [Project Profiles](#project-profiles)
  - [1. unraid-management-agent (Go plugin)](#1-unraid-management-agent)
  - [2. domalab/unraid-api-client (Python library)](#2-domalabunraid-api-client)
  - [3. mcp-ssh-sre / unraid-ssh-mcp (SSH-based MCP)](#3-mcp-ssh-sre--unraid-ssh-mcp)
  - [4. PSUnraid (PowerShell module)](#4-psunraid)
  - [5. ha-unraid (Home Assistant integration)](#5-ha-unraid)
  - [6. chris-mc1/unraid_api (HA integration)](#6-chris-mc1unraid_api)
- [Feature Matrix](#feature-matrix)
- [Gap Analysis](#gap-analysis)
- [Recommended Priorities](#recommended-priorities)
- [Sources](#sources)

---

## Executive Summary

Our `unraid-mcp` server provides 10 MCP tools (90 actions) built on the official Unraid GraphQL API. After analyzing six competing projects, we identified several significant gaps:

**Critical gaps (high-value features we lack):**
1. **Array control operations** (start/stop array, parity check control, disk spin up/down)
2. **UPS monitoring** (battery level, load, runtime, power status)
3. **GPU metrics** (utilization, temperature, memory, power draw)
4. **SMART disk health data** (per-disk SMART status, errors, power-on hours)
5. **Parity check history** (dates, durations, error counts)
6. **System reboot/shutdown** commands
7. **Services status** (running system services)
8. **Flash drive info** (boot device monitoring)
9. **Plugins list** (installed plugins)

**Moderate gaps (nice-to-have features):**
10. **Docker container resource metrics** (CPU %, memory usage per container)
11. **Docker container pause/unpause** operations
12. **ZFS pool/dataset/snapshot management**
13. **User script execution** (User Scripts plugin integration)
14. **Network bandwidth monitoring** (per-interface stats)
15. **Prometheus metrics endpoint**
16. **MQTT event publishing**
17. **WebSocket real-time streaming** (not just subscription diagnostics)
18. **MCP Resources** (subscribable data streams)
19. **MCP Prompts** (guided interaction templates)
20. **Unassigned devices** monitoring

**Architectural gaps:**
21. No confirmation/safety mechanism for destructive operations
22. No Pydantic response models (type-safe responses)
23. No Docker network listing
24. No container update capability
25. No owner/cloud/remote-access info queries

---

## Project Profiles

### 1. unraid-management-agent

- **Repository:** [ruaan-deysel/unraid-management-agent](https://github.com/ruaan-deysel/unraid-management-agent)
- **Language:** Go
- **Architecture:** Unraid plugin with REST API + WebSocket + MCP + Prometheus + MQTT
- **API Type:** REST (59 endpoints) + WebSocket (9 event types) + MCP (54 tools)
- **Data Collection:** Native Go libraries (Docker SDK, libvirt, /proc, /sys) -- does NOT depend on the GraphQL API
- **Stars/Activity:** Active development, comprehensive documentation

**Key differentiators from our project:**
- Runs as an Unraid plugin directly on the server (no external dependency on GraphQL API)
- Collects data directly from /proc, /sys, Docker SDK, and libvirt
- 59 REST endpoints vs our 10 MCP tools (90 actions)
- 54 MCP tools with Resources and Prompts
- Real-time WebSocket event streaming (9 event types, 5-60s intervals)
- 41 Prometheus metrics for Grafana dashboards
- MQTT publishing for Home Assistant/IoT integration
- Confirmation-required destructive operations (`confirm: true` parameter)
- Collector management (enable/disable collectors, adjust intervals)
- System reboot and shutdown commands

**Unique capabilities not available via GraphQL API:**
- GPU metrics (utilization, temperature, memory, power draw via nvidia-smi)
- UPS metrics via NUT (Network UPS Tools) direct integration
- Fan RPM readings from /sys
- Motherboard temperature from /sys
- SMART disk data (power-on hours, power cycles, read/write bytes, I/O utilization)
- Network interface bandwidth (rx/tx bytes, real-time)
- Docker container resource usage (CPU %, memory bytes, network I/O)
- Unassigned devices monitoring
- ZFS pools, datasets, snapshots, ARC stats
- Parity check scheduling
- Mover settings
- Disk thresholds/settings
- Service management
- Plugin and update management
- Flash drive info
- Network access URLs (LAN, WAN, mDNS, IPv6)
- User script execution
- Share configuration modification (POST endpoints)
- System settings modification

**MCP-specific features we lack:**
- MCP Resources (subscribable real-time data: `unraid://system`, `unraid://array`, `unraid://containers`, `unraid://vms`, `unraid://disks`)
- MCP Prompts (`analyze_disk_health`, `system_overview`, `troubleshoot_issue`)
- Dual MCP transport (HTTP + SSE)
- Confirmation-gated destructive operations

**REST Endpoints (59 total):**

| Category | Endpoints |
|----------|-----------|
| System & Health | `GET /health`, `GET /system`, `POST /system/reboot`, `POST /system/shutdown` |
| Array | `GET /array`, `POST /array/start`, `POST /array/stop` |
| Parity | `POST /parity-check/start\|stop\|pause\|resume`, `GET /parity-check/history`, `GET /parity-check/schedule` |
| Disks | `GET /disks`, `GET /disks/{id}` |
| Shares | `GET /shares`, `GET /shares/{name}/config`, `POST /shares/{name}/config` |
| Docker | `GET /docker`, `GET /docker/{id}`, `POST /docker/{id}/start\|stop\|restart\|pause\|unpause` |
| VMs | `GET /vm`, `GET /vm/{id}`, `POST /vm/{id}/start\|stop\|restart\|pause\|resume\|hibernate\|force-stop` |
| UPS | `GET /ups` |
| GPU | `GET /gpu` |
| Network | `GET /network`, `GET /network/access-urls`, `GET /network/{interface}/config` |
| Collectors | `GET /collectors/status`, `GET /collectors/{name}`, `POST /collectors/{name}/enable\|disable`, `PATCH /collectors/{name}/interval` |
| Logs | `GET /logs`, `GET /logs/{filename}` |
| Settings | `GET /settings/system\|docker\|vm\|disks\|disk-thresholds\|mover\|services\|network-services`, `POST /settings/system` |
| Plugins | `GET /plugins`, `GET /updates` |
| Flash | `GET /system/flash` |
| Prometheus | `GET /metrics` |
| WebSocket | `WS /ws` |

---

### 2. domalab/unraid-api-client

- **Repository:** [domalab/unraid-api-client](https://github.com/domalab/unraid-api-client)
- **Language:** Python (async, aiohttp)
- **Architecture:** Client library for the official Unraid GraphQL API
- **API Type:** GraphQL client (same API we use)
- **PyPI Package:** `unraid-api` (installable via pip)

**Key differentiators from our project:**
- Pure client library (not an MCP server), but shows what the GraphQL API can do
- Full Pydantic model coverage for all responses (type-safe)
- SSL auto-discovery (handles Unraid's "No", "Yes", "Strict" SSL modes)
- Redirect handling for myunraid.net remote access
- Session injection for Home Assistant integration
- Comprehensive exception hierarchy

**Methods we should consider adding MCP tools for:**

| Method | Our Coverage | Notes |
|--------|-------------|-------|
| `test_connection()` | Missing | Connection validation |
| `get_version()` | Missing | API and OS version info |
| `get_server_info()` | Partial | For device registration |
| `get_system_metrics()` | Missing | CPU, memory, temperature, power, uptime as typed model |
| `typed_get_array()` | Have `get_array_status()` | They have richer Pydantic model |
| `typed_get_containers()` | Have `list_docker_containers()` | They have typed models |
| `typed_get_vms()` | Have `list_vms()` | They have typed models |
| `typed_get_ups_devices()` | **Missing** | UPS battery, power, runtime |
| `typed_get_shares()` | Have `get_shares_info()` | Similar |
| `get_notification_overview()` | Have it | Same |
| `start/stop_container()` | Have `manage_docker_container()` | Same |
| `pause/unpause_container()` | **Missing** | Docker pause/unpause |
| `update_container()` | **Missing** | Container image update |
| `remove_container()` | **Missing** | Container removal |
| `start/stop_vm()` | Have `manage_vm()` | Same |
| `pause/resume_vm()` | **Missing** | VM pause/resume |
| `force_stop_vm()` | **Missing** | Force stop VM |
| `reboot_vm()` | **Missing** | VM reboot |
| `start/stop_array()` | **Missing** | Array start/stop control |
| `start/pause/resume/cancel_parity_check()` | **Missing** | Full parity control |
| `spin_up/down_disk()` | **Missing** | Disk spin control |
| `get_parity_history()` | **Missing** | Historical parity data |
| `typed_get_vars()` | Have `get_unraid_variables()` | Same |
| `typed_get_registration()` | Have `get_registration_info()` | Same |
| `typed_get_services()` | **Missing** | System services list |
| `typed_get_flash()` | **Missing** | Flash drive info |
| `typed_get_owner()` | **Missing** | Server owner info |
| `typed_get_plugins()` | **Missing** | Installed plugins |
| `typed_get_docker_networks()` | **Missing** | Docker network list |
| `typed_get_log_files()` | Have `list_available_log_files()` | Same |
| `typed_get_cloud()` | **Missing** | Unraid Connect cloud status |
| `typed_get_connect()` | Have `get_connect_settings()` | Same |
| `typed_get_remote_access()` | **Missing** | Remote access settings |
| `get_physical_disks()` | Have `list_physical_disks()` | Same |
| `get_array_disks()` | **Missing** | Array disk assignments |

---

### 3. mcp-ssh-sre / unraid-ssh-mcp

- **Repository:** [ohare93/mcp-ssh-sre](https://github.com/ohare93/mcp-ssh-sre)
- **Language:** TypeScript/Node.js
- **Architecture:** MCP server that connects via SSH to run predefined commands
- **API Type:** SSH command execution (read-only by design)
- **Tools:** 12 tool modules with 79+ actions

**Why SSH instead of GraphQL API:**
The project's documentation explicitly compares SSH vs API capabilities:

| Feature | GraphQL API | SSH |
|---------|------------|-----|
| Docker container logs | Limited | Full |
| SMART disk health data | Limited | Full (smartctl) |
| Real-time CPU/load averages | Polling | Direct |
| Network bandwidth monitoring | Limited | Full (iftop, nethogs) |
| Process monitoring (ps/top) | Not available | Full |
| Log file analysis | Basic | Full (grep, awk) |
| Security auditing | Not available | Full |

**Tool modules and actions:**

| Module | Tool Name | Actions |
|--------|-----------|---------|
| Docker | `docker` | list_containers, inspect, logs, stats, port, env, top, health, logs_aggregate, list_networks, inspect_network, list_volumes, inspect_volume, network_containers |
| System | `system` | list_files, read_file, find_files, disk_usage, system_info |
| Monitoring | `monitoring` | ps, process_tree, top, iostat, network_connections |
| Security | `security` | open_ports, audit_privileges, ssh_connections, cert_expiry |
| Log Analysis | `log` | grep_all, error_aggregator, timeline, parse_docker, compare_timerange, restart_history |
| Resources | `resource` | dangling, hogs, disk_analyzer, docker_df, zombies, io_profile |
| Performance | `performance` | bottleneck, bandwidth, track_metric |
| VMs | `vm` | list, info, vnc, logs |
| Container Topology | `container_topology` | network_topology, volume_sharing, dependency_graph, port_conflicts, network_test |
| Health Diagnostics | `health` | comprehensive, common_issues, threshold_alerts, compare_baseline, diagnostic_report, snapshot |
| **Unraid Array** | `unraid` | array_status, smart, temps, shares, share_usage, parity_status, parity_history, sync_status, spin_status, unclean_check, mover_status, mover_log, cache_usage, split_level |
| **Unraid Plugins** | `plugin` | list, updates, template, scripts, share_config, disk_assignments, recent_changes |

**Unique capabilities we lack entirely:**
- Container log retrieval and aggregation
- Container environment variable inspection
- Container topology analysis (network maps, shared volumes, dependency graphs, port conflicts)
- Process monitoring (ps, top, process trees)
- Disk I/O monitoring (iostat)
- Network connection analysis (ss/netstat)
- Security auditing (open ports, privilege audit, SSH connection logs, SSL cert expiry)
- Performance bottleneck analysis
- Resource waste detection (dangling Docker resources, zombie processes)
- Comprehensive health diagnostics with baseline comparison
- Mover status and logs
- Cache usage analysis
- Split level configuration
- User script discovery
- Docker template inspection
- Disk assignment information
- Recent config file change detection

---

### 4. PSUnraid

- **Repository:** [jlabon2/PSUnraid](https://github.com/jlabon2/PSUnraid)
- **Language:** PowerShell
- **Architecture:** PowerShell module using GraphQL API
- **API Type:** GraphQL (same as ours)
- **Status:** Proof of concept, 30+ cmdlets

**Cmdlets and operations:**

| Category | Cmdlets |
|----------|---------|
| Connection | `Connect-Unraid`, `Disconnect-Unraid` |
| System | `Get-UnraidServer`, `Get-UnraidMetrics`, `Get-UnraidLog`, `Start-UnraidMonitor` |
| Docker | `Get-UnraidContainer`, `Start-UnraidContainer`, `Stop-UnraidContainer`, `Restart-UnraidContainer` |
| VMs | `Get-UnraidVm`, `Start-UnraidVm`, `Stop-UnraidVm`, `Suspend-UnraidVm`, `Resume-UnraidVm`, `Restart-UnraidVm` |
| Array | `Get-UnraidArray`, `Get-UnraidPhysicalDisk`, `Get-UnraidShare`, `Start-UnraidArray`, `Stop-UnraidArray` |
| Parity | `Start-UnraidParityCheck`, `Stop-UnraidParityCheck`, `Suspend-UnraidParityCheck`, `Resume-UnraidParityCheck`, `Get-UnraidParityHistory` |
| Notifications | `Get-UnraidNotification`, `Set-UnraidNotification`, `Remove-UnraidNotification` |
| Other | `Get-UnraidPlugin`, `Get-UnraidUps`, `Restart-UnraidApi` |

**Features we lack that PSUnraid has (via same GraphQL API):**
- Real-time monitoring dashboard (`Start-UnraidMonitor`)
- Notification management (mark as read, delete notifications)
- Array start/stop
- Parity check full lifecycle (start, stop, pause, resume, history)
- UPS monitoring
- Plugin listing
- API restart capability
- VM suspend/resume/restart

---

### 5. ha-unraid (Home Assistant)

- **Repository:** [domalab/ha-unraid](https://github.com/domalab/ha-unraid) (ruaan-deysel fork is active)
- **Language:** Python
- **Architecture:** Home Assistant custom integration
- **API Type:** Originally SSH-based (through v2025.06.11), rebuilt for GraphQL API (v2025.12.0+)
- **Requires:** Unraid 7.2.0+, GraphQL API v4.21.0+

**Sensors provided:**

| Entity Type | Entities |
|-------------|----------|
| **Sensors** | CPU Usage, CPU Temperature, CPU Power, Memory Usage, Uptime, Array State, Array Usage, Parity Progress, per-Disk Usage, per-Share Usage, Flash Usage, UPS Battery, UPS Load, UPS Runtime, UPS Power, Notifications count |
| **Binary Sensors** | Array Started, Parity Check Running, Parity Valid, per-Disk Health, UPS Connected |
| **Switches** | Docker Container start/stop, VM start/stop |
| **Buttons** | Array Start/Stop, Parity Check Start/Stop, Disk Spin Up/Down |

**Features we lack:**
- CPU temperature and CPU power consumption monitoring
- UPS full monitoring (battery, load, runtime, power, connected status)
- Parity progress tracking
- Per-disk health binary status
- Flash device usage monitoring
- Array start/stop buttons
- Parity check start/stop
- Disk spin up/down
- Dynamic entity creation (only creates entities for available services)

---

### 6. chris-mc1/unraid_api (HA integration)

- **Repository:** [chris-mc1/unraid_api](https://github.com/chris-mc1/unraid_api)
- **Language:** Python
- **Architecture:** Lightweight Home Assistant integration using GraphQL API
- **API Type:** GraphQL
- **Status:** Simpler/lighter alternative to ha-unraid

**Entities provided:**
- Array state sensor
- Array used space percentage
- RAM usage percentage
- CPU utilization
- Per-share free space (optional)
- Per-disk state, temperature, spinning status, used space (optional)

**Notable:** This is a simpler, lighter-weight integration focused on monitoring only (no control operations).

---

## Feature Matrix

### Legend
- **Y** = Supported
- **N** = Not supported
- **P** = Partial support
- **--** = Not applicable

### Monitoring Features

| Feature | Our MCP (10 tools, 90 actions) | mgmt-agent (54 MCP tools) | unraid-api-client | mcp-ssh-sre (79 actions) | PSUnraid | ha-unraid | chris-mc1 |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| System info (hostname, uptime) | Y | Y | Y | Y | Y | Y | N |
| CPU usage | Y | Y | Y | Y | Y | Y | Y |
| CPU temperature | N | Y | Y | N | N | Y | N |
| CPU power consumption | N | Y | N | N | N | Y | N |
| Memory usage | Y | Y | Y | Y | Y | Y | Y |
| GPU metrics | N | Y | N | N | N | N | N |
| Fan RPM | N | Y | N | N | N | N | N |
| Motherboard temperature | N | Y | N | N | N | N | N |
| UPS monitoring | N | Y | Y | N | Y | Y | N |
| Network config | Y | Y | Y | Y | N | N | N |
| Network bandwidth | N | Y | N | Y | N | N | N |
| Registration/license info | Y | Y | Y | N | N | N | N |
| Connect settings | Y | Y | Y | N | N | N | N |
| Unraid variables | Y | Y | Y | N | N | N | N |
| System services status | N | Y | Y | N | N | N | N |
| Flash drive info | N | Y | Y | N | N | Y | N |
| Owner info | N | N | Y | N | N | N | N |
| Installed plugins | N | Y | Y | Y | Y | N | N |
| Available updates | N | Y | N | Y | N | N | N |

### Storage Features

| Feature | Our MCP | mgmt-agent | unraid-api-client | mcp-ssh-sre | PSUnraid | ha-unraid | chris-mc1 |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Array status | Y | Y | Y | Y | Y | Y | Y |
| Array start/stop | N | Y | Y | N | Y | Y | N |
| Physical disk listing | Y | Y | Y | N | Y | N | N |
| Disk details | Y | Y | Y | Y | Y | Y | Y |
| Disk SMART data | N | Y | N | Y | N | P | N |
| Disk spin up/down | N | Y | Y | Y | N | Y | N |
| Disk temperatures | P | Y | Y | Y | N | Y | Y |
| Disk I/O stats | N | Y | N | Y | N | N | N |
| Shares info | Y | Y | Y | Y | Y | Y | Y |
| Share configuration | N | Y | N | Y | N | N | N |
| Parity check control | N | Y | Y | N | Y | Y | N |
| Parity check history | N | Y | Y | Y | Y | N | N |
| Parity progress | N | Y | Y | Y | Y | Y | N |
| ZFS pools/datasets/snapshots | N | Y | N | N | N | N | N |
| ZFS ARC stats | N | Y | N | N | N | N | N |
| Unassigned devices | N | Y | N | N | N | N | N |
| Mover status/logs | N | N | N | Y | N | N | N |
| Cache usage | N | N | N | Y | N | N | N |

### Docker Features

| Feature | Our MCP | mgmt-agent | unraid-api-client | mcp-ssh-sre | PSUnraid | ha-unraid | chris-mc1 |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| List containers | Y | Y | Y | Y | Y | Y | N |
| Container details | Y | Y | Y | Y | N | P | N |
| Start/stop/restart | Y | Y | Y | N | Y | Y | N |
| Pause/unpause | N | Y | Y | N | N | N | N |
| Container resource usage | N | Y | Y | Y | N | N | N |
| Container logs | N | N | N | Y | N | N | N |
| Container env vars | N | N | N | Y | N | N | N |
| Container network topology | N | N | N | Y | N | N | N |
| Container port inspection | N | N | N | Y | N | N | N |
| Docker networks | N | Y | Y | Y | N | N | N |
| Docker volumes | N | N | N | Y | N | N | N |
| Container update | N | N | Y | N | N | N | N |
| Container removal | N | N | Y | N | N | N | N |
| Docker settings | N | Y | N | N | N | N | N |

### VM Features

| Feature | Our MCP | mgmt-agent | unraid-api-client | mcp-ssh-sre | PSUnraid | ha-unraid | chris-mc1 |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| List VMs | Y | Y | Y | Y | Y | Y | N |
| VM details | Y | Y | Y | Y | N | P | N |
| Start/stop | Y | Y | Y | N | Y | Y | N |
| Restart | Y | Y | N | N | Y | N | N |
| Pause/resume | N | Y | Y | N | Y | N | N |
| Hibernate | N | Y | N | N | N | N | N |
| Force stop | N | Y | Y | N | Y | N | N |
| Reboot VM | N | N | Y | N | N | N | N |
| VNC info | N | N | N | Y | N | N | N |
| VM libvirt logs | N | N | N | Y | N | N | N |
| VM settings | N | Y | N | N | N | N | N |

### Cloud Storage (RClone) Features

| Feature | Our MCP | mgmt-agent | unraid-api-client | mcp-ssh-sre | PSUnraid | ha-unraid | chris-mc1 |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| List remotes | Y | N | N | N | N | N | N |
| Get config form | Y | N | N | N | N | N | N |
| Create remote | Y | N | N | N | N | N | N |
| Delete remote | Y | N | N | N | N | N | N |

> **Note:** RClone management is unique to our project among these competitors.

### Notification Features

| Feature | Our MCP | mgmt-agent | unraid-api-client | mcp-ssh-sre | PSUnraid | ha-unraid | chris-mc1 |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Notification overview | Y | Y | Y | N | N | Y | N |
| List notifications | Y | Y | Y | Y | Y | N | N |
| Mark as read | N | N | N | N | Y | N | N |
| Delete notifications | N | N | N | N | Y | N | N |

### Logs & Diagnostics

| Feature | Our MCP | mgmt-agent | unraid-api-client | mcp-ssh-sre | PSUnraid | ha-unraid | chris-mc1 |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| List log files | Y | Y | Y | N | N | N | N |
| Get log contents | Y | Y | Y | Y | Y | N | N |
| Log search/grep | N | N | N | Y | N | N | N |
| Error aggregation | N | N | N | Y | N | N | N |
| Syslog access | N | Y | N | Y | Y | N | N |
| Docker daemon log | N | Y | N | Y | N | N | N |
| Health check | Y | Y | N | Y | N | N | N |
| Subscription diagnostics | Y | N | N | N | N | N | N |

### Integration & Protocol Features

| Feature | Our MCP | mgmt-agent | unraid-api-client | mcp-ssh-sre | PSUnraid | ha-unraid | chris-mc1 |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| MCP tools | Y (10 tools, 90 actions) | Y (54) | N | Y (79 actions) | N | N | N |
| MCP Resources | N | Y (5) | N | N | N | N | N |
| MCP Prompts | N | Y (3) | N | N | N | N | N |
| REST API | N | Y (59) | N | N | N | N | N |
| WebSocket streaming | N | Y (9 events) | N | N | N | N | N |
| Prometheus metrics | N | Y (41) | N | N | N | N | N |
| MQTT publishing | N | Y | N | N | N | N | N |
| SSE transport | Y | Y | N | Y | N | N | N |
| Stdio transport | Y | N | N | Y | N | N | N |
| Streamable HTTP | Y | Y | N | Y | N | N | N |
| Pydantic models | N | N | Y | N | N | N | N |
| Safety confirmations | N | Y | N | N | N | N | N |

### Security & Operational Features

| Feature | Our MCP | mgmt-agent | mcp-ssh-sre | PSUnraid |
|---------|:---:|:---:|:---:|:---:|
| Open port scanning | N | N | Y | N |
| SSH login monitoring | N | N | Y | N |
| Container privilege audit | N | N | Y | N |
| SSL certificate expiry | N | N | Y | N |
| Process monitoring | N | N | Y | N |
| Zombie process detection | N | N | Y | N |
| Performance bottleneck analysis | N | N | Y | N |
| System reboot | N | Y | N | N |
| System shutdown | N | Y | N | N |
| User script execution | N | Y | Y | N |

---

## Gap Analysis

### Priority 1: High-Value Features Available via GraphQL API

These features are available through the same GraphQL API we already use and should be straightforward to implement:

1. **Array start/stop control** -- Both `domalab/unraid-api-client` and `PSUnraid` implement this via GraphQL mutations. This is a fundamental control operation that every competitor supports.

2. **Parity check lifecycle** (start, stop, pause, resume, history) -- Available via GraphQL mutations. Critical for array management.

3. **Disk spin up/down** -- Available via GraphQL mutations. Important for power management and noise control.

4. **UPS monitoring** -- Available via GraphQL query. Present in `unraid-api-client`, `PSUnraid`, and `ha-unraid`. Data includes battery level, load, runtime, power state.

5. **System services list** -- Available via GraphQL query (`services`). Shows Docker service, VM manager status, etc.

6. **Flash drive info** -- Available via GraphQL query (`flash`). Boot device monitoring.

7. **Installed plugins list** -- Available via GraphQL query (`plugins`). Useful for understanding server configuration.

8. **Docker networks** -- Available via GraphQL query. Listed in `unraid-api-client`.

9. **Parity history** -- Available via GraphQL query. Historical parity check data.

10. **VM pause/resume and force stop** -- Available via GraphQL mutations. Completing our VM control capabilities.

11. **Docker pause/unpause** -- Available via GraphQL mutations. Completing our Docker control capabilities.

12. **Cloud/remote access status** -- Available via GraphQL queries. Shows Unraid Connect status, remote access configuration.

13. **Notification management** -- Mark as read, delete. `PSUnraid` implements this via GraphQL.

14. **API/OS version info** -- Simple query that helps with compatibility checks.

### Priority 2: High-Value Features Requiring Non-GraphQL Data Sources

These would require SSH access or other system-level access that our GraphQL-only architecture cannot provide:

1. **Container logs** -- Not available via GraphQL. SSH-based solutions (mcp-ssh-sre) can retrieve full container logs via `docker logs`.

2. **SMART disk data** -- Limited via GraphQL. Full SMART data (power-on hours, error counts, reallocated sectors) requires `smartctl` access.

3. **GPU metrics** -- Not available via GraphQL. Requires nvidia-smi or similar.

4. **Process monitoring** -- Not available via GraphQL. Requires `ps`/`top` access.

5. **Network bandwidth** -- Not in GraphQL. Requires direct system access.

6. **Container resource usage** (CPU%, memory) -- Not available through the current GraphQL API at a per-container level in real-time.

7. **Log search/grep** -- While we can get log contents, we cannot search across logs.

8. **Security auditing** -- Not available via GraphQL.

### Priority 3: Architectural Improvements

1. **MCP Resources** -- Add subscribable data streams (system, array, containers, VMs, disks) for real-time AI agent monitoring.

2. **MCP Prompts** -- Add guided interaction templates (disk health analysis, system overview, troubleshooting).

3. **Confirmation for destructive operations** -- Add a `confirm` parameter for array stop, system reboot, container removal, etc.

4. **Pydantic response models** -- Type-safe response parsing like `domalab/unraid-api-client`.

5. **Connection validation tool** -- Simple tool to verify API connectivity and version compatibility.

---

## Recommended Priorities

### Phase 1: Low-Hanging Fruit (GraphQL mutations/queries we already have access to)

**Estimated effort: Small -- these are straightforward GraphQL queries/mutations**

| New Tool | Priority | Notes |
|----------|----------|-------|
| `start_array()` / `stop_array()` | Critical | Every competitor has this |
| `start_parity_check()` / `stop_parity_check()` | Critical | Full parity lifecycle |
| `pause_parity_check()` / `resume_parity_check()` | Critical | Full parity lifecycle |
| `get_parity_history()` | High | Historical data |
| `spin_up_disk()` / `spin_down_disk()` | High | Disk power management |
| `get_ups_status()` | High | UPS monitoring |
| `get_services_status()` | Medium | System services |
| `get_flash_info()` | Medium | Flash drive info |
| `get_plugins()` | Medium | Plugin management |
| `get_docker_networks()` | Medium | Docker networking |
| `pause_docker_container()` / `unpause_docker_container()` | Medium | Docker control |
| `pause_vm()` / `resume_vm()` / `force_stop_vm()` | Medium | VM control |
| `get_cloud_status()` / `get_remote_access()` | Low | Connect info |
| `get_version()` | Low | API version |
| `manage_notifications()` | Low | Mark read/delete |

### Phase 2: MCP Protocol Enhancements

| Enhancement | Priority | Notes |
|-------------|----------|-------|
| MCP Resources (5 streams) | High | Real-time data for AI agents |
| MCP Prompts (3 templates) | Medium | Guided interactions |
| Confirmation parameter | High | Safety for destructive ops |
| Connection validation tool | Medium | Health/compatibility check |

### Phase 3: Advanced Features (may require SSH)

| Feature | Priority | Notes |
|---------|----------|-------|
| Container log retrieval | High | Most-requested SSH-only feature |
| SMART disk health data | High | Disk failure prediction |
| GPU monitoring | Medium | For GPU passthrough users |
| Performance/resource monitoring | Medium | Bottleneck analysis |
| Security auditing | Low | Port scan, login audit |

---

## Sources

- [ruaan-deysel/unraid-management-agent](https://github.com/ruaan-deysel/unraid-management-agent) -- Go-based Unraid plugin with REST API, WebSocket, MCP, Prometheus, and MQTT
- [domalab/unraid-api-client](https://github.com/domalab/unraid-api-client) -- Async Python client for Unraid GraphQL API (PyPI: `unraid-api`)
- [ohare93/mcp-ssh-sre](https://github.com/ohare93/mcp-ssh-sre) -- SSH-based MCP server for read-only server monitoring
- [jlabon2/PSUnraid](https://github.com/jlabon2/PSUnraid) -- PowerShell module for Unraid 7.x management via GraphQL API
- [domalab/ha-unraid](https://github.com/domalab/ha-unraid) (ruaan-deysel fork) -- Home Assistant integration via GraphQL API
- [chris-mc1/unraid_api](https://github.com/chris-mc1/unraid_api) -- Lightweight Home Assistant integration for Unraid
- [nickbeddows-ctrl/unraid-ssh-mcp](https://github.com/nickbeddows-ctrl/unraid-ssh-mcp) -- Guardrailed MCP server for Unraid management via SSH
- [MCP SSH Unraid on LobeHub](https://lobehub.com/mcp/ohare93-unraid-ssh-mcp)
- [MCP SSH SRE on Glama](https://glama.ai/mcp/servers/@ohare93/mcp-ssh-sre)
- [Unraid Integration for Home Assistant (domalab docs)](https://domalab.github.io/ha-unraid/)
- [Home Assistant Unraid Integration forum thread](https://community.home-assistant.io/t/unraid-integration/785003)
