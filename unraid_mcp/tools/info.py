"""System information and server status queries.

Provides the `unraid_info` tool with 19 read-only actions for retrieving
system information, array status, network config, and server metadata.
"""

from typing import Any, Literal

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError

# Pre-built queries keyed by action name
QUERIES: dict[str, str] = {
    "overview": """
        query GetSystemInfo {
          info {
            os { platform distro release codename kernel arch hostname codepage logofile serial build uptime }
            cpu { manufacturer brand vendor family model stepping revision voltage speed speedmin speedmax threads cores processors socket cache flags }
            memory {
              layout { bank type clockSpeed formFactor manufacturer partNum serialNum }
            }
            baseboard { manufacturer model version serial assetTag }
            system { manufacturer model version serial uuid sku }
            versions { kernel openssl systemOpenssl systemOpensslLib node v8 npm yarn pm2 gulp grunt git tsc mysql redis mongodb apache nginx php docker postfix postgresql perl python gcc unraid }
            apps { installed started }
            machineId
            time
          }
        }
    """,
    "array": """
        query GetArrayStatus {
          array {
            id
            state
            capacity {
              kilobytes { free used total }
              disks { free used total }
            }
            boot { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
            parities { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
            disks { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
            caches { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
          }
        }
    """,
    "network": """
        query GetNetworkConfig {
          network {
            id
            accessUrls { type name ipv4 ipv6 }
          }
        }
    """,
    "registration": """
        query GetRegistrationInfo {
          registration {
            id type
            keyFile { location }
            state expiration updateExpiration
          }
        }
    """,
    "connect": """
        query GetConnectSettings {
          connect { status sandbox flashGuid }
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
            csrfToken
          }
        }
    """,
    "metrics": """
        query GetMetrics {
          metrics { cpu { used } memory { used total } }
        }
    """,
    "services": """
        query GetServices {
          services { name state }
        }
    """,
    "display": """
        query GetDisplay {
          info { display { theme } }
        }
    """,
    "config": """
        query GetConfig {
          config { valid error }
        }
    """,
    "online": """
        query GetOnline { online }
    """,
    "owner": """
        query GetOwner {
          owner { username avatar url }
        }
    """,
    "settings": """
        query GetSettings {
          settings { unified { values } }
        }
    """,
    "server": """
        query GetServer {
          info {
            os { hostname uptime }
            versions { unraid }
            machineId time
          }
          array { state }
          online
        }
    """,
    "servers": """
        query GetServers {
          servers { id name status description ip port }
        }
    """,
    "flash": """
        query GetFlash {
          flash { id guid product vendor size }
        }
    """,
    "ups_devices": """
        query GetUpsDevices {
          upsDevices { id model status runtime charge load }
        }
    """,
    "ups_device": """
        query GetUpsDevice($id: PrefixedID!) {
          upsDeviceById(id: $id) { id model status runtime charge load voltage frequency temperature }
        }
    """,
    "ups_config": """
        query GetUpsConfig {
          upsConfiguration { enabled mode cable driver port }
        }
    """,
}

INFO_ACTIONS = Literal[
    "overview", "array", "network", "registration", "connect", "variables",
    "metrics", "services", "display", "config", "online", "owner",
    "settings", "server", "servers", "flash",
    "ups_devices", "ups_device", "ups_config",
]


def _process_system_info(raw_info: dict[str, Any]) -> dict[str, Any]:
    """Process raw system info into summary + details."""
    summary: dict[str, Any] = {}
    if raw_info.get("os"):
        os_info = raw_info["os"]
        summary["os"] = (
            f"{os_info.get('distro', '')} {os_info.get('release', '')} "
            f"({os_info.get('platform', '')}, {os_info.get('arch', '')})"
        )
        summary["hostname"] = os_info.get("hostname")
        summary["uptime"] = os_info.get("uptime")

    if raw_info.get("cpu"):
        cpu = raw_info["cpu"]
        summary["cpu"] = (
            f"{cpu.get('manufacturer', '')} {cpu.get('brand', '')} "
            f"({cpu.get('cores')} cores, {cpu.get('threads')} threads)"
        )

    if raw_info.get("memory") and raw_info["memory"].get("layout"):
        mem_layout = raw_info["memory"]["layout"]
        summary["memory_layout_details"] = []
        for stick in mem_layout:
            summary["memory_layout_details"].append(
                f"Bank {stick.get('bank', '?')}: Type {stick.get('type', '?')}, "
                f"Speed {stick.get('clockSpeed', '?')}MHz, "
                f"Manufacturer: {stick.get('manufacturer', '?')}, "
                f"Part: {stick.get('partNum', '?')}"
            )
        summary["memory_summary"] = (
            "Stick layout details retrieved. Overall total/used/free memory stats "
            "are unavailable due to API limitations."
        )
    else:
        summary["memory_summary"] = "Memory information not available."

    return {"summary": summary, "details": raw_info}


def _analyze_disk_health(disks: list[dict[str, Any]]) -> dict[str, int]:
    """Analyze health status of disk arrays."""
    counts = {"healthy": 0, "failed": 0, "missing": 0, "new": 0, "warning": 0, "critical": 0, "unknown": 0}
    for disk in disks:
        status = disk.get("status", "").upper()
        warning = disk.get("warning")
        critical = disk.get("critical")
        if status == "DISK_OK":
            if critical:
                counts["critical"] += 1
            elif warning:
                counts["warning"] += 1
            else:
                counts["healthy"] += 1
        elif status in ("DISK_DSBL", "DISK_INVALID"):
            counts["failed"] += 1
        elif status == "DISK_NP":
            counts["missing"] += 1
        elif status == "DISK_NEW":
            counts["new"] += 1
        else:
            counts["unknown"] += 1
    return counts


def _process_array_status(raw: dict[str, Any]) -> dict[str, Any]:
    """Process raw array data into summary + details."""

    def format_kb(k: Any) -> str:
        if k is None:
            return "N/A"
        k = int(k)
        if k >= 1024 * 1024 * 1024:
            return f"{k / (1024 * 1024 * 1024):.2f} TB"
        if k >= 1024 * 1024:
            return f"{k / (1024 * 1024):.2f} GB"
        if k >= 1024:
            return f"{k / 1024:.2f} MB"
        return f"{k} KB"

    summary: dict[str, Any] = {"state": raw.get("state")}
    if raw.get("capacity") and raw["capacity"].get("kilobytes"):
        kb = raw["capacity"]["kilobytes"]
        summary["capacity_total"] = format_kb(kb.get("total"))
        summary["capacity_used"] = format_kb(kb.get("used"))
        summary["capacity_free"] = format_kb(kb.get("free"))

    summary["num_parity_disks"] = len(raw.get("parities", []))
    summary["num_data_disks"] = len(raw.get("disks", []))
    summary["num_cache_pools"] = len(raw.get("caches", []))

    health_summary: dict[str, Any] = {}
    for key, label in [("parities", "parity_health"), ("disks", "data_health"), ("caches", "cache_health")]:
        if raw.get(key):
            health_summary[label] = _analyze_disk_health(raw[key])

    total_failed = sum(h.get("failed", 0) for h in health_summary.values())
    total_critical = sum(h.get("critical", 0) for h in health_summary.values())
    total_missing = sum(h.get("missing", 0) for h in health_summary.values())
    total_warning = sum(h.get("warning", 0) for h in health_summary.values())

    if total_failed > 0 or total_critical > 0:
        overall = "CRITICAL"
    elif total_missing > 0:
        overall = "DEGRADED"
    elif total_warning > 0:
        overall = "WARNING"
    else:
        overall = "HEALTHY"

    summary["overall_health"] = overall
    summary["health_summary"] = health_summary

    return {"summary": summary, "details": raw}


def register_info_tool(mcp: FastMCP) -> None:
    """Register the unraid_info tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_info(
        action: INFO_ACTIONS,
        device_id: str | None = None,
    ) -> dict[str, Any]:
        """Query Unraid system information.

        Actions:
          overview - OS, CPU, memory, baseboard, versions
          array - Array state, capacity, disk health
          network - Access URLs, interfaces
          registration - License type, state, expiration
          connect - Unraid Connect settings
          variables - System variables and configuration
          metrics - CPU and memory utilization
          services - Running services
          display - Theme settings
          config - Configuration validity
          online - Server online status
          owner - Server owner info
          settings - All unified settings
          server - Quick server summary
          servers - Connected servers list
          flash - Flash drive info
          ups_devices - List UPS devices
          ups_device - Single UPS device (requires device_id)
          ups_config - UPS configuration
        """
        if action not in QUERIES:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {list(QUERIES.keys())}")

        if action == "ups_device" and not device_id:
            raise ToolError("device_id is required for ups_device action")

        query = QUERIES[action]
        variables: dict[str, Any] | None = None
        if action == "ups_device":
            variables = {"id": device_id}

        try:
            logger.info(f"Executing unraid_info action={action}")
            data = await make_graphql_request(query, variables)

            # Action-specific response processing
            if action == "overview":
                raw = data.get("info", {})
                if not raw:
                    raise ToolError("No system info returned from Unraid API")
                return _process_system_info(raw)

            if action == "array":
                raw = data.get("array", {})
                if not raw:
                    raise ToolError("No array information returned from Unraid API")
                return _process_array_status(raw)

            if action == "network":
                return dict(data.get("network", {}))

            if action == "registration":
                return dict(data.get("registration", {}))

            if action == "connect":
                return dict(data.get("connect", {}))

            if action == "variables":
                return dict(data.get("vars", {}))

            if action == "metrics":
                return dict(data.get("metrics", {}))

            if action == "services":
                services = data.get("services", [])
                return {"services": list(services) if isinstance(services, list) else []}

            if action == "display":
                info = data.get("info", {})
                return dict(info.get("display", {}))

            if action == "config":
                return dict(data.get("config", {}))

            if action == "online":
                return {"online": data.get("online")}

            if action == "owner":
                return dict(data.get("owner", {}))

            if action == "settings":
                settings = data.get("settings", {})
                if settings and settings.get("unified"):
                    values = settings["unified"].get("values", {})
                    return dict(values) if isinstance(values, dict) else {"raw": values}
                return {}

            if action == "server":
                return data

            if action == "servers":
                servers = data.get("servers", [])
                return {"servers": list(servers) if isinstance(servers, list) else []}

            if action == "flash":
                return dict(data.get("flash", {}))

            if action == "ups_devices":
                devices = data.get("upsDevices", [])
                return {"ups_devices": list(devices) if isinstance(devices, list) else []}

            if action == "ups_device":
                return dict(data.get("upsDeviceById", {}))

            if action == "ups_config":
                return dict(data.get("upsConfiguration", {}))

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in unraid_info action={action}: {e}", exc_info=True)
            raise ToolError(f"Failed to execute info/{action}: {str(e)}") from e

    logger.info("Info tool registered successfully")
