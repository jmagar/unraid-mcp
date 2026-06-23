"""Complete GraphQL operation inventory used by schema contract tests."""

from collections.abc import Iterable

from unraid_mcp.tools._array import _ARRAY_MUTATIONS, _ARRAY_QUERIES
from unraid_mcp.tools._connect import _CONNECT_MUTATIONS, _CONNECT_QUERIES
from unraid_mcp.tools._customization import _CUSTOMIZATION_MUTATIONS, _CUSTOMIZATION_QUERIES
from unraid_mcp.tools._disk import _DISK_MUTATIONS, _DISK_QUERIES
from unraid_mcp.tools._docker import (
    _DOCKER_BULK_MUTATIONS,
    _DOCKER_MUTATIONS,
    _DOCKER_ORGANIZER,
    _DOCKER_QUERIES,
    _DOCKER_ROOT_MUTATIONS,
)
from unraid_mcp.tools._health import _HEALTH_QUERIES
from unraid_mcp.tools._key import _KEY_MUTATIONS, _KEY_QUERIES
from unraid_mcp.tools._notification import _NOTIFICATION_MUTATIONS, _NOTIFICATION_QUERIES
from unraid_mcp.tools._oidc import _OIDC_QUERIES
from unraid_mcp.tools._onboarding import (
    _ONBOARDING_INPUT_MUTATIONS,
    _ONBOARDING_QUERIES,
    _ONBOARDING_SIMPLE_MUTATIONS,
)
from unraid_mcp.tools._plugin import _PLUGIN_MUTATIONS, _PLUGIN_QUERIES
from unraid_mcp.tools._rclone import _RCLONE_MUTATIONS, _RCLONE_QUERIES
from unraid_mcp.tools._setting import _SETTING_MUTATIONS
from unraid_mcp.tools._system import _SYSTEM_QUERIES
from unraid_mcp.tools._user import _USER_QUERIES
from unraid_mcp.tools._vm import _VM_MUTATIONS, _VM_QUERIES


def operation_dicts() -> Iterable[tuple[str, dict[str, str]]]:
    docker_organizer = {name: spec["mutation"] for name, spec in _DOCKER_ORGANIZER.items()}
    return (
        ("system", _SYSTEM_QUERIES),
        ("health", {"check": _HEALTH_QUERIES["comprehensive_health"]}),
        ("array", _ARRAY_QUERIES),
        ("array", _ARRAY_MUTATIONS),
        ("disk", _DISK_QUERIES),
        ("disk", _DISK_MUTATIONS),
        ("docker", _DOCKER_QUERIES),
        ("docker", _DOCKER_MUTATIONS),
        ("docker", _DOCKER_BULK_MUTATIONS),
        ("docker", _DOCKER_ROOT_MUTATIONS),
        ("docker", docker_organizer),
        ("vm", _VM_QUERIES),
        ("vm", _VM_MUTATIONS),
        ("notification", _NOTIFICATION_QUERIES),
        ("notification", _NOTIFICATION_MUTATIONS),
        ("rclone", _RCLONE_QUERIES),
        ("rclone", _RCLONE_MUTATIONS),
        ("user", _USER_QUERIES),
        ("key", _KEY_QUERIES),
        ("key", _KEY_MUTATIONS),
        ("setting", _SETTING_MUTATIONS),
        ("connect", _CONNECT_QUERIES),
        ("connect", _CONNECT_MUTATIONS),
        ("customization", _CUSTOMIZATION_QUERIES),
        ("customization", _CUSTOMIZATION_MUTATIONS),
        ("plugin", _PLUGIN_QUERIES),
        ("plugin", _PLUGIN_MUTATIONS),
        ("oidc", _OIDC_QUERIES),
        ("onboarding", _ONBOARDING_QUERIES),
        ("onboarding", _ONBOARDING_SIMPLE_MUTATIONS),
        ("onboarding", _ONBOARDING_INPUT_MUTATIONS),
    )


def all_operation_cases() -> list[tuple[str, str, str]]:
    cases: list[tuple[str, str, str]] = []
    for action, operations in operation_dicts():
        for subaction, query in operations.items():
            cases.append((action, subaction, query))
    return cases
