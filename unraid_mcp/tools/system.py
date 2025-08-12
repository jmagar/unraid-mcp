"""System information and array status tools.

This module provides tools for retrieving core Unraid system information,
array status with health analysis, network configuration, registration info,
and system variables.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError


# Standalone functions for use by subscription resources
async def _get_system_info() -> dict[str, Any]:
    """Standalone function to get system info - used by subscriptions and tools."""
    query = """
    query GetSystemInfo {
      info {
        os { platform distro release codename kernel arch hostname codepage logofile serial build uptime }
        cpu { manufacturer brand vendor family model stepping revision voltage speed speedmin speedmax threads cores processors socket cache flags }
        memory {
          # Avoid fetching problematic fields that cause type errors
          layout { bank type clockSpeed formFactor manufacturer partNum serialNum }
        }
        baseboard { manufacturer model version serial assetTag }
        system { manufacturer model version serial uuid sku }
        versions { kernel openssl systemOpenssl systemOpensslLib node v8 npm yarn pm2 gulp grunt git tsc mysql redis mongodb apache nginx php docker postfix postgresql perl python gcc unraid }
        apps { installed started }
        # Remove devices section as it has non-nullable fields that might be null
        machineId
        time
      }
    }
    """
    try:
        logger.info("Executing get_system_info")
        response_data = await make_graphql_request(query)
        raw_info = response_data.get("info", {})
        if not raw_info:
            raise ToolError("No system info returned from Unraid API")

        # Process for human-readable output
        summary: dict[str, Any] = {}
        if raw_info.get('os'):
            os_info = raw_info['os']
            summary['os'] = f"{os_info.get('distro', '')} {os_info.get('release', '')} ({os_info.get('platform', '')}, {os_info.get('arch', '')})"
            summary['hostname'] = os_info.get('hostname')
            summary['uptime'] = os_info.get('uptime')

        if raw_info.get('cpu'):
            cpu_info = raw_info['cpu']
            summary['cpu'] = f"{cpu_info.get('manufacturer', '')} {cpu_info.get('brand', '')} ({cpu_info.get('cores')} cores, {cpu_info.get('threads')} threads)"

        if raw_info.get('memory') and raw_info['memory'].get('layout'):
            mem_layout = raw_info['memory']['layout']
            summary['memory_layout_details'] = []  # Renamed for clarity
            # The API is not returning 'size' for individual sticks in the layout, even if queried.
            # So, we cannot calculate total from layout currently.
            for stick in mem_layout:
                # stick_size = stick.get('size') # This is None in the actual API response
                summary['memory_layout_details'].append(
                    f"Bank {stick.get('bank', '?')}: Type {stick.get('type', '?')}, Speed {stick.get('clockSpeed', '?')}MHz, Manufacturer: {stick.get('manufacturer','?')}, Part: {stick.get('partNum', '?')}"
                )
            summary['memory_summary'] = "Stick layout details retrieved. Overall total/used/free memory stats are unavailable due to API limitations (Int overflow or data not provided by API)."
        else:
            summary['memory_summary'] = "Memory information (layout or stats) not available or failed to retrieve."

        # Include a key for the full details if needed by an LLM for deeper dives
        return {"summary": summary, "details": raw_info}

    except Exception as e:
        logger.error(f"Error in get_system_info: {e}", exc_info=True)
        raise ToolError(f"Failed to retrieve system information: {str(e)}") from e


async def _get_array_status() -> dict[str, Any]:
    """Standalone function to get array status - used by subscriptions and tools."""
    query = """
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
    """
    try:
        logger.info("Executing get_array_status")
        response_data = await make_graphql_request(query)
        raw_array_info = response_data.get("array", {})
        if not raw_array_info:
            raise ToolError("No array information returned from Unraid API")

        summary: dict[str, Any] = {}
        summary['state'] = raw_array_info.get('state')

        if raw_array_info.get('capacity') and raw_array_info['capacity'].get('kilobytes'):
            kb_cap = raw_array_info['capacity']['kilobytes']
            # Helper to format KB into TB/GB/MB
            def format_kb(k: Any) -> str:
                if k is None:
                    return "N/A"
                k = int(k) # Values are strings in SDL for PrefixedID containing types like capacity
                if k >= 1024*1024*1024:
                    return f"{k / (1024*1024*1024):.2f} TB"
                if k >= 1024*1024:
                    return f"{k / (1024*1024):.2f} GB"
                if k >= 1024:
                    return f"{k / 1024:.2f} MB"
                return f"{k} KB"

            summary['capacity_total'] = format_kb(kb_cap.get('total'))
            summary['capacity_used'] = format_kb(kb_cap.get('used'))
            summary['capacity_free'] = format_kb(kb_cap.get('free'))

        summary['num_parity_disks'] = len(raw_array_info.get('parities', []))
        summary['num_data_disks'] = len(raw_array_info.get('disks', []))
        summary['num_cache_pools'] = len(raw_array_info.get('caches', [])) # Note: caches are pools, not individual cache disks

        # Enhanced: Add disk health summary
        def analyze_disk_health(disks: list[dict[str, Any]], disk_type: str) -> dict[str, int]:
            """Analyze health status of disk arrays"""
            if not disks:
                return {}

            health_counts = {
                'healthy': 0,
                'failed': 0,
                'missing': 0,
                'new': 0,
                'warning': 0,
                'unknown': 0
            }

            for disk in disks:
                status = disk.get('status', '').upper()
                warning = disk.get('warning')
                critical = disk.get('critical')

                if status == 'DISK_OK':
                    if warning or critical:
                        health_counts['warning'] += 1
                    else:
                        health_counts['healthy'] += 1
                elif status in ['DISK_DSBL', 'DISK_INVALID']:
                    health_counts['failed'] += 1
                elif status == 'DISK_NP':
                    health_counts['missing'] += 1
                elif status == 'DISK_NEW':
                    health_counts['new'] += 1
                else:
                    health_counts['unknown'] += 1

            return health_counts

        # Analyze health for each disk type
        health_summary = {}
        if raw_array_info.get('parities'):
            health_summary['parity_health'] = analyze_disk_health(raw_array_info['parities'], 'parity')
        if raw_array_info.get('disks'):
            health_summary['data_health'] = analyze_disk_health(raw_array_info['disks'], 'data')
        if raw_array_info.get('caches'):
            health_summary['cache_health'] = analyze_disk_health(raw_array_info['caches'], 'cache')

        # Overall array health assessment
        total_failed = sum(h.get('failed', 0) for h in health_summary.values())
        total_missing = sum(h.get('missing', 0) for h in health_summary.values())
        total_warning = sum(h.get('warning', 0) for h in health_summary.values())

        if total_failed > 0:
            overall_health = "CRITICAL"
        elif total_missing > 0:
            overall_health = "DEGRADED"
        elif total_warning > 0:
            overall_health = "WARNING"
        else:
            overall_health = "HEALTHY"

        summary['overall_health'] = overall_health
        summary['health_summary'] = health_summary

        return {"summary": summary, "details": raw_array_info}

    except Exception as e:
        logger.error(f"Error in get_array_status: {e}", exc_info=True)
        raise ToolError(f"Failed to retrieve array status: {str(e)}") from e


def register_system_tools(mcp: FastMCP) -> None:
    """Register all system tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    async def get_system_info() -> dict[str, Any]:
        """Retrieves comprehensive information about the Unraid system, OS, CPU, memory, and baseboard."""
        return await _get_system_info()

    @mcp.tool()
    async def get_array_status() -> dict[str, Any]:
        """Retrieves the current status of the Unraid storage array, including its state, capacity, and details of all disks."""
        return await _get_array_status()

    @mcp.tool()
    async def get_network_config() -> dict[str, Any]:
        """Retrieves network configuration details, including access URLs."""
        query = """
        query GetNetworkConfig {
          network {
            id
            accessUrls { type name ipv4 ipv6 }
          }
        }
        """
        try:
            logger.info("Executing get_network_config tool")
            response_data = await make_graphql_request(query)
            network = response_data.get("network", {})
            return dict(network) if isinstance(network, dict) else {}
        except Exception as e:
            logger.error(f"Error in get_network_config: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve network configuration: {str(e)}") from e

    @mcp.tool()
    async def get_registration_info() -> dict[str, Any]:
        """Retrieves Unraid registration details."""
        query = """
        query GetRegistrationInfo {
          registration {
            id
            type
            keyFile { location contents }
            state
            expiration
            updateExpiration
          }
        }
        """
        try:
            logger.info("Executing get_registration_info tool")
            response_data = await make_graphql_request(query)
            registration = response_data.get("registration", {})
            return dict(registration) if isinstance(registration, dict) else {}
        except Exception as e:
            logger.error(f"Error in get_registration_info: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve registration information: {str(e)}") from e

    @mcp.tool()
    async def get_connect_settings() -> dict[str, Any]:
        """Retrieves settings related to Unraid Connect."""
        # Based on actual schema: settings.unified.values contains the JSON settings
        query = """
        query GetConnectSettingsForm {
          settings {
            unified {
              values
            }
          }
        }
        """
        try:
            logger.info("Executing get_connect_settings tool")
            response_data = await make_graphql_request(query)

            # Navigate down to the unified settings values
            if response_data.get("settings") and response_data["settings"].get("unified"):
                values = response_data["settings"]["unified"].get("values", {})
                # Filter for Connect-related settings if values is a dict
                if isinstance(values, dict):
                    # Look for connect-related keys in the unified settings
                    connect_settings = {}
                    for key, value in values.items():
                        if 'connect' in key.lower() or key in ['accessType', 'forwardType', 'port']:
                            connect_settings[key] = value
                    return connect_settings if connect_settings else values
                return dict(values) if isinstance(values, dict) else {}
            return {}
        except Exception as e:
            logger.error(f"Error in get_connect_settings: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve Unraid Connect settings: {str(e)}") from e

    @mcp.tool()
    async def get_unraid_variables() -> dict[str, Any]:
        """Retrieves a selection of Unraid system variables and settings.
           Note: Many variables are omitted due to API type issues (Int overflow/NaN).
        """
        # Querying a smaller, curated set of fields to avoid Int overflow and NaN issues
        # pending Unraid API schema fixes for the full Vars type.
        query = """
        query GetSelectiveUnraidVariables {
          vars {
            id
            version
            name
            timeZone
            comment
            security
            workgroup
            domain
            domainShort
            hideDotFiles
            localMaster
            enableFruit
            useNtp
            # ntpServer1, ntpServer2, ... are strings, should be okay but numerous
            domainLogin # Boolean
            sysModel # String
            # sysArraySlots, sysCacheSlots are Int, were problematic (NaN)
            sysFlashSlots # Int, might be okay if small and always set
            useSsl # Boolean
            port # Int, usually small
            portssl # Int, usually small
            localTld # String
            bindMgt # Boolean
            useTelnet # Boolean
            porttelnet # Int, usually small
            useSsh # Boolean
            portssh # Int, usually small
            startPage # String
            startArray # Boolean
            # spindownDelay, queueDepth are Int, potentially okay if always set
            # defaultFormat, defaultFsType are String
            shutdownTimeout # Int, potentially okay
            # luksKeyfile is String
            # pollAttributes, pollAttributesDefault, pollAttributesStatus are Int/String, were problematic (NaN or type)
            # nrRequests, nrRequestsDefault, nrRequestsStatus were problematic
            # mdNumStripes, mdNumStripesDefault, mdNumStripesStatus were problematic
            # mdSyncWindow, mdSyncWindowDefault, mdSyncWindowStatus were problematic
            # mdSyncThresh, mdSyncThreshDefault, mdSyncThreshStatus were problematic
            # mdWriteMethod, mdWriteMethodDefault, mdWriteMethodStatus were problematic
            # shareDisk, shareUser, shareUserInclude, shareUserExclude are String arrays/String
            shareSmbEnabled # Boolean
            shareNfsEnabled # Boolean
            shareAfpEnabled # Boolean
            # shareInitialOwner, shareInitialGroup are String
            shareCacheEnabled # Boolean
            # shareCacheFloor is String (numeric string?)
            # shareMoverSchedule, shareMoverLogging are String
            # fuseRemember, fuseRememberDefault, fuseRememberStatus are String/Boolean, were problematic
            # fuseDirectio, fuseDirectioDefault, fuseDirectioStatus are String/Boolean, were problematic
            shareAvahiEnabled # Boolean
            # shareAvahiSmbName, shareAvahiSmbModel, shareAvahiAfpName, shareAvahiAfpModel are String
            safeMode # Boolean
            startMode # String
            configValid # Boolean
            configError # String
            joinStatus # String
            deviceCount # Int, might be okay
            flashGuid # String
            flashProduct # String
            flashVendor # String
            # regCheck, regFile, regGuid, regTy, regState, regTo, regTm, regTm2, regGen are varied, mostly String/Int
            # sbName, sbVersion, sbUpdated, sbEvents, sbState, sbClean, sbSynced, sbSyncErrs, sbSynced2, sbSyncExit are varied
            # mdColor, mdNumDisks, mdNumDisabled, mdNumInvalid, mdNumMissing, mdNumNew, mdNumErased are Int, potentially okay if counts
            # mdResync, mdResyncCorr, mdResyncPos, mdResyncDb, mdResyncDt, mdResyncAction are varied (Int/Boolean/String)
            # mdResyncSize was an overflow
            mdState # String (enum)
            mdVersion # String
            # cacheNumDevices, cacheSbNumDisks were problematic (NaN)
            # fsState, fsProgress, fsCopyPrcnt, fsNumMounted, fsNumUnmountable, fsUnmountableMask are varied
            shareCount # Int, might be okay
            shareSmbCount # Int, might be okay
            shareNfsCount # Int, might be okay
            shareAfpCount # Int, might be okay
            shareMoverActive # Boolean
            csrfToken # String
          }
        }
        """
        try:
            logger.info("Executing get_unraid_variables tool with a selective query")
            response_data = await make_graphql_request(query)
            vars_data = response_data.get("vars", {})
            return dict(vars_data) if isinstance(vars_data, dict) else {}
        except Exception as e:
            logger.error(f"Error in get_unraid_variables: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve Unraid variables: {str(e)}") from e

    logger.info("System tools registered successfully")
