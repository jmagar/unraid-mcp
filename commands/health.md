---
description: Check Unraid system health and connectivity
argument-hint: [action]
---

Execute the `unraid_health` MCP tool with action: `$1`

## Available Actions (3)

**Health Monitoring:**
- `check` - Comprehensive health check of all system components
- `test_connection` - Test basic API connectivity
- `diagnose` - Detailed diagnostic information for troubleshooting

## What Each Action Checks

### `check` - System Health
- API connectivity and response time
- Array status and disk health
- Running services status
- Docker container health
- VM status
- System resources (CPU, RAM, disk I/O)
- Network connectivity
- UPS status (if configured)

Returns: Overall health status (`HEALTHY`, `WARNING`, `CRITICAL`) with component details

### `test_connection` - Connectivity
- GraphQL endpoint availability
- Authentication validity
- Basic query execution
- Network latency

Returns: Connection status and latency metrics

### `diagnose` - Diagnostic Details
- Full system configuration
- Resource utilization trends
- Error logs and warnings
- Component-level diagnostics
- Troubleshooting recommendations

Returns: Detailed diagnostic report

## Example Usage

```
/unraid-health check
/unraid-health test_connection
/unraid-health diagnose
```

**Use Cases:**
- `check` - Quick health status (monitoring dashboards)
- `test_connection` - Verify API access (troubleshooting)
- `diagnose` - Deep dive debugging (issue resolution)

Use the tool to execute the requested health check and present results with clear severity indicators.
