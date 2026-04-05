# MCP Resources Reference

## Overview

MCP resources expose real-time subscription data via URI-based access. Unlike tools, resources do not perform mutations -- they return the latest cached data from persistent WebSocket subscriptions to the Unraid GraphQL API.

Use resources when:
- Reading live telemetry (CPU, memory, array state)
- Monitoring ongoing events (notifications, parity progress)
- Providing real-time context to the LLM without tool invocation overhead

Use the `live` action on the `unraid` tool when:
- You need a one-shot snapshot with a specific collection duration
- You want to control the `collect_for` parameter
- The resource data shows "connecting" (subscription not yet initialized)

## URI Scheme

All resources use the `unraid://` scheme:

```
unraid://logs/stream
unraid://live/<subscription-name>
```

## Available Resources

### Log stream

| URI | Description | Source subscription |
|-----|-------------|---------------------|
| `unraid://logs/stream` | Real-time log file stream | `logFileSubscription` |

Returns log file content with path, total lines, start line, and content. Auto-starts on boot if `UNRAID_AUTOSTART_LOG_PATH` is set or `/var/log/syslog` exists.

### Live telemetry (snapshot subscriptions)

These subscriptions emit data continuously. The resource returns the latest cached value.

| URI | Description | Source subscription |
|-----|-------------|---------------------|
| `unraid://live/cpu` | CPU utilization per core and total | `systemMetricsCpu` |
| `unraid://live/memory` | Memory usage, swap, available, buffer/cache | `systemMetricsMemory` |
| `unraid://live/cpu_telemetry` | CPU power draw and temperature | `systemMetricsCpuTelemetry` |
| `unraid://live/array_state` | Array state, capacity, parity check status | `arraySubscription` |

### Live telemetry (event-driven subscriptions)

These subscriptions only emit when state changes. A timeout does not indicate an error -- it means no recent change occurred.

| URI | Description | Source subscription |
|-----|-------------|---------------------|
| `unraid://live/parity_progress` | Parity check progress, speed, errors | `parityHistorySubscription` |
| `unraid://live/ups_status` | UPS battery, power, model, status | `upsUpdates` |
| `unraid://live/notifications_overview` | Unread/archive notification counts by type | `notificationsOverview` |
| `unraid://live/owner` | Server owner username, URL, avatar | `ownerSubscription` |
| `unraid://live/server_status` | Server name, status, GUID, WAN/LAN IPs | `serversSubscription` |

## Response Format

All resource responses return JSON:

```json
{
  "systemMetricsCpu": {
    "id": "...",
    "percentTotal": 12.5,
    "cpus": [
      {"percentTotal": 15.0, "percentUser": 10.0, "percentSystem": 5.0, "percentIdle": 85.0}
    ]
  },
  "_fetched_at": "2026-04-04T12:00:00.000000"
}
```

The `_fetched_at` timestamp indicates when the data was last received from the WebSocket.

### Connecting state

When a subscription has not yet received data:

```json
{
  "status": "connecting",
  "message": "Subscription 'cpu' is starting. Retry in a moment."
}
```

### Error state

When a subscription has permanently failed:

```json
{
  "status": "error",
  "message": "Subscription 'cpu' failed: WebSocket authentication error"
}
```

Terminal failure states: `failed`, `auth_failed`, `max_retries_exceeded`.

## Auto-start Behavior

When `UNRAID_AUTO_START_SUBSCRIPTIONS=true` (default):
- All snapshot subscriptions start automatically on server boot
- The log file subscription starts if `UNRAID_AUTOSTART_LOG_PATH` is set or `/var/log/syslog` exists
- Resources serve cached data immediately after the first WebSocket message arrives

When `UNRAID_AUTO_START_SUBSCRIPTIONS=false`:
- Subscriptions do not start on boot
- Resources fall back to `subscribe_once` -- a one-shot WebSocket query
- This is useful for low-resource environments or when real-time data is not needed

## Subscription Manager

The `SubscriptionManager` singleton manages persistent WebSocket connections:

- Maintains one WebSocket per subscription type
- Automatic reconnection with exponential backoff (up to `UNRAID_MAX_RECONNECT_ATTEMPTS`)
- Resets reconnect counter after 30 seconds of stable connection
- Log content capped at 1 MB / 5,000 lines to prevent memory growth
- GraphQL-over-WebSocket protocol with `connection_init` and `subscribe` messages

## Diagnostic Tools

Two diagnostic tools help troubleshoot subscription issues:

| Tool | Purpose |
|------|---------|
| `diagnose_subscriptions` | Shows connection states, errors, WebSocket URLs, and data availability for all subscriptions |
| `test_subscription_query` | Sends a test subscription query (allowlisted fields: `containerStats`, `cpu`, `memory`, `array`, `network`, `docker`, `vm`) |

## See Also

- [TOOLS.md](TOOLS.md) -- For the `live` action that provides on-demand snapshots
- [SCHEMA.md](SCHEMA.md) -- GraphQL subscription query definitions
- [../upstream/CLAUDE.md](../upstream/CLAUDE.md) -- Unraid GraphQL subscription schema
