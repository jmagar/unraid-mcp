"""System domain handler for the Unraid MCP tool.

Covers: overview, array, network, registration, variables, metrics, services,
display, config, online, owner, settings, server, servers, flash, ups_devices,
ups_device, ups_config, server_time, timezones (20 subactions).
"""

from typing import Any

from ..config.logging import logger
from ..core import client as _client
from ..core.exceptions import ToolError, tool_error_handler
from ..core.utils import format_kb, safe_get, validate_subaction


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
    "ups_device": "query GetUpsDevice($id: String!) { upsDeviceById(id: $id) { id name model status battery { chargeLevel estimatedRuntime health } power { loadPercentage inputVoltage outputVoltage } } }",
    "ups_config": "query GetUpsConfig { upsConfiguration { service upsCable upsType device batteryLevel minutes timeout killUps upsName } }",
    "server_time": "query GetSystemTime { systemTime { currentTime timeZone useNtp ntpServers } }",
    "timezones": "query GetTimeZones { timeZoneOptions { value label } }",
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
    validate_subaction(subaction, _SYSTEM_SUBACTIONS, "system")

    if subaction == "ups_device" and not device_id:
        raise ToolError("device_id is required for system/ups_device")

    query = _SYSTEM_QUERIES[subaction]
    variables: dict[str, Any] | None = {"id": device_id} if subaction == "ups_device" else None

    with tool_error_handler("system", subaction, logger):
        logger.info(f"Executing unraid action=system subaction={subaction}")
        data = await _client.make_graphql_request(query, variables)

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
            return dict(safe_get(data, "info", "display", default={}))
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

        if subaction == "ups_device":
            result = data.get("upsDeviceById")
            if result is None:
                raise ToolError(f"UPS device '{device_id}' not found")
            return dict(result)

        simple_dict = {
            "registration": "registration",
            "variables": "vars",
            "metrics": "metrics",
            "config": "config",
            "owner": "owner",
            "flash": "flash",
            "ups_config": "upsConfiguration",
            "server_time": "systemTime",
        }
        if subaction in simple_dict:
            result = data.get(simple_dict[subaction])
            if result is None:
                if subaction == "registration":
                    raise ToolError(
                        "No registration data returned — server may be unlicensed or API unavailable"
                    )
                logger.warning("system/%s returned null from API", subaction)
                return {}
            return dict(result)

        list_actions = {
            "services": ("services", "services"),
            "servers": ("servers", "servers"),
            "ups_devices": ("upsDevices", "ups_devices"),
            "timezones": ("timeZoneOptions", "timezones"),
        }
        if subaction in list_actions:
            response_key, output_key = list_actions[subaction]
            items = data.get(response_key) or []
            return {output_key: list(items) if isinstance(items, list) else []}

        raise ToolError(f"Unhandled system subaction '{subaction}' — this is a bug")
