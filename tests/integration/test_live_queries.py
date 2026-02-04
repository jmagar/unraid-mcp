#!/usr/bin/env python3
"""Live API test: fires every GraphQL query from the codebase against the Unraid server."""

import asyncio
import sys
import time
from pathlib import Path

import httpx

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Now import from the application config
try:
    from unraid_mcp.config.settings import (
        UNRAID_API_KEY,
        UNRAID_API_URL,
        UNRAID_VERIFY_SSL,
    )
except ImportError:
    # Fallback or error if not found (e.g. if not installed as package)
    print(
        "Error: Could not import unraid_mcp.config.settings. Ensure project root is in PYTHONPATH."
    )
    sys.exit(1)

API_URL = UNRAID_API_URL

if not API_URL:
    print("WARNING: UNRAID_API_URL is not set. Skipping integration tests.")
    sys.exit(0)
API_KEY = UNRAID_API_KEY

if not API_KEY:
    # Fail loudly if API_KEY is missing, to prevent accidental commits of secrets
    # or running without proper configuration.
    raise ValueError(
        "UNRAID_API_KEY environment variable is required (check .env file or export UNRAID_API_KEY='...')"
    )

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY,
    "User-Agent": "UnraidMCPServer/0.1.0",
}

# Queries that fail due to confirmed Unraid API server-side bugs.
# These are reported separately and don't count as test failures.
KNOWN_SERVER_ISSUES = {
    "rclone/get_rclone_config_form": "INTERNAL_SERVER_ERROR: configForm resolver fails with 'url must not start with a slash'",
}

# Queries that return errors because the feature is unavailable on the server
# (e.g. VMs not enabled). Valid queries, just no data.
KNOWN_UNAVAILABLE = {
    "vm/list_vms",
    "vm/get_vm_details_both_fields",
}

TESTS = [
    (
        "system/get_system_info",
        """query GetSystemInfo {
      info {
        os { platform distro release codename kernel arch hostname logofile serial build uptime }
        cpu { manufacturer brand vendor family model stepping revision voltage speed speedmin speedmax threads cores processors socket cache flags }
        memory { layout { bank type clockSpeed formFactor manufacturer partNum serialNum } }
        baseboard { manufacturer model version serial assetTag }
        system { manufacturer model version serial uuid sku }
        versions {
          core { unraid api kernel }
          packages { openssl node npm pm2 git nginx php docker }
        }
        machineId
        time
      }
    }""",
        None,
    ),
    (
        "system/get_array_status",
        """query GetArrayStatus {
      array {
        id state
        capacity { kilobytes { free used total } disks { free used total } }
        boot { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
        parities { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
        disks { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
        caches { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
      }
    }""",
        None,
    ),
    (
        "system/get_network_config",
        """query GetNetworkConfig {
      network { id accessUrls { type name ipv4 ipv6 } }
    }""",
        None,
    ),
    (
        "system/get_registration_info",
        """query GetRegistrationInfo {
      registration { id type keyFile { location contents } state expiration updateExpiration }
    }""",
        None,
    ),
    (
        "system/get_connect_settings",
        """query GetConnectSettingsForm {
      settings { unified { values } }
    }""",
        None,
    ),
    (
        "system/get_unraid_variables",
        """query GetSelectiveUnraidVariables {
      vars {
        id version name timeZone comment security workgroup domain domainShort
        hideDotFiles localMaster enableFruit useNtp domainLogin sysModel
        sysFlashSlots useSsl port portssl localTld bindMgt useTelnet porttelnet
        useSsh portssh startPage startArray shutdownTimeout
        shareSmbEnabled shareNfsEnabled shareAfpEnabled shareCacheEnabled
        shareAvahiEnabled safeMode startMode configValid configError
        joinStatus deviceCount flashGuid flashProduct flashVendor
        mdState mdVersion shareCount shareSmbCount shareNfsCount shareAfpCount
        shareMoverActive csrfToken
      }
    }""",
        None,
    ),
    (
        "storage/get_shares_info",
        """query GetSharesInfo {
      shares { id name free used size include exclude cache nameOrig comment allocator splitLevel floor cow color luksStatus }
    }""",
        None,
    ),
    (
        "storage/get_notifications_overview",
        """query GetNotificationsOverview {
      notifications { overview { unread { info warning alert total } archive { info warning alert total } } }
    }""",
        None,
    ),
    (
        "storage/list_notifications",
        """query ListNotifications($filter: NotificationFilter!) {
      notifications { list(filter: $filter) { id title subject description importance link type timestamp formattedTimestamp } }
    }""",
        {"filter": {"type": "UNREAD", "offset": 0, "limit": 5}},
    ),
    (
        "storage/list_available_log_files",
        """query ListLogFiles {
      logFiles { name path size modifiedAt }
    }""",
        None,
    ),
    (
        "storage/list_physical_disks",
        """query ListPhysicalDisksMinimal {
      disks { id device name }
    }""",
        None,
    ),
    (
        "docker/list_docker_containers",
        """query ListDockerContainers {
      docker { containers(skipCache: false) { id names image state status autoStart } }
    }""",
        None,
    ),
    (
        "docker/container_detail_fields",
        """query GetAllContainerDetailsForFiltering {
      docker { containers(skipCache: false) {
        id names image imageId command created
        ports { ip privatePort publicPort type }
        sizeRootFs labels state status
        hostConfig { networkMode }
        networkSettings mounts autoStart
      } }
    }""",
        None,
    ),
    (
        "vm/list_vms",
        """query ListVMs {
      vms { id domains { id name state uuid } }
    }""",
        None,
    ),
    (
        "vm/get_vm_details_both_fields",
        """query GetVmDetails {
      vms { domains { id name state uuid } domain { id name state uuid } }
    }""",
        None,
    ),
    (
        "rclone/list_rclone_remotes",
        """query ListRCloneRemotes {
      rclone { remotes { name type parameters config } }
    }""",
        None,
    ),
    (
        "rclone/get_rclone_config_form",
        """query GetRCloneConfigForm($formOptions: RCloneConfigFormInput) {
      rclone { configForm(formOptions: $formOptions) { id dataSchema uiSchema } }
    }""",
        None,
    ),
    (
        "health/health_check",
        """query ComprehensiveHealthCheck {
      info { machineId time versions { core { unraid } } os { uptime } }
      array { state }
      notifications { overview { unread { alert warning total } } }
      docker { containers(skipCache: true) { id state status } }
    }""",
        None,
    ),
]


async def run_tests():
    results = []
    # SSL verification can be toggled via env var (default False for local testing)
    verify_ssl = UNRAID_VERIFY_SSL
    async with httpx.AsyncClient(verify=verify_ssl, follow_redirects=False) as client:
        for name, query, variables in TESTS:
            payload = {"query": query}
            if variables:
                payload["variables"] = variables

            start = time.time()
            try:
                r = await client.post(API_URL, json=payload, headers=HEADERS, timeout=30.0)
                elapsed = round((time.time() - start) * 1000)

                if r.status_code != 200:
                    results.append((name, "HTTP_ERROR", f"Status {r.status_code}", elapsed))
                    continue

                try:
                    data = r.json()
                except ValueError:
                    # Catch JSONDecodeError (subclass of ValueError) if response is not valid JSON
                    results.append(
                        (
                            name,
                            "JSON_ERR",
                            f"Invalid JSON (status {r.status_code}): {r.text[:100]}",
                            elapsed,
                        )
                    )
                    continue
                if "errors" in data and data["errors"]:
                    err_msgs = "; ".join(e.get("message", str(e))[:120] for e in data["errors"])
                    _data_content = data.get("data")
                    has_data = bool(
                        isinstance(_data_content, dict)
                        and any(v is not None for v in _data_content.values())
                    )
                    if name in KNOWN_SERVER_ISSUES:
                        status = "KNOWN_BUG"
                    elif name in KNOWN_UNAVAILABLE:
                        status = "UNAVAIL"
                    elif has_data:
                        status = "PARTIAL"
                    else:
                        status = "GQL_ERROR"
                    results.append((name, status, err_msgs, elapsed))
                else:
                    results.append((name, "OK", "", elapsed))
            except Exception as e:
                elapsed = round((time.time() - start) * 1000)
                results.append((name, "EXCEPTION", str(e)[:120], elapsed))

    # Print results
    STATUS_ICONS = {
        "OK": "  OK",
        "PARTIAL": "WARN",
        "UNAVAIL": "SKIP",
        "KNOWN_BUG": " BUG",
        "GQL_ERROR": "FAIL",
        "HTTP_ERROR": "FAIL",
        "EXCEPTION": "FAIL",
        "JSON_ERR": "FAIL",
    }
    print(f"{'Tool':<42} {'Status':<12} {'Time':>6}  Detail")
    print("-" * 130)
    for name, status, err, elapsed in results:
        icon = STATUS_ICONS.get(status, "FAIL")
        if status == "KNOWN_BUG":
            detail = KNOWN_SERVER_ISSUES.get(name, err)[:70]
        elif status == "UNAVAIL":
            detail = "Feature unavailable on server"
        else:
            detail = err[:70] if err else ""
        print(f"{name:<42} {icon:<12} {elapsed:>5}ms  {detail}")

    ok = sum(1 for _, s, _, _ in results if s == "OK")
    unavail = sum(1 for _, s, _, _ in results if s == "UNAVAIL")
    known = sum(1 for _, s, _, _ in results if s == "KNOWN_BUG")
    partial = sum(1 for _, s, _, _ in results if s == "PARTIAL")
    fail = sum(
        1 for _, s, _, _ in results if s in ("GQL_ERROR", "HTTP_ERROR", "EXCEPTION", "JSON_ERR")
    )
    print(
        f"\nTotal: {len(results)} | OK: {ok} | Unavailable: {unavail} | Known bugs: {known} | Partial: {partial} | Failed: {fail}"
    )

    # Print details only for unexpected failures
    failures = [
        (n, s, e)
        for n, s, e, _ in results
        if s in ("GQL_ERROR", "HTTP_ERROR", "EXCEPTION", "PARTIAL", "JSON_ERR")
    ]
    if failures:
        print("\n=== UNEXPECTED FAILURES ===")
        for name, status, err in failures:
            print(f"\n{name} [{status}]:")
            print(f"  {err}")
    else:
        print("\nNo unexpected failures.")

    return len(failures)


if __name__ == "__main__":
    sys.exit(asyncio.run(run_tests()))
