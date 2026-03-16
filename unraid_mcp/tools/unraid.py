"""Single consolidated Unraid tool.

Provides the `unraid` tool with 15 actions, each routing to domain-specific
subactions via the action + subaction pattern.

Actions:
  system       - Server info, metrics, network, UPS (19 subactions)
  health       - Health checks, connection test, diagnostics, setup (4 subactions)
  array        - Parity checks, array state, disk operations (13 subactions)
  disk         - Shares, physical disks, log files (6 subactions)
  docker       - Container lifecycle and network inspection (7 subactions)
  vm           - Virtual machine lifecycle (9 subactions)
  notification - System notifications CRUD (12 subactions)
  key          - API key management (7 subactions)
  plugin       - Plugin management (3 subactions)
  rclone       - Cloud storage remote management (4 subactions)
  setting      - System settings and UPS config (2 subactions)
  customization - Theme and UI customization (5 subactions)
  oidc         - OIDC/SSO provider management (5 subactions)
  user         - Current authenticated user (1 subaction)
  live         - Real-time WebSocket subscription snapshots (11 subactions)
"""

import asyncio
import datetime
import os
import re
import time
from typing import Any, Literal, get_args

from fastmcp import Context, FastMCP

from ..config.logging import logger
from ..core.client import DISK_TIMEOUT, make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler
from ..core.guards import gate_destructive_action
from ..core.setup import elicit_and_configure, elicit_reset_confirmation
from ..core.utils import format_bytes, format_kb, safe_get


# ===========================================================================
# SYSTEM (info)
# ===========================================================================

_SYSTEM_QUERIES: dict[str, str] = {
    "overview": """
        query GetSystemInfo {
          info {
            os { platform distro release codename kernel arch hostname logofile serial build uptime }
            cpu { manufacturer brand vendor family model stepping revision voltage speed speedmin speedmax threads cores processors socket cache }
            memory { layout { bank type clockSpeed formFactor manufacturer partNum serialNum } }
            baseboard { manufacturer model version serial assetTag }
            system { manufacturer model version serial uuid sku }
            versions { core { unraid api kernel } packages { openssl node npm pm2 git nginx php docker } }
            machineId time
          }
        }
    """,
    "array": """
        query GetArrayStatus {
          array {
            id state
            capacity { kilobytes { free used total } disks { free used total } }
            boot { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
            parities { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
            disks { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
            caches { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
          }
        }
    """,
    "network": """
        query GetNetworkInfo {
          servers { id name status wanip lanip localurl remoteurl }
          vars { id port portssl localTld useSsl }
        }
    """,
    "registration": """
        query GetRegistrationInfo {
          registration { id type keyFile { location } state expiration updateExpiration }
        }
    """,
    "variables": """
        query GetSelectiveUnraidVariables {
          vars {
            id version name timeZone comment security workgroup domain domainShort
            hideDotFiles localMaster enableFruit useNtp domainLogin sysModel
            sysFlashSlots useSsl port portssl localTld bindMgt useTelnet porttelnet
            useSsh portssh startPage startArray shutdownTimeout
            shareSmbEnabled shareNfsEnabled shareAfpEnabled shareCacheEnabled
            shareAvahiEnabled safeMode startMode configValid configError joinStatus
            deviceCount flashGuid flashProduct flashVendor mdState mdVersion
            shareCount shareSmbCount shareNfsCount shareAfpCount shareMoverActive
          }
        }
    """,
    "metrics": "query GetMetrics { metrics { cpu { percentTotal } memory { total used free available buffcache percentTotal } } }",
    "services": "query GetServices { services { name online version } }",
    "display": "query GetDisplay { info { display { theme } } }",
    "config": "query GetConfig { config { valid error } }",
    "online": "query GetOnline { online }",
    "owner": "query GetOwner { owner { username avatar url } }",
    "settings": "query GetSettings { settings { unified { values } } }",
    "server": """
        query GetServer {
          info { os { hostname uptime } versions { core { unraid } } machineId time }
          array { state }
          online
        }
    """,
    "servers": "query GetServers { servers { id name status wanip lanip localurl remoteurl } }",
    "flash": "query GetFlash { flash { id vendor product } }",
    "ups_devices": "query GetUpsDevices { upsDevices { id name model status battery { chargeLevel estimatedRuntime health } power { loadPercentage inputVoltage outputVoltage } } }",
    "ups_device": "query GetUpsDevice($id: String!) { upsDeviceById(id: $id) { id name model status battery { chargeLevel estimatedRuntime health } power { loadPercentage inputVoltage outputVoltage nominalPower currentPower } } }",
    "ups_config": "query GetUpsConfig { upsConfiguration { service upsCable upsType device batteryLevel minutes timeout killUps upsName } }",
}

_SYSTEM_SUBACTIONS: set[str] = set(_SYSTEM_QUERIES)


def _analyze_disk_health(disks: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "healthy": 0,
        "failed": 0,
        "missing": 0,
        "new": 0,
        "warning": 0,
        "critical": 0,
        "unknown": 0,
    }
    for disk in disks:
        status = disk.get("status", "").upper()
        warning = disk.get("warning")
        critical = disk.get("critical")
        if status == "DISK_OK":
            counts["critical" if critical else "warning" if warning else "healthy"] += 1
        elif status in ("DISK_DSBL", "DISK_INVALID"):
            counts["failed"] += 1
        elif status == "DISK_NP":
            counts["missing"] += 1
        elif status == "DISK_NEW":
            counts["new"] += 1
        else:
            counts["unknown"] += 1
    return counts


async def _handle_system(subaction: str, device_id: str | None) -> dict[str, Any]:
    if subaction not in _SYSTEM_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for system. Must be one of: {sorted(_SYSTEM_SUBACTIONS)}"
        )

    if subaction == "ups_device" and not device_id:
        raise ToolError("device_id is required for system/ups_device")

    query = _SYSTEM_QUERIES[subaction]
    variables: dict[str, Any] | None = {"id": device_id} if subaction == "ups_device" else None

    with tool_error_handler("system", subaction, logger):
        logger.info(f"Executing unraid action=system subaction={subaction}")
        data = await make_graphql_request(query, variables)

        if subaction == "overview":
            raw = data.get("info") or {}
            if not raw:
                raise ToolError("No system info returned from Unraid API")
            summary: dict[str, Any] = {}
            if raw.get("os"):
                os_info = raw["os"]
                summary["os"] = (
                    f"{os_info.get('distro')} {os_info.get('release')} ({os_info.get('platform')}, {os_info.get('arch')})"
                )
                summary["hostname"] = os_info.get("hostname")
                summary["uptime"] = os_info.get("uptime")
            if raw.get("cpu"):
                cpu = raw["cpu"]
                summary["cpu"] = (
                    f"{cpu.get('manufacturer')} {cpu.get('brand')} ({cpu.get('cores')} cores, {cpu.get('threads')} threads)"
                )
            if raw.get("memory") and raw["memory"].get("layout"):
                summary["memory_layout_details"] = [
                    f"Bank {s.get('bank')}: {s.get('type')}, {s.get('clockSpeed')}MHz, {s.get('manufacturer')}, {s.get('partNum')}"
                    for s in raw["memory"]["layout"]
                ]
            return {"summary": summary, "details": raw}

        if subaction == "array":
            raw = data.get("array") or {}
            if not raw:
                raise ToolError("No array information returned from Unraid API")
            summary = {"state": raw.get("state")}
            if raw.get("capacity") and raw["capacity"].get("kilobytes"):
                kb = raw["capacity"]["kilobytes"]
                summary["capacity_total"] = format_kb(kb.get("total"))
                summary["capacity_used"] = format_kb(kb.get("used"))
                summary["capacity_free"] = format_kb(kb.get("free"))
            summary["num_parity_disks"] = len(raw.get("parities", []))
            summary["num_data_disks"] = len(raw.get("disks", []))
            summary["num_cache_pools"] = len(raw.get("caches", []))
            health: dict[str, Any] = {}
            for key, label in [
                ("parities", "parity_health"),
                ("disks", "data_health"),
                ("caches", "cache_health"),
            ]:
                if raw.get(key):
                    health[label] = _analyze_disk_health(raw[key])
            total_failed = sum(h.get("failed", 0) for h in health.values())
            total_critical = sum(h.get("critical", 0) for h in health.values())
            total_missing = sum(h.get("missing", 0) for h in health.values())
            total_warning = sum(h.get("warning", 0) for h in health.values())
            summary["overall_health"] = (
                "CRITICAL"
                if total_failed or total_critical
                else "DEGRADED"
                if total_missing
                else "WARNING"
                if total_warning
                else "HEALTHY"
            )
            summary["health_summary"] = health
            return {"summary": summary, "details": raw}

        if subaction == "display":
            return dict((data.get("info") or {}).get("display") or {})
        if subaction == "online":
            return {"online": data.get("online")}
        if subaction == "settings":
            settings = data.get("settings") or {}
            if not settings or not settings.get("unified"):
                raise ToolError("No settings data returned or unexpected structure")
            values = settings["unified"].get("values") or {}
            return dict(values) if isinstance(values, dict) else {"raw": values}
        if subaction == "server":
            return data
        if subaction == "network":
            servers_data = data.get("servers") or []
            vars_data = data.get("vars") or {}
            access_urls = []
            for srv in servers_data:
                if srv.get("lanip"):
                    access_urls.append(
                        {"type": "LAN", "ipv4": srv["lanip"], "url": srv.get("localurl")}
                    )
                if srv.get("wanip"):
                    access_urls.append(
                        {"type": "WAN", "ipv4": srv["wanip"], "url": srv.get("remoteurl")}
                    )
            return {
                "accessUrls": access_urls,
                "httpPort": vars_data.get("port"),
                "httpsPort": vars_data.get("portssl"),
                "localTld": vars_data.get("localTld"),
                "useSsl": vars_data.get("useSsl"),
            }

        simple_dict = {
            "registration": "registration",
            "variables": "vars",
            "metrics": "metrics",
            "config": "config",
            "owner": "owner",
            "flash": "flash",
            "ups_device": "upsDeviceById",
            "ups_config": "upsConfiguration",
        }
        if subaction in simple_dict:
            return dict(data.get(simple_dict[subaction]) or {})

        list_actions = {
            "services": ("services", "services"),
            "servers": ("servers", "servers"),
            "ups_devices": ("upsDevices", "ups_devices"),
        }
        if subaction in list_actions:
            response_key, output_key = list_actions[subaction]
            items = data.get(response_key) or []
            return {output_key: list(items) if isinstance(items, list) else []}

        raise ToolError(f"Unhandled system subaction '{subaction}' — this is a bug")


# ===========================================================================
# HEALTH
# ===========================================================================

_HEALTH_SUBACTIONS: set[str] = {"check", "test_connection", "diagnose", "setup"}
_SEVERITY = {"healthy": 0, "warning": 1, "degraded": 2, "unhealthy": 3}


async def _handle_health(subaction: str, ctx: Context | None) -> dict[str, Any] | str:
    if subaction not in _HEALTH_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for health. Must be one of: {sorted(_HEALTH_SUBACTIONS)}"
        )

    from ..config.settings import (
        CREDENTIALS_ENV_PATH,
        UNRAID_API_URL,
    )
    from ..core.utils import safe_display_url
    from ..subscriptions.utils import _analyze_subscription_status

    if subaction == "setup":
        if CREDENTIALS_ENV_PATH.exists():
            try:
                await make_graphql_request(_SYSTEM_QUERIES["online"])
                connection_ok = True
            except Exception:
                connection_ok = False
            status_note = (
                "and working"
                if connection_ok
                else "but the connection test failed — may be a transient outage"
            )
            reset = await elicit_reset_confirmation(
                ctx,
                f"{safe_display_url(UNRAID_API_URL) or ''} ({status_note})",
            )
            if not reset:
                return (
                    f"✅ Credentials already configured ({status_note}).\n"
                    f"URL: `{safe_display_url(UNRAID_API_URL)}`\n\nNo changes made."
                )
        configured = await elicit_and_configure(ctx)
        if configured:
            return "✅ Credentials configured successfully. You can now use all Unraid MCP tools."
        return (
            f"⚠️ Credentials not configured.\n\n"
            f"Your MCP client may not support elicitation, or setup was cancelled.\n\n"
            f"**Manual setup** — create `{CREDENTIALS_ENV_PATH}` with:\n"
            f"```\nUNRAID_API_URL=https://your-unraid-server:port\nUNRAID_API_KEY=your-api-key\n```\n\n"
            "Then run any Unraid tool to connect."
        )

    with tool_error_handler("health", subaction, logger):
        logger.info(f"Executing unraid action=health subaction={subaction}")

        if subaction == "test_connection":
            start = time.time()
            data = await make_graphql_request(_SYSTEM_QUERIES["online"])
            latency = round((time.time() - start) * 1000, 2)
            return {"status": "connected", "online": data.get("online"), "latency_ms": latency}

        if subaction == "check":
            return await _comprehensive_health_check()

        if subaction == "diagnose":
            from ..server import cache_middleware, error_middleware
            from ..subscriptions.manager import subscription_manager
            from ..subscriptions.resources import ensure_subscriptions_started

            await ensure_subscriptions_started()
            status = await subscription_manager.get_subscription_status()
            error_count, connection_issues = _analyze_subscription_status(status)
            cache_stats = cache_middleware.statistics()
            return {
                "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                "environment": {
                    "auto_start_enabled": subscription_manager.auto_start_enabled,
                    "max_reconnect_attempts": subscription_manager.max_reconnect_attempts,
                    "api_url_configured": bool(UNRAID_API_URL),
                },
                "subscriptions": status,
                "summary": {
                    "total_configured": len(subscription_manager.subscription_configs),
                    "active_count": len(subscription_manager.active_subscriptions),
                    "with_data": len(subscription_manager.resource_data),
                    "in_error_state": error_count,
                    "connection_issues": connection_issues,
                },
                "cache": {
                    "call_tool": {
                        "hits": cache_stats.call_tool.get.hit,
                        "misses": cache_stats.call_tool.get.miss,
                        "puts": cache_stats.call_tool.put.total,
                    }
                    if cache_stats.call_tool
                    else {"hits": 0, "misses": 0, "puts": 0},
                },
                "errors": error_middleware.get_error_stats(),
            }

        raise ToolError(f"Unhandled health subaction '{subaction}' — this is a bug")


async def _comprehensive_health_check() -> dict[str, Any]:
    from ..config.settings import (
        UNRAID_API_URL,
        UNRAID_MCP_HOST,
        UNRAID_MCP_PORT,
        UNRAID_MCP_TRANSPORT,
        VERSION,
    )
    from ..core.utils import safe_display_url

    start_time = time.time()
    health_severity = 0
    issues: list[str] = []

    def _escalate(level: str) -> None:
        nonlocal health_severity
        health_severity = max(health_severity, _SEVERITY.get(level, 0))

    try:
        query = """
        query ComprehensiveHealthCheck {
          info { machineId time versions { core { unraid } } os { uptime } }
          array { state }
          notifications { overview { unread { alert warning total } } }
          docker { containers(skipCache: true) { id state status } }
        }
        """
        data = await make_graphql_request(query)
        api_latency = round((time.time() - start_time) * 1000, 2)

        health_info: dict[str, Any] = {
            "status": "healthy",
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "api_latency_ms": api_latency,
            "server": {
                "name": "Unraid MCP Server",
                "version": VERSION,
                "transport": UNRAID_MCP_TRANSPORT,
                "host": UNRAID_MCP_HOST,
                "port": UNRAID_MCP_PORT,
            },
        }

        if not data:
            health_info["status"] = "unhealthy"
            health_info["issues"] = ["No response from Unraid API"]
            return health_info

        info = data.get("info") or {}
        if info:
            health_info["unraid_system"] = {
                "status": "connected",
                "url": safe_display_url(UNRAID_API_URL),
                "machine_id": info.get("machineId"),
                "version": ((info.get("versions") or {}).get("core") or {}).get("unraid"),
                "uptime": (info.get("os") or {}).get("uptime"),
            }
        else:
            _escalate("degraded")
            issues.append("Unable to retrieve system info")

        array_info = data.get("array") or {}
        if array_info:
            state = array_info.get("state", "unknown")
            health_info["array_status"] = {
                "state": state,
                "healthy": state in ("STARTED", "STOPPED"),
            }
            if state not in ("STARTED", "STOPPED"):
                _escalate("warning")
                issues.append(f"Array in unexpected state: {state}")
        else:
            _escalate("warning")
            issues.append("Unable to retrieve array status")

        notifications = data.get("notifications") or {}
        if notifications and notifications.get("overview"):
            unread = notifications["overview"].get("unread") or {}
            alerts = unread.get("alert", 0)
            health_info["notifications"] = {
                "unread_total": unread.get("total", 0),
                "unread_alerts": alerts,
                "unread_warnings": unread.get("warning", 0),
            }
            if alerts > 0:
                _escalate("warning")
                issues.append(f"{alerts} unread alert(s)")

        docker = data.get("docker") or {}
        if docker and docker.get("containers"):
            containers = docker["containers"]
            health_info["docker_services"] = {
                "total": len(containers),
                "running": len(
                    [c for c in containers if (c.get("state") or "").upper() == "RUNNING"]
                ),
                "stopped": len(
                    [c for c in containers if (c.get("state") or "").upper() == "EXITED"]
                ),
            }

        if api_latency > 10000:
            _escalate("degraded")
            issues.append(f"Very high API latency: {api_latency}ms")
        elif api_latency > 5000:
            _escalate("warning")
            issues.append(f"High API latency: {api_latency}ms")

        severity_to_status = {v: k for k, v in _SEVERITY.items()}
        health_info["status"] = severity_to_status.get(health_severity, "healthy")
        if issues:
            health_info["issues"] = issues
        health_info["performance"] = {
            "api_response_time_ms": api_latency,
            "check_duration_ms": round((time.time() - start_time) * 1000, 2),
        }
        return health_info

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "error": str(e),
        }


# ===========================================================================
# ARRAY
# ===========================================================================

_ARRAY_QUERIES: dict[str, str] = {
    "parity_status": "query GetParityStatus { array { parityCheckStatus { progress speed errors status paused running correcting } } }",
    "parity_history": "query GetParityHistory { parityHistory { date duration speed status errors progress correcting paused running } }",
}

_ARRAY_MUTATIONS: dict[str, str] = {
    "parity_start": "mutation StartParityCheck($correct: Boolean!) { parityCheck { start(correct: $correct) } }",
    "parity_pause": "mutation PauseParityCheck { parityCheck { pause } }",
    "parity_resume": "mutation ResumeParityCheck { parityCheck { resume } }",
    "parity_cancel": "mutation CancelParityCheck { parityCheck { cancel } }",
    "start_array": "mutation StartArray { array { setState(input: { desiredState: START }) { state capacity { kilobytes { free used total } } } } }",
    "stop_array": "mutation StopArray { array { setState(input: { desiredState: STOP }) { state } } }",
    "add_disk": "mutation AddDisk($id: PrefixedID!, $slot: Int) { array { addDiskToArray(input: { id: $id, slot: $slot }) { state disks { id name device type status } } } }",
    "remove_disk": "mutation RemoveDisk($id: PrefixedID!) { array { removeDiskFromArray(input: { id: $id }) { state disks { id name device type } } } }",
    "mount_disk": "mutation MountDisk($id: PrefixedID!) { array { mountArrayDisk(id: $id) { id name device status } } }",
    "unmount_disk": "mutation UnmountDisk($id: PrefixedID!) { array { unmountArrayDisk(id: $id) { id name device status } } }",
    "clear_disk_stats": "mutation ClearDiskStats($id: PrefixedID!) { array { clearArrayDiskStatistics(id: $id) } }",
}

_ARRAY_SUBACTIONS: set[str] = set(_ARRAY_QUERIES) | set(_ARRAY_MUTATIONS)
_ARRAY_DESTRUCTIVE: set[str] = {"remove_disk", "clear_disk_stats", "stop_array"}


async def _handle_array(
    subaction: str,
    disk_id: str | None,
    correct: bool | None,
    slot: int | None,
    ctx: Context | None,
    confirm: bool,
) -> dict[str, Any]:
    if subaction not in _ARRAY_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for array. Must be one of: {sorted(_ARRAY_SUBACTIONS)}"
        )

    await gate_destructive_action(
        ctx,
        subaction,
        _ARRAY_DESTRUCTIVE,
        confirm,
        {
            "remove_disk": f"Remove disk **{disk_id}** from the array. The array must be stopped first.",
            "clear_disk_stats": f"Clear all I/O statistics for disk **{disk_id}**. This cannot be undone.",
            "stop_array": "Stop the Unraid array. Running containers and VMs may lose access to array shares.",
        },
    )

    with tool_error_handler("array", subaction, logger):
        logger.info(f"Executing unraid action=array subaction={subaction}")

        if subaction in _ARRAY_QUERIES:
            data = await make_graphql_request(_ARRAY_QUERIES[subaction])
            return {"success": True, "subaction": subaction, "data": data}

        if subaction == "parity_start":
            if correct is None:
                raise ToolError("correct is required for array/parity_start")
            data = await make_graphql_request(_ARRAY_MUTATIONS[subaction], {"correct": correct})
            return {"success": True, "subaction": subaction, "data": data}

        if subaction in (
            "parity_pause",
            "parity_resume",
            "parity_cancel",
            "start_array",
            "stop_array",
        ):
            data = await make_graphql_request(_ARRAY_MUTATIONS[subaction])
            return {"success": True, "subaction": subaction, "data": data}

        if subaction == "add_disk":
            if not disk_id:
                raise ToolError("disk_id is required for array/add_disk")
            variables: dict[str, Any] = {"id": disk_id}
            if slot is not None:
                variables["slot"] = slot
            data = await make_graphql_request(_ARRAY_MUTATIONS[subaction], variables)
            return {"success": True, "subaction": subaction, "data": data}

        if subaction in ("remove_disk", "mount_disk", "unmount_disk", "clear_disk_stats"):
            if not disk_id:
                raise ToolError(f"disk_id is required for array/{subaction}")
            data = await make_graphql_request(_ARRAY_MUTATIONS[subaction], {"id": disk_id})
            return {"success": True, "subaction": subaction, "data": data}

        raise ToolError(f"Unhandled array subaction '{subaction}' — this is a bug")


# ===========================================================================
# DISK (shares, physical disks, logs, flash backup)
# ===========================================================================

_DISK_QUERIES: dict[str, str] = {
    "shares": "query GetSharesInfo { shares { id name free used size include exclude cache nameOrig comment allocator splitLevel floor cow color luksStatus } }",
    "disks": "query ListPhysicalDisks { disks { id device name } }",
    "disk_details": "query GetDiskDetails($id: PrefixedID!) { disk(id: $id) { id device name serialNum size temperature } }",
    "log_files": "query ListLogFiles { logFiles { name path size modifiedAt } }",
    "logs": "query GetLogContent($path: String!, $lines: Int) { logFile(path: $path, lines: $lines) { path content totalLines startLine } }",
}

_DISK_MUTATIONS: dict[str, str] = {
    "flash_backup": "mutation InitiateFlashBackup($input: InitiateFlashBackupInput!) { initiateFlashBackup(input: $input) { status jobId } }",
}

_DISK_SUBACTIONS: set[str] = set(_DISK_QUERIES) | set(_DISK_MUTATIONS)
_DISK_DESTRUCTIVE: set[str] = {"flash_backup"}
_ALLOWED_LOG_PREFIXES = ("/var/log/", "/boot/logs/", "/mnt/")
_MAX_TAIL_LINES = 10_000


async def _handle_disk(
    subaction: str,
    disk_id: str | None,
    log_path: str | None,
    tail_lines: int,
    remote_name: str | None,
    source_path: str | None,
    destination_path: str | None,
    backup_options: dict[str, Any] | None,
    ctx: Context | None,
    confirm: bool,
) -> dict[str, Any]:
    if subaction not in _DISK_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for disk. Must be one of: {sorted(_DISK_SUBACTIONS)}"
        )

    await gate_destructive_action(
        ctx,
        subaction,
        _DISK_DESTRUCTIVE,
        confirm,
        f"Back up flash drive to **{remote_name}:{destination_path}**. Existing backups will be overwritten.",
    )

    if subaction == "disk_details" and not disk_id:
        raise ToolError("disk_id is required for disk/disk_details")

    if subaction == "logs":
        if tail_lines < 1 or tail_lines > _MAX_TAIL_LINES:
            raise ToolError(f"tail_lines must be between 1 and {_MAX_TAIL_LINES}, got {tail_lines}")
        if not log_path:
            raise ToolError("log_path is required for disk/logs")
        normalized = await asyncio.to_thread(os.path.realpath, log_path)
        if not any(normalized.startswith(p) for p in _ALLOWED_LOG_PREFIXES):
            raise ToolError(f"log_path must start with one of: {', '.join(_ALLOWED_LOG_PREFIXES)}")
        log_path = normalized

    if subaction == "flash_backup":
        if not remote_name:
            raise ToolError("remote_name is required for disk/flash_backup")
        if not source_path:
            raise ToolError("source_path is required for disk/flash_backup")
        if not destination_path:
            raise ToolError("destination_path is required for disk/flash_backup")
        input_data: dict[str, Any] = {
            "remoteName": remote_name,
            "sourcePath": source_path,
            "destinationPath": destination_path,
        }
        if backup_options is not None:
            input_data["options"] = backup_options
        with tool_error_handler("disk", subaction, logger):
            data = await make_graphql_request(
                _DISK_MUTATIONS["flash_backup"], {"input": input_data}
            )
            backup = data.get("initiateFlashBackup")
            if not backup:
                raise ToolError("Failed to start flash backup: no confirmation from server")
            return {"success": True, "subaction": "flash_backup", "data": backup}

    custom_timeout = DISK_TIMEOUT if subaction in ("disks", "disk_details") else None
    variables: dict[str, Any] | None = None
    if subaction == "disk_details":
        variables = {"id": disk_id}
    elif subaction == "logs":
        variables = {"path": log_path, "lines": tail_lines}

    with tool_error_handler("disk", subaction, logger):
        logger.info(f"Executing unraid action=disk subaction={subaction}")
        data = await make_graphql_request(
            _DISK_QUERIES[subaction], variables, custom_timeout=custom_timeout
        )

        if subaction == "shares":
            return {"shares": data.get("shares", [])}
        if subaction == "disks":
            return {"disks": data.get("disks", [])}
        if subaction == "disk_details":
            raw = data.get("disk", {})
            if not raw:
                raise ToolError(f"Disk '{disk_id}' not found")
            return {
                "summary": {
                    "disk_id": raw.get("id"),
                    "device": raw.get("device"),
                    "name": raw.get("name"),
                    "serial_number": raw.get("serialNum"),
                    "size_formatted": format_bytes(raw.get("size")),
                    "temperature": f"{raw['temperature']}\u00b0C"
                    if raw.get("temperature") is not None
                    else "N/A",
                },
                "details": raw,
            }
        if subaction == "log_files":
            return {"log_files": data.get("logFiles", [])}
        if subaction == "logs":
            return dict(data.get("logFile") or {})

        raise ToolError(f"Unhandled disk subaction '{subaction}' — this is a bug")


# ===========================================================================
# DOCKER
# ===========================================================================

_DOCKER_QUERIES: dict[str, str] = {
    "list": "query ListDockerContainers { docker { containers(skipCache: false) { id names image state status autoStart } } }",
    "details": "query GetContainerDetails { docker { containers(skipCache: false) { id names image imageId command created ports { ip privatePort publicPort type } sizeRootFs labels state status hostConfig { networkMode } networkSettings mounts autoStart } } }",
    "networks": "query GetDockerNetworks { docker { networks { id name driver scope } } }",
    "network_details": "query GetDockerNetwork { docker { networks { id name driver scope enableIPv6 internal attachable containers options labels } } }",
    "_resolve": "query ResolveContainerID { docker { containers(skipCache: true) { id names } } }",
}

_DOCKER_MUTATIONS: dict[str, str] = {
    "start": "mutation StartContainer($id: PrefixedID!) { docker { start(id: $id) { id names state status } } }",
    "stop": "mutation StopContainer($id: PrefixedID!) { docker { stop(id: $id) { id names state status } } }",
}

_DOCKER_SUBACTIONS: set[str] = set(_DOCKER_QUERIES) | set(_DOCKER_MUTATIONS) | {"restart"}
_DOCKER_NEEDS_CONTAINER_ID = {"start", "stop", "details", "restart"}
_DOCKER_ID_PATTERN = re.compile(r"^[a-f0-9]{64}(:[a-z0-9]+)?$", re.IGNORECASE)
_DOCKER_SHORT_ID_PATTERN = re.compile(r"^[a-f0-9]{12,63}$", re.IGNORECASE)


def _find_container(
    identifier: str, containers: list[dict[str, Any]], *, strict: bool = False
) -> dict[str, Any] | None:
    for c in containers:
        if c.get("id") == identifier or identifier in c.get("names", []):
            return c
    if strict:
        return None
    id_lower = identifier.lower()
    for c in containers:
        for name in c.get("names", []):
            if name.lower().startswith(id_lower):
                return c
    for c in containers:
        for name in c.get("names", []):
            if id_lower in name.lower():
                return c
    return None


async def _resolve_container_id(container_id: str, *, strict: bool = False) -> str:
    if _DOCKER_ID_PATTERN.match(container_id):
        return container_id
    data = await make_graphql_request(_DOCKER_QUERIES["_resolve"])
    containers = safe_get(data, "docker", "containers", default=[])
    if _DOCKER_SHORT_ID_PATTERN.match(container_id):
        id_lower = container_id.lower()
        matches = [
            c for c in containers if (c.get("id") or "").lower().split(":")[0].startswith(id_lower)
        ]
        if len(matches) == 1:
            return str(matches[0].get("id", ""))
        if len(matches) > 1:
            raise ToolError(
                f"Short ID prefix '{container_id}' is ambiguous. Matches: {', '.join(str(c.get('id', '')) for c in matches[:5])}."
            )
    resolved = _find_container(container_id, containers, strict=strict)
    if resolved:
        return str(resolved.get("id", ""))
    names: list[str] = []
    for c in containers:
        names.extend(c.get("names", []))
    msg = (
        f"Container '{container_id}' not found by exact match. Mutations require exact name or full ID."
        if strict
        else f"Container '{container_id}' not found."
    )
    if names:
        msg += f" Available: {', '.join(names[:10])}"
    raise ToolError(msg)


async def _handle_docker(
    subaction: str, container_id: str | None, network_id: str | None
) -> dict[str, Any]:
    if subaction not in _DOCKER_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for docker. Must be one of: {sorted(_DOCKER_SUBACTIONS)}"
        )
    if subaction in _DOCKER_NEEDS_CONTAINER_ID and not container_id:
        raise ToolError(f"container_id is required for docker/{subaction}")
    if subaction == "network_details" and not network_id:
        raise ToolError("network_id is required for docker/network_details")

    with tool_error_handler("docker", subaction, logger):
        logger.info(f"Executing unraid action=docker subaction={subaction}")

        if subaction == "list":
            data = await make_graphql_request(_DOCKER_QUERIES["list"])
            return {"containers": safe_get(data, "docker", "containers", default=[])}

        if subaction == "details":
            actual_id = await _resolve_container_id(container_id or "")
            data = await make_graphql_request(_DOCKER_QUERIES["details"])
            for c in safe_get(data, "docker", "containers", default=[]):
                if c.get("id") == actual_id:
                    return c
            raise ToolError(f"Container '{container_id}' not found in details response.")

        if subaction == "networks":
            data = await make_graphql_request(_DOCKER_QUERIES["networks"])
            return {"networks": safe_get(data, "docker", "networks", default=[])}

        if subaction == "network_details":
            data = await make_graphql_request(_DOCKER_QUERIES["network_details"])
            for net in safe_get(data, "docker", "networks", default=[]):
                if net.get("id") == network_id or net.get("name") == network_id:
                    return dict(net)
            raise ToolError(f"Network '{network_id}' not found.")

        if subaction == "restart":
            actual_id = await _resolve_container_id(container_id or "", strict=True)
            stop_data = await make_graphql_request(
                _DOCKER_MUTATIONS["stop"],
                {"id": actual_id},
                operation_context={"operation": "stop"},
            )
            stop_was_idempotent = stop_data.get("idempotent_success", False)
            start_data = await make_graphql_request(
                _DOCKER_MUTATIONS["start"],
                {"id": actual_id},
                operation_context={"operation": "start"},
            )
            result = (
                {}
                if start_data.get("idempotent_success")
                else safe_get(start_data, "docker", "start", default={})
            )
            response: dict[str, Any] = {
                "success": True,
                "subaction": "restart",
                "container": result,
            }
            if stop_was_idempotent:
                response["note"] = "Container was already stopped before restart"
            return response

        actual_id = await _resolve_container_id(container_id or "", strict=True)
        data = await make_graphql_request(
            _DOCKER_MUTATIONS[subaction],
            {"id": actual_id},
            operation_context={"operation": subaction},
        )
        if data.get("idempotent_success"):
            return {
                "success": True,
                "subaction": subaction,
                "idempotent": True,
                "message": f"Container already in desired state for '{subaction}'",
            }
        return {
            "success": True,
            "subaction": subaction,
            "container": (data.get("docker") or {}).get(subaction),
        }


# ===========================================================================
# VM
# ===========================================================================

_VM_QUERIES: dict[str, str] = {
    "list": "query ListVMs { vms { id domains { id name state uuid } } }",
    "details": "query ListVMs { vms { id domains { id name state uuid } } }",
}

_VM_MUTATIONS: dict[str, str] = {
    "start": "mutation StartVM($id: PrefixedID!) { vm { start(id: $id) } }",
    "stop": "mutation StopVM($id: PrefixedID!) { vm { stop(id: $id) } }",
    "pause": "mutation PauseVM($id: PrefixedID!) { vm { pause(id: $id) } }",
    "resume": "mutation ResumeVM($id: PrefixedID!) { vm { resume(id: $id) } }",
    "force_stop": "mutation ForceStopVM($id: PrefixedID!) { vm { forceStop(id: $id) } }",
    "reboot": "mutation RebootVM($id: PrefixedID!) { vm { reboot(id: $id) } }",
    "reset": "mutation ResetVM($id: PrefixedID!) { vm { reset(id: $id) } }",
}

_VM_SUBACTIONS: set[str] = set(_VM_QUERIES) | set(_VM_MUTATIONS)
_VM_DESTRUCTIVE: set[str] = {"force_stop", "reset"}
_VM_MUTATION_FIELDS: dict[str, str] = {"force_stop": "forceStop"}


async def _handle_vm(
    subaction: str, vm_id: str | None, ctx: Context | None, confirm: bool
) -> dict[str, Any]:
    if subaction not in _VM_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for vm. Must be one of: {sorted(_VM_SUBACTIONS)}"
        )
    if subaction != "list" and not vm_id:
        raise ToolError(f"vm_id is required for vm/{subaction}")

    await gate_destructive_action(
        ctx,
        subaction,
        _VM_DESTRUCTIVE,
        confirm,
        {
            "force_stop": f"Force stop VM **{vm_id}**. Unsaved data may be lost.",
            "reset": f"Reset VM **{vm_id}**. This is a hard reset — unsaved data may be lost.",
        },
    )

    with tool_error_handler("vm", subaction, logger):
        logger.info(f"Executing unraid action=vm subaction={subaction}")

        if subaction == "list":
            data = await make_graphql_request(_VM_QUERIES["list"])
            if data.get("vms"):
                vms = data["vms"].get("domains") or data["vms"].get("domain") or []
                if isinstance(vms, dict):
                    vms = [vms]
                return {"vms": vms}
            return {"vms": []}

        if subaction == "details":
            data = await make_graphql_request(_VM_QUERIES["details"])
            if not data.get("vms"):
                raise ToolError("No VM data returned from server")
            vms = data["vms"].get("domains") or data["vms"].get("domain") or []
            if isinstance(vms, dict):
                vms = [vms]
            for vm in vms:
                if vm.get("uuid") == vm_id or vm.get("id") == vm_id or vm.get("name") == vm_id:
                    return dict(vm)
            available = [f"{v.get('name')} (UUID: {v.get('uuid')})" for v in vms]
            raise ToolError(f"VM '{vm_id}' not found. Available: {', '.join(available)}")

        data = await make_graphql_request(_VM_MUTATIONS[subaction], {"id": vm_id})
        field = _VM_MUTATION_FIELDS.get(subaction, subaction)
        if data.get("vm") and field in data["vm"]:
            return {"success": data["vm"][field], "subaction": subaction, "vm_id": vm_id}
        raise ToolError(f"Failed to {subaction} VM or unexpected response")


# ===========================================================================
# NOTIFICATION
# ===========================================================================

_NOTIFICATION_QUERIES: dict[str, str] = {
    "overview": "query GetNotificationsOverview { notifications { overview { unread { info warning alert total } archive { info warning alert total } } } }",
    "list": "query ListNotifications($filter: NotificationFilter!) { notifications { list(filter: $filter) { id title subject description importance link type timestamp formattedTimestamp } } }",
}

_NOTIFICATION_MUTATIONS: dict[str, str] = {
    "create": "mutation CreateNotification($input: NotificationData!) { createNotification(input: $input) { id title importance } }",
    "archive": "mutation ArchiveNotification($id: PrefixedID!) { archiveNotification(id: $id) { id title importance } }",
    "mark_unread": "mutation UnreadNotification($id: PrefixedID!) { unreadNotification(id: $id) { id title importance } }",
    "delete": "mutation DeleteNotification($id: PrefixedID!, $type: NotificationType!) { deleteNotification(id: $id, type: $type) { unread { info warning alert total } archive { info warning alert total } } }",
    "delete_archived": "mutation DeleteArchivedNotifications { deleteArchivedNotifications { unread { info warning alert total } archive { info warning alert total } } }",
    "archive_all": "mutation ArchiveAllNotifications($importance: NotificationImportance) { archiveAll(importance: $importance) { unread { info warning alert total } archive { info warning alert total } } }",
    "archive_many": "mutation ArchiveNotifications($ids: [PrefixedID!]!) { archiveNotifications(ids: $ids) { unread { info warning alert total } archive { info warning alert total } } }",
    "unarchive_many": "mutation UnarchiveNotifications($ids: [PrefixedID!]!) { unarchiveNotifications(ids: $ids) { unread { info warning alert total } archive { info warning alert total } } }",
    "unarchive_all": "mutation UnarchiveAll($importance: NotificationImportance) { unarchiveAll(importance: $importance) { unread { info warning alert total } archive { info warning alert total } } }",
    "recalculate": "mutation RecalculateOverview { recalculateOverview { unread { info warning alert total } archive { info warning alert total } } }",
}

_NOTIFICATION_SUBACTIONS: set[str] = set(_NOTIFICATION_QUERIES) | set(_NOTIFICATION_MUTATIONS)
_NOTIFICATION_DESTRUCTIVE: set[str] = {"delete", "delete_archived"}
_VALID_IMPORTANCE = frozenset({"ALERT", "WARNING", "INFO"})
_VALID_LIST_TYPES = frozenset({"UNREAD", "ARCHIVE"})
_VALID_NOTIF_TYPES = frozenset({"UNREAD", "ARCHIVE"})


async def _handle_notification(
    subaction: str,
    ctx: Context | None,
    confirm: bool,
    notification_id: str | None,
    notification_ids: list[str] | None,
    notification_type: str | None,
    importance: str | None,
    offset: int,
    limit: int,
    list_type: str,
    title: str | None,
    subject: str | None,
    description: str | None,
) -> dict[str, Any]:
    if subaction not in _NOTIFICATION_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for notification. Must be one of: {sorted(_NOTIFICATION_SUBACTIONS)}"
        )

    await gate_destructive_action(
        ctx,
        subaction,
        _NOTIFICATION_DESTRUCTIVE,
        confirm,
        {
            "delete": f"Delete notification **{notification_id}** permanently. This cannot be undone.",
            "delete_archived": "Delete ALL archived notifications permanently. This cannot be undone.",
        },
    )

    if list_type.upper() not in _VALID_LIST_TYPES:
        raise ToolError(
            f"Invalid list_type '{list_type}'. Must be one of: {sorted(_VALID_LIST_TYPES)}"
        )
    if importance is not None and importance.upper() not in _VALID_IMPORTANCE:
        raise ToolError(
            f"Invalid importance '{importance}'. Must be one of: {sorted(_VALID_IMPORTANCE)}"
        )
    if notification_type is not None and notification_type.upper() not in _VALID_NOTIF_TYPES:
        raise ToolError(
            f"Invalid notification_type '{notification_type}'. Must be one of: {sorted(_VALID_NOTIF_TYPES)}"
        )

    with tool_error_handler("notification", subaction, logger):
        logger.info(f"Executing unraid action=notification subaction={subaction}")

        if subaction == "overview":
            data = await make_graphql_request(_NOTIFICATION_QUERIES["overview"])
            return dict((data.get("notifications") or {}).get("overview") or {})

        if subaction == "list":
            filter_vars: dict[str, Any] = {
                "type": list_type.upper(),
                "offset": offset,
                "limit": limit,
            }
            if importance:
                filter_vars["importance"] = importance.upper()
            data = await make_graphql_request(
                _NOTIFICATION_QUERIES["list"], {"filter": filter_vars}
            )
            return {"notifications": (data.get("notifications", {}) or {}).get("list", [])}

        if subaction == "create":
            if title is None or subject is None or description is None or importance is None:
                raise ToolError("create requires title, subject, description, and importance")
            if importance.upper() not in _VALID_IMPORTANCE:
                raise ToolError(
                    f"importance must be one of: {', '.join(sorted(_VALID_IMPORTANCE))}"
                )
            if len(title) > 200:
                raise ToolError(f"title must be at most 200 characters (got {len(title)})")
            if len(subject) > 500:
                raise ToolError(f"subject must be at most 500 characters (got {len(subject)})")
            if len(description) > 2000:
                raise ToolError(
                    f"description must be at most 2000 characters (got {len(description)})"
                )
            data = await make_graphql_request(
                _NOTIFICATION_MUTATIONS["create"],
                {
                    "input": {
                        "title": title,
                        "subject": subject,
                        "description": description,
                        "importance": importance.upper(),
                    }
                },
            )
            notif = data.get("createNotification")
            if notif is None:
                raise ToolError("Notification creation failed: server returned no data")
            return {"success": True, "notification": notif}

        if subaction in ("archive", "mark_unread"):
            if not notification_id:
                raise ToolError(f"notification_id is required for notification/{subaction}")
            data = await make_graphql_request(
                _NOTIFICATION_MUTATIONS[subaction], {"id": notification_id}
            )
            return {"success": True, "subaction": subaction, "data": data}

        if subaction == "delete":
            if not notification_id or not notification_type:
                raise ToolError("delete requires notification_id and notification_type")
            data = await make_graphql_request(
                _NOTIFICATION_MUTATIONS["delete"],
                {"id": notification_id, "type": notification_type.upper()},
            )
            return {"success": True, "subaction": "delete", "data": data}

        if subaction == "delete_archived":
            data = await make_graphql_request(_NOTIFICATION_MUTATIONS["delete_archived"])
            return {"success": True, "subaction": "delete_archived", "data": data}

        if subaction == "archive_all":
            variables: dict[str, Any] | None = (
                {"importance": importance.upper()} if importance else None
            )
            data = await make_graphql_request(_NOTIFICATION_MUTATIONS["archive_all"], variables)
            return {"success": True, "subaction": "archive_all", "data": data}

        if subaction == "archive_many":
            if not notification_ids:
                raise ToolError("notification_ids is required for notification/archive_many")
            data = await make_graphql_request(
                _NOTIFICATION_MUTATIONS["archive_many"], {"ids": notification_ids}
            )
            return {"success": True, "subaction": "archive_many", "data": data}

        if subaction == "unarchive_many":
            if not notification_ids:
                raise ToolError("notification_ids is required for notification/unarchive_many")
            data = await make_graphql_request(
                _NOTIFICATION_MUTATIONS["unarchive_many"], {"ids": notification_ids}
            )
            return {"success": True, "subaction": "unarchive_many", "data": data}

        if subaction == "unarchive_all":
            vars_: dict[str, Any] | None = (
                {"importance": importance.upper()} if importance else None
            )
            data = await make_graphql_request(_NOTIFICATION_MUTATIONS["unarchive_all"], vars_)
            return {"success": True, "subaction": "unarchive_all", "data": data}

        if subaction == "recalculate":
            data = await make_graphql_request(_NOTIFICATION_MUTATIONS["recalculate"])
            return {"success": True, "subaction": "recalculate", "data": data}

        raise ToolError(f"Unhandled notification subaction '{subaction}' — this is a bug")


# ===========================================================================
# KEY (API keys)
# ===========================================================================

_KEY_QUERIES: dict[str, str] = {
    "list": "query ListApiKeys { apiKeys { id name roles permissions { resource actions } createdAt } }",
    "get": "query GetApiKey($id: PrefixedID!) { apiKey(id: $id) { id name roles permissions { resource actions } createdAt } }",
}

_KEY_MUTATIONS: dict[str, str] = {
    "create": "mutation CreateApiKey($input: CreateApiKeyInput!) { apiKey { create(input: $input) { id name key roles } } }",
    "update": "mutation UpdateApiKey($input: UpdateApiKeyInput!) { apiKey { update(input: $input) { id name roles } } }",
    "delete": "mutation DeleteApiKey($input: DeleteApiKeyInput!) { apiKey { delete(input: $input) } }",
    "add_role": "mutation AddRole($input: AddRoleForApiKeyInput!) { apiKey { addRole(input: $input) } }",
    "remove_role": "mutation RemoveRole($input: RemoveRoleFromApiKeyInput!) { apiKey { removeRole(input: $input) } }",
}

_KEY_SUBACTIONS: set[str] = set(_KEY_QUERIES) | set(_KEY_MUTATIONS)
_KEY_DESTRUCTIVE: set[str] = {"delete"}


async def _handle_key(
    subaction: str,
    key_id: str | None,
    name: str | None,
    roles: list[str] | None,
    permissions: list[str] | None,
    ctx: Context | None,
    confirm: bool,
) -> dict[str, Any]:
    if subaction not in _KEY_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for key. Must be one of: {sorted(_KEY_SUBACTIONS)}"
        )

    await gate_destructive_action(
        ctx,
        subaction,
        _KEY_DESTRUCTIVE,
        confirm,
        f"Delete API key **{key_id}**. Any clients using this key will lose access.",
    )

    with tool_error_handler("key", subaction, logger):
        logger.info(f"Executing unraid action=key subaction={subaction}")

        if subaction == "list":
            data = await make_graphql_request(_KEY_QUERIES["list"])
            keys = data.get("apiKeys", [])
            return {"keys": list(keys) if isinstance(keys, list) else []}

        if subaction == "get":
            if not key_id:
                raise ToolError("key_id is required for key/get")
            data = await make_graphql_request(_KEY_QUERIES["get"], {"id": key_id})
            return dict(data.get("apiKey") or {})

        if subaction == "create":
            if not name:
                raise ToolError("name is required for key/create")
            input_data: dict[str, Any] = {"name": name}
            if roles is not None:
                input_data["roles"] = roles
            if permissions is not None:
                input_data["permissions"] = permissions
            data = await make_graphql_request(_KEY_MUTATIONS["create"], {"input": input_data})
            created_key = (data.get("apiKey") or {}).get("create")
            if not created_key:
                raise ToolError("Failed to create API key: no data returned from server")
            return {"success": True, "key": created_key}

        if subaction == "update":
            if not key_id:
                raise ToolError("key_id is required for key/update")
            input_data: dict[str, Any] = {"id": key_id}
            if name:
                input_data["name"] = name
            if roles is not None:
                input_data["roles"] = roles
            data = await make_graphql_request(_KEY_MUTATIONS["update"], {"input": input_data})
            updated_key = (data.get("apiKey") or {}).get("update")
            if not updated_key:
                raise ToolError("Failed to update API key: no data returned from server")
            return {"success": True, "key": updated_key}

        if subaction == "delete":
            if not key_id:
                raise ToolError("key_id is required for key/delete")
            data = await make_graphql_request(
                _KEY_MUTATIONS["delete"], {"input": {"ids": [key_id]}}
            )
            if not (data.get("apiKey") or {}).get("delete"):
                raise ToolError(f"Failed to delete API key '{key_id}': no confirmation from server")
            return {"success": True, "message": f"API key '{key_id}' deleted"}

        if subaction in ("add_role", "remove_role"):
            if not key_id:
                raise ToolError(f"key_id is required for key/{subaction}")
            if not roles or len(roles) == 0:
                raise ToolError(
                    f"roles is required for key/{subaction} (pass as roles=['ROLE_NAME'])"
                )
            data = await make_graphql_request(
                _KEY_MUTATIONS[subaction], {"input": {"apiKeyId": key_id, "role": roles[0]}}
            )
            verb = "added to" if subaction == "add_role" else "removed from"
            return {"success": True, "message": f"Role '{roles[0]}' {verb} key '{key_id}'"}

        raise ToolError(f"Unhandled key subaction '{subaction}' — this is a bug")


# ===========================================================================
# PLUGIN
# ===========================================================================

_PLUGIN_QUERIES: dict[str, str] = {
    "list": "query ListPlugins { plugins { name version hasApiModule hasCliModule } }",
}

_PLUGIN_MUTATIONS: dict[str, str] = {
    "add": "mutation AddPlugin($input: PluginManagementInput!) { addPlugin(input: $input) }",
    "remove": "mutation RemovePlugin($input: PluginManagementInput!) { removePlugin(input: $input) }",
}

_PLUGIN_SUBACTIONS: set[str] = set(_PLUGIN_QUERIES) | set(_PLUGIN_MUTATIONS)
_PLUGIN_DESTRUCTIVE: set[str] = {"remove"}


async def _handle_plugin(
    subaction: str,
    names: list[str] | None,
    bundled: bool,
    restart: bool,
    ctx: Context | None,
    confirm: bool,
) -> dict[str, Any]:
    if subaction not in _PLUGIN_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for plugin. Must be one of: {sorted(_PLUGIN_SUBACTIONS)}"
        )

    await gate_destructive_action(
        ctx,
        subaction,
        _PLUGIN_DESTRUCTIVE,
        confirm,
        f"Remove plugin(s) **{names}** from the Unraid API. This cannot be undone without re-installing.",
    )

    with tool_error_handler("plugin", subaction, logger):
        logger.info(f"Executing unraid action=plugin subaction={subaction}")

        if subaction == "list":
            data = await make_graphql_request(_PLUGIN_QUERIES["list"])
            return {"success": True, "subaction": subaction, "data": data}

        if subaction in ("add", "remove"):
            if not names:
                raise ToolError(f"names is required for plugin/{subaction}")
            data = await make_graphql_request(
                _PLUGIN_MUTATIONS[subaction],
                {"input": {"names": names, "bundled": bundled, "restart": restart}},
            )
            result_key = "addPlugin" if subaction == "add" else "removePlugin"
            return {
                "success": True,
                "subaction": subaction,
                "names": names,
                "manual_restart_required": data.get(result_key),
            }

        raise ToolError(f"Unhandled plugin subaction '{subaction}' — this is a bug")


# ===========================================================================
# RCLONE
# ===========================================================================

_RCLONE_QUERIES: dict[str, str] = {
    "list_remotes": "query ListRCloneRemotes { rclone { remotes { name type parameters config } } }",
    "config_form": "query GetRCloneConfigForm($formOptions: RCloneConfigFormInput) { rclone { configForm(formOptions: $formOptions) { id dataSchema uiSchema } } }",
}

_RCLONE_MUTATIONS: dict[str, str] = {
    "create_remote": "mutation CreateRCloneRemote($input: CreateRCloneRemoteInput!) { rclone { createRCloneRemote(input: $input) { name type parameters } } }",
    "delete_remote": "mutation DeleteRCloneRemote($input: DeleteRCloneRemoteInput!) { rclone { deleteRCloneRemote(input: $input) } }",
}

_RCLONE_SUBACTIONS: set[str] = set(_RCLONE_QUERIES) | set(_RCLONE_MUTATIONS)
_RCLONE_DESTRUCTIVE: set[str] = {"delete_remote"}
_MAX_CONFIG_KEYS = 50
_DANGEROUS_KEY_PATTERN = re.compile(r"\.\.|[/\\;|`$(){}]")
_MAX_VALUE_LENGTH = 4096


def _validate_rclone_config(config_data: dict[str, Any]) -> dict[str, str]:
    if len(config_data) > _MAX_CONFIG_KEYS:
        raise ToolError(f"config_data has {len(config_data)} keys (max {_MAX_CONFIG_KEYS})")
    validated: dict[str, str] = {}
    for key, value in config_data.items():
        if not isinstance(key, str) or not key.strip():
            raise ToolError(
                f"config_data keys must be non-empty strings, got: {type(key).__name__}"
            )
        if _DANGEROUS_KEY_PATTERN.search(key):
            raise ToolError(f"config_data key '{key}' contains disallowed characters")
        if not isinstance(value, (str, int, float, bool)):
            raise ToolError(f"config_data['{key}'] must be a string, number, or boolean")
        str_value = str(value)
        if len(str_value) > _MAX_VALUE_LENGTH:
            raise ToolError(
                f"config_data['{key}'] value exceeds max length ({len(str_value)} > {_MAX_VALUE_LENGTH})"
            )
        validated[key] = str_value
    return validated


async def _handle_rclone(
    subaction: str,
    name: str | None,
    provider_type: str | None,
    config_data: dict[str, Any] | None,
    ctx: Context | None,
    confirm: bool,
) -> dict[str, Any]:
    if subaction not in _RCLONE_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for rclone. Must be one of: {sorted(_RCLONE_SUBACTIONS)}"
        )

    await gate_destructive_action(
        ctx,
        subaction,
        _RCLONE_DESTRUCTIVE,
        confirm,
        f"Delete rclone remote **{name}**. This cannot be undone.",
    )

    with tool_error_handler("rclone", subaction, logger):
        logger.info(f"Executing unraid action=rclone subaction={subaction}")

        if subaction == "list_remotes":
            data = await make_graphql_request(_RCLONE_QUERIES["list_remotes"])
            remotes = data.get("rclone", {}).get("remotes", [])
            return {"remotes": list(remotes) if isinstance(remotes, list) else []}

        if subaction == "config_form":
            variables: dict[str, Any] = {}
            if provider_type:
                variables["formOptions"] = {"providerType": provider_type}
            data = await make_graphql_request(_RCLONE_QUERIES["config_form"], variables or None)
            form = (data.get("rclone") or {}).get("configForm", {})
            if not form:
                raise ToolError("No RClone config form data received")
            return dict(form)

        if subaction == "create_remote":
            if name is None or provider_type is None or config_data is None:
                raise ToolError("create_remote requires name, provider_type, and config_data")
            validated = _validate_rclone_config(config_data)
            data = await make_graphql_request(
                _RCLONE_MUTATIONS["create_remote"],
                {"input": {"name": name, "type": provider_type, "parameters": validated}},
            )
            remote = (data.get("rclone") or {}).get("createRCloneRemote")
            if not remote:
                raise ToolError(f"Failed to create remote '{name}': no confirmation from server")
            return {
                "success": True,
                "message": f"Remote '{name}' created successfully",
                "remote": remote,
            }

        if subaction == "delete_remote":
            if not name:
                raise ToolError("name is required for rclone/delete_remote")
            data = await make_graphql_request(
                _RCLONE_MUTATIONS["delete_remote"], {"input": {"name": name}}
            )
            if not (data.get("rclone") or {}).get("deleteRCloneRemote", False):
                raise ToolError(f"Failed to delete remote '{name}'")
            return {"success": True, "message": f"Remote '{name}' deleted successfully"}

        raise ToolError(f"Unhandled rclone subaction '{subaction}' — this is a bug")


# ===========================================================================
# SETTING
# ===========================================================================

_SETTING_MUTATIONS: dict[str, str] = {
    "update": "mutation UpdateSettings($input: JSON!) { updateSettings(input: $input) { restartRequired values warnings } }",
    "configure_ups": "mutation ConfigureUps($config: UPSConfigInput!) { configureUps(config: $config) }",
}

_SETTING_SUBACTIONS: set[str] = set(_SETTING_MUTATIONS)
_SETTING_DESTRUCTIVE: set[str] = {"configure_ups"}


async def _handle_setting(
    subaction: str,
    settings_input: dict[str, Any] | None,
    ups_config: dict[str, Any] | None,
    ctx: Context | None,
    confirm: bool,
) -> dict[str, Any]:
    if subaction not in _SETTING_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for setting. Must be one of: {sorted(_SETTING_SUBACTIONS)}"
        )

    await gate_destructive_action(
        ctx,
        subaction,
        _SETTING_DESTRUCTIVE,
        confirm,
        "Configure UPS monitoring. This will overwrite the current UPS daemon settings.",
    )

    with tool_error_handler("setting", subaction, logger):
        logger.info(f"Executing unraid action=setting subaction={subaction}")

        if subaction == "update":
            if settings_input is None:
                raise ToolError("settings_input is required for setting/update")
            data = await make_graphql_request(
                _SETTING_MUTATIONS["update"], {"input": settings_input}
            )
            return {"success": True, "subaction": "update", "data": data.get("updateSettings")}

        if subaction == "configure_ups":
            if ups_config is None:
                raise ToolError("ups_config is required for setting/configure_ups")
            data = await make_graphql_request(
                _SETTING_MUTATIONS["configure_ups"], {"config": ups_config}
            )
            return {
                "success": True,
                "subaction": "configure_ups",
                "result": data.get("configureUps"),
            }

        raise ToolError(f"Unhandled setting subaction '{subaction}' — this is a bug")


# ===========================================================================
# CUSTOMIZATION
# ===========================================================================

_CUSTOMIZATION_QUERIES: dict[str, str] = {
    "theme": "query GetCustomization { customization { theme { name showBannerImage showBannerGradient showHeaderDescription headerBackgroundColor headerPrimaryTextColor headerSecondaryTextColor } partnerInfo { partnerName hasPartnerLogo partnerUrl partnerLogoUrl } activationCode { code partnerName serverName sysModel comment header theme } } }",
    "public_theme": "query GetPublicTheme { publicTheme { name showBannerImage showBannerGradient showHeaderDescription headerBackgroundColor headerPrimaryTextColor headerSecondaryTextColor } publicPartnerInfo { partnerName hasPartnerLogo partnerUrl partnerLogoUrl } }",
    "is_initial_setup": "query IsInitialSetup { isInitialSetup }",
    "sso_enabled": "query IsSSOEnabled { isSSOEnabled }",
}

_CUSTOMIZATION_MUTATIONS: dict[str, str] = {
    "set_theme": "mutation SetTheme($theme: ThemeName!) { customization { setTheme(theme: $theme) { name showBannerImage showBannerGradient showHeaderDescription } } }",
}

_CUSTOMIZATION_SUBACTIONS: set[str] = set(_CUSTOMIZATION_QUERIES) | set(_CUSTOMIZATION_MUTATIONS)


async def _handle_customization(subaction: str, theme_name: str | None) -> dict[str, Any]:
    if subaction not in _CUSTOMIZATION_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for customization. Must be one of: {sorted(_CUSTOMIZATION_SUBACTIONS)}"
        )

    with tool_error_handler("customization", subaction, logger):
        logger.info(f"Executing unraid action=customization subaction={subaction}")

        if subaction in _CUSTOMIZATION_QUERIES:
            data = await make_graphql_request(_CUSTOMIZATION_QUERIES[subaction])
            if subaction == "is_initial_setup":
                return {"isInitialSetup": data.get("isInitialSetup")}
            if subaction == "sso_enabled":
                return {"isSSOEnabled": data.get("isSSOEnabled")}
            return dict(data)

        if subaction == "set_theme":
            if not theme_name:
                raise ToolError("theme_name is required for customization/set_theme")
            data = await make_graphql_request(
                _CUSTOMIZATION_MUTATIONS["set_theme"], {"theme": theme_name}
            )
            return {
                "success": True,
                "subaction": "set_theme",
                "data": (data.get("customization") or {}).get("setTheme"),
            }

        raise ToolError(f"Unhandled customization subaction '{subaction}' — this is a bug")


# ===========================================================================
# OIDC
# ===========================================================================

_OIDC_QUERIES: dict[str, str] = {
    "providers": "query GetOidcProviders { oidcProviders { id name clientId issuer authorizationEndpoint tokenEndpoint jwksUri scopes authorizationRules { claim operator value } authorizationRuleMode buttonText buttonIcon buttonVariant buttonStyle } }",
    "provider": "query GetOidcProvider($id: PrefixedID!) { oidcProvider(id: $id) { id name clientId issuer scopes authorizationRules { claim operator value } authorizationRuleMode buttonText buttonIcon } }",
    "configuration": "query GetOidcConfiguration { oidcConfiguration { providers { id name clientId scopes } defaultAllowedOrigins } }",
    "public_providers": "query GetPublicOidcProviders { publicOidcProviders { id name buttonText buttonIcon buttonVariant buttonStyle } }",
    "validate_session": "query ValidateOidcSession($token: String!) { validateOidcSession(token: $token) { valid username } }",
}

_OIDC_SUBACTIONS: set[str] = set(_OIDC_QUERIES)


async def _handle_oidc(
    subaction: str, provider_id: str | None, token: str | None
) -> dict[str, Any]:
    if subaction not in _OIDC_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for oidc. Must be one of: {sorted(_OIDC_SUBACTIONS)}"
        )

    if subaction == "provider" and not provider_id:
        raise ToolError("provider_id is required for oidc/provider")
    if subaction == "validate_session" and not token:
        raise ToolError("token is required for oidc/validate_session")

    variables: dict[str, Any] | None = None
    if subaction == "provider":
        variables = {"id": provider_id}
    elif subaction == "validate_session":
        variables = {"token": token}

    with tool_error_handler("oidc", subaction, logger):
        logger.info(f"Executing unraid action=oidc subaction={subaction}")
        data = await make_graphql_request(_OIDC_QUERIES[subaction], variables)

        if subaction == "providers":
            return {"providers": data.get("oidcProviders", [])}
        if subaction == "provider":
            return dict(data.get("oidcProvider") or {})
        if subaction == "configuration":
            return dict(data.get("oidcConfiguration") or {})
        if subaction == "public_providers":
            return {"providers": data.get("publicOidcProviders", [])}
        if subaction == "validate_session":
            return dict(data.get("validateOidcSession") or {})

        raise ToolError(f"Unhandled oidc subaction '{subaction}' — this is a bug")


# ===========================================================================
# USER
# ===========================================================================

_USER_QUERIES: dict[str, str] = {
    "me": "query GetMe { me { id name description roles } }",
}

_USER_SUBACTIONS: set[str] = set(_USER_QUERIES)


async def _handle_user(subaction: str) -> dict[str, Any]:
    if subaction not in _USER_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for user. Must be one of: {sorted(_USER_SUBACTIONS)}"
        )

    with tool_error_handler("user", subaction, logger):
        logger.info("Executing unraid action=user subaction=me")
        data = await make_graphql_request(_USER_QUERIES["me"])
        return data.get("me") or {}


# ===========================================================================
# LIVE (subscriptions)
# ===========================================================================

_LIVE_ALLOWED_LOG_PREFIXES = ("/var/log/", "/boot/logs/", "/mnt/")


async def _handle_live(
    subaction: str, path: str | None, collect_for: float, timeout: float
) -> dict[str, Any]:
    from ..subscriptions.queries import COLLECT_ACTIONS, EVENT_DRIVEN_ACTIONS, SNAPSHOT_ACTIONS
    from ..subscriptions.snapshot import subscribe_collect, subscribe_once

    all_live = set(SNAPSHOT_ACTIONS) | set(COLLECT_ACTIONS)
    if subaction not in all_live:
        raise ToolError(
            f"Invalid subaction '{subaction}' for live. Must be one of: {sorted(all_live)}"
        )

    if subaction == "log_tail":
        if not path:
            raise ToolError("path is required for live/log_tail")
        normalized = os.path.realpath(path)  # noqa: ASYNC240
        if not any(normalized.startswith(p) for p in _LIVE_ALLOWED_LOG_PREFIXES):
            raise ToolError(f"path must start with one of: {', '.join(_LIVE_ALLOWED_LOG_PREFIXES)}")
        path = normalized

    with tool_error_handler("live", subaction, logger):
        logger.info(f"Executing unraid action=live subaction={subaction} timeout={timeout}")

        if subaction in SNAPSHOT_ACTIONS:
            if subaction in EVENT_DRIVEN_ACTIONS:
                try:
                    data = await subscribe_once(SNAPSHOT_ACTIONS[subaction], timeout=timeout)
                except ToolError as e:
                    if "timed out" in str(e):
                        return {
                            "success": True,
                            "subaction": subaction,
                            "status": "no_recent_events",
                            "message": f"No events received in {timeout:.0f}s — this subscription only emits on state changes",
                        }
                    raise
            else:
                data = await subscribe_once(SNAPSHOT_ACTIONS[subaction], timeout=timeout)
            return {"success": True, "subaction": subaction, "data": data}

        if subaction == "log_tail":
            events = await subscribe_collect(
                COLLECT_ACTIONS["log_tail"],
                variables={"path": path},
                collect_for=collect_for,
                timeout=timeout,
            )
            return {
                "success": True,
                "subaction": subaction,
                "path": path,
                "collect_for": collect_for,
                "event_count": len(events),
                "events": events,
            }

        if subaction == "notification_feed":
            events = await subscribe_collect(
                COLLECT_ACTIONS["notification_feed"], collect_for=collect_for, timeout=timeout
            )
            return {
                "success": True,
                "subaction": subaction,
                "collect_for": collect_for,
                "event_count": len(events),
                "events": events,
            }

        raise ToolError(f"Unhandled live subaction '{subaction}' — this is a bug")


# ===========================================================================
# TOOL REGISTRATION
# ===========================================================================

UNRAID_ACTIONS = Literal[
    "array",
    "customization",
    "disk",
    "docker",
    "health",
    "key",
    "live",
    "notification",
    "oidc",
    "plugin",
    "rclone",
    "setting",
    "system",
    "user",
    "vm",
]


def register_unraid_tool(mcp: FastMCP) -> None:
    """Register the single `unraid` tool with the FastMCP instance."""

    @mcp.tool(timeout=120)
    async def unraid(
        action: UNRAID_ACTIONS,
        subaction: str,
        ctx: Context | None = None,
        confirm: bool = False,
        # system
        device_id: str | None = None,
        # array + disk
        disk_id: str | None = None,
        correct: bool | None = None,
        slot: int | None = None,
        # disk
        log_path: str | None = None,
        tail_lines: int = 100,
        remote_name: str | None = None,
        source_path: str | None = None,
        destination_path: str | None = None,
        backup_options: dict[str, Any] | None = None,
        # docker
        container_id: str | None = None,
        network_id: str | None = None,
        # vm
        vm_id: str | None = None,
        # notification
        notification_id: str | None = None,
        notification_ids: list[str] | None = None,
        notification_type: str | None = None,
        importance: str | None = None,
        offset: int = 0,
        limit: int = 20,
        list_type: str = "UNREAD",
        title: str | None = None,
        subject: str | None = None,
        description: str | None = None,
        # key
        key_id: str | None = None,
        name: str | None = None,
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
        # plugin
        names: list[str] | None = None,
        bundled: bool = False,
        restart: bool = True,
        # rclone
        provider_type: str | None = None,
        config_data: dict[str, Any] | None = None,
        # setting
        settings_input: dict[str, Any] | None = None,
        ups_config: dict[str, Any] | None = None,
        # customization
        theme_name: str | None = None,
        # oidc
        provider_id: str | None = None,
        token: str | None = None,
        # live
        path: str | None = None,
        collect_for: float = 5.0,
        timeout: float = 10.0,
    ) -> dict[str, Any] | str:
        """Interact with an Unraid server's GraphQL API.

        Use action + subaction to select an operation. All params are optional
        except those required by the specific subaction.

        ┌─────────────────┬──────────────────────────────────────────────────────────────────────┐
        │ action          │ subactions                                                           │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ system          │ overview, array, network, registration, variables, metrics,          │
        │                 │ services, display, config, online, owner, settings, server,          │
        │                 │ servers, flash, ups_devices, ups_device, ups_config                  │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ health          │ check, test_connection, diagnose, setup                              │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ array           │ parity_status, parity_history, parity_start, parity_pause,          │
        │                 │ parity_resume, parity_cancel, start_array*, stop_array*,             │
        │                 │ add_disk, remove_disk*, mount_disk, unmount_disk, clear_disk_stats*  │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ disk            │ shares, disks, disk_details, log_files, logs, flash_backup*          │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ docker          │ list, details, start, stop, restart, networks, network_details       │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ vm              │ list, details, start, stop, pause, resume,                           │
        │                 │ force_stop*, reboot, reset*                                          │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ notification    │ overview, list, create, archive, mark_unread, recalculate,           │
        │                 │ archive_all, archive_many, unarchive_many, unarchive_all,            │
        │                 │ delete*, delete_archived*                                            │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ key             │ list, get, create, update, delete*, add_role, remove_role            │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ plugin          │ list, add, remove*                                                   │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ rclone          │ list_remotes, config_form, create_remote, delete_remote*             │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ setting         │ update, configure_ups*                                               │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ customization   │ theme, public_theme, is_initial_setup, sso_enabled, set_theme        │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ oidc            │ providers, provider, configuration, public_providers,                │
        │                 │ validate_session                                                     │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ user            │ me                                                                   │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ live            │ cpu, memory, cpu_telemetry, array_state, parity_progress,            │
        │                 │ ups_status, notifications_overview, owner, server_status,            │
        │                 │ log_tail (requires path=), notification_feed                         │
        └─────────────────┴──────────────────────────────────────────────────────────────────────┘

        * Destructive — requires confirm=True
        """
        if action == "system":
            return await _handle_system(subaction, device_id)

        if action == "health":
            return await _handle_health(subaction, ctx)

        if action == "array":
            return await _handle_array(subaction, disk_id, correct, slot, ctx, confirm)

        if action == "disk":
            return await _handle_disk(
                subaction,
                disk_id,
                log_path,
                tail_lines,
                remote_name,
                source_path,
                destination_path,
                backup_options,
                ctx,
                confirm,
            )

        if action == "docker":
            return await _handle_docker(subaction, container_id, network_id)

        if action == "vm":
            return await _handle_vm(subaction, vm_id, ctx, confirm)

        if action == "notification":
            return await _handle_notification(
                subaction,
                ctx,
                confirm,
                notification_id,
                notification_ids,
                notification_type,
                importance,
                offset,
                limit,
                list_type,
                title,
                subject,
                description,
            )

        if action == "key":
            return await _handle_key(subaction, key_id, name, roles, permissions, ctx, confirm)

        if action == "plugin":
            return await _handle_plugin(subaction, names, bundled, restart, ctx, confirm)

        if action == "rclone":
            return await _handle_rclone(subaction, name, provider_type, config_data, ctx, confirm)

        if action == "setting":
            return await _handle_setting(subaction, settings_input, ups_config, ctx, confirm)

        if action == "customization":
            return await _handle_customization(subaction, theme_name)

        if action == "oidc":
            return await _handle_oidc(subaction, provider_id, token)

        if action == "user":
            return await _handle_user(subaction)

        if action == "live":
            return await _handle_live(subaction, path, collect_for, timeout)

        raise ToolError(
            f"Invalid action '{action}'. Must be one of: {sorted(get_args(UNRAID_ACTIONS))}"
        )

    logger.info("Unraid tool registered successfully")
