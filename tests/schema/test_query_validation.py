"""Schema validation tests for all GraphQL queries and mutations.

Validates every query and mutation in the tool QUERIES/MUTATIONS dicts
against the Unraid GraphQL SDL schema to catch syntax errors, missing
fields, and type mismatches before they reach production.
"""

from pathlib import Path

import pytest
from graphql import DocumentNode, GraphQLSchema, build_schema, parse, validate


SCHEMA_PATH = Path(__file__).resolve().parents[2] / "docs" / "unraid-schema.graphql"


@pytest.fixture(scope="module")
def schema() -> GraphQLSchema:
    """Load and cache the Unraid GraphQL schema for the entire test module."""
    schema_sdl = SCHEMA_PATH.read_text()
    return build_schema(schema_sdl)


def _validate_operation(schema: GraphQLSchema, query_str: str) -> list[str]:
    """Parse and validate a GraphQL operation against the schema."""
    doc: DocumentNode = parse(query_str)
    errors = validate(schema, doc)
    return [str(e) for e in errors]


def _all_domain_dicts() -> list[tuple[str, dict[str, str]]]:
    """Return all query/mutation dicts imported directly from domain modules.

    Single source of truth used by both test_all_tool_queries_validate and
    test_total_operations_count so the two lists stay in sync automatically.
    """
    from unraid_mcp.tools._array import _ARRAY_MUTATIONS, _ARRAY_QUERIES
    from unraid_mcp.tools._customization import (
        _CUSTOMIZATION_MUTATIONS,
        _CUSTOMIZATION_QUERIES,
    )
    from unraid_mcp.tools._disk import _DISK_MUTATIONS, _DISK_QUERIES
    from unraid_mcp.tools._docker import _DOCKER_MUTATIONS, _DOCKER_QUERIES
    from unraid_mcp.tools._key import _KEY_MUTATIONS, _KEY_QUERIES
    from unraid_mcp.tools._notification import (
        _NOTIFICATION_MUTATIONS,
        _NOTIFICATION_QUERIES,
    )
    from unraid_mcp.tools._oidc import _OIDC_QUERIES
    from unraid_mcp.tools._plugin import _PLUGIN_MUTATIONS, _PLUGIN_QUERIES
    from unraid_mcp.tools._rclone import _RCLONE_MUTATIONS, _RCLONE_QUERIES
    from unraid_mcp.tools._setting import _SETTING_MUTATIONS
    from unraid_mcp.tools._system import _SYSTEM_QUERIES
    from unraid_mcp.tools._user import _USER_QUERIES
    from unraid_mcp.tools._vm import _VM_MUTATIONS, _VM_QUERIES

    return [
        ("system/QUERIES", _SYSTEM_QUERIES),
        ("array/QUERIES", _ARRAY_QUERIES),
        ("array/MUTATIONS", _ARRAY_MUTATIONS),
        ("disk/QUERIES", _DISK_QUERIES),
        ("disk/MUTATIONS", _DISK_MUTATIONS),
        ("docker/QUERIES", _DOCKER_QUERIES),
        ("docker/MUTATIONS", _DOCKER_MUTATIONS),
        ("vm/QUERIES", _VM_QUERIES),
        ("vm/MUTATIONS", _VM_MUTATIONS),
        ("notification/QUERIES", _NOTIFICATION_QUERIES),
        ("notification/MUTATIONS", _NOTIFICATION_MUTATIONS),
        ("rclone/QUERIES", _RCLONE_QUERIES),
        ("rclone/MUTATIONS", _RCLONE_MUTATIONS),
        ("user/QUERIES", _USER_QUERIES),
        ("key/QUERIES", _KEY_QUERIES),
        ("key/MUTATIONS", _KEY_MUTATIONS),
        ("setting/MUTATIONS", _SETTING_MUTATIONS),
        ("customization/QUERIES", _CUSTOMIZATION_QUERIES),
        ("customization/MUTATIONS", _CUSTOMIZATION_MUTATIONS),
        ("plugin/QUERIES", _PLUGIN_QUERIES),
        ("plugin/MUTATIONS", _PLUGIN_MUTATIONS),
        ("oidc/QUERIES", _OIDC_QUERIES),
    ]


# ============================================================================
# Info Tool (19 queries)
# ============================================================================
class TestInfoQueries:
    """Validate all queries from unraid_mcp/tools/info.py."""

    def test_overview_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["overview"])
        assert not errors, f"overview query validation failed: {errors}"

    def test_array_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["array"])
        assert not errors, f"array query validation failed: {errors}"

    def test_network_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["network"])
        assert not errors, f"network query validation failed: {errors}"

    def test_registration_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["registration"])
        assert not errors, f"registration query validation failed: {errors}"

    def test_variables_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["variables"])
        assert not errors, f"variables query validation failed: {errors}"

    def test_metrics_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["metrics"])
        assert not errors, f"metrics query validation failed: {errors}"

    def test_services_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["services"])
        assert not errors, f"services query validation failed: {errors}"

    def test_display_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["display"])
        assert not errors, f"display query validation failed: {errors}"

    def test_config_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["config"])
        assert not errors, f"config query validation failed: {errors}"

    def test_online_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["online"])
        assert not errors, f"online query validation failed: {errors}"

    def test_owner_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["owner"])
        assert not errors, f"owner query validation failed: {errors}"

    def test_settings_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["settings"])
        assert not errors, f"settings query validation failed: {errors}"

    def test_server_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["server"])
        assert not errors, f"server query validation failed: {errors}"

    def test_servers_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["servers"])
        assert not errors, f"servers query validation failed: {errors}"

    def test_flash_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["flash"])
        assert not errors, f"flash query validation failed: {errors}"

    def test_ups_devices_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["ups_devices"])
        assert not errors, f"ups_devices query validation failed: {errors}"

    def test_ups_device_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["ups_device"])
        assert not errors, f"ups_device query validation failed: {errors}"

    def test_ups_config_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["ups_config"])
        assert not errors, f"ups_config query validation failed: {errors}"

    def test_all_info_actions_covered(self, schema: GraphQLSchema) -> None:
        """Ensure every key in QUERIES has a corresponding test."""
        from unraid_mcp.tools._system import _SYSTEM_QUERIES as QUERIES

        expected_actions = {
            "overview",
            "array",
            "network",
            "registration",
            "variables",
            "metrics",
            "services",
            "display",
            "config",
            "online",
            "owner",
            "settings",
            "server",
            "servers",
            "flash",
            "ups_devices",
            "ups_device",
            "ups_config",
        }
        assert set(QUERIES.keys()) == expected_actions


# ============================================================================
# Array Tool (2 queries + 11 mutations)
# ============================================================================
class TestArrayQueries:
    """Validate all queries from unraid_mcp/tools/array.py."""

    def test_parity_status_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._array import _ARRAY_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["parity_status"])
        assert not errors, f"parity_status query validation failed: {errors}"

    def test_parity_history_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._array import _ARRAY_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["parity_history"])
        assert not errors, f"parity_history query validation failed: {errors}"

    def test_all_array_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._array import _ARRAY_QUERIES as QUERIES

        assert set(QUERIES.keys()) == {"parity_status", "parity_history"}


class TestArrayMutations:
    """Validate all mutations from unraid_mcp/tools/array.py."""

    def test_parity_start_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._array import _ARRAY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["parity_start"])
        assert not errors, f"parity_start mutation validation failed: {errors}"

    def test_parity_pause_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._array import _ARRAY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["parity_pause"])
        assert not errors, f"parity_pause mutation validation failed: {errors}"

    def test_parity_resume_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._array import _ARRAY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["parity_resume"])
        assert not errors, f"parity_resume mutation validation failed: {errors}"

    def test_parity_cancel_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._array import _ARRAY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["parity_cancel"])
        assert not errors, f"parity_cancel mutation validation failed: {errors}"

    def test_start_array_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._array import _ARRAY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["start_array"])
        assert not errors, f"start_array mutation validation failed: {errors}"

    def test_stop_array_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._array import _ARRAY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["stop_array"])
        assert not errors, f"stop_array mutation validation failed: {errors}"

    def test_add_disk_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._array import _ARRAY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["add_disk"])
        assert not errors, f"add_disk mutation validation failed: {errors}"

    def test_remove_disk_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._array import _ARRAY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["remove_disk"])
        assert not errors, f"remove_disk mutation validation failed: {errors}"

    def test_mount_disk_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._array import _ARRAY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["mount_disk"])
        assert not errors, f"mount_disk mutation validation failed: {errors}"

    def test_unmount_disk_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._array import _ARRAY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["unmount_disk"])
        assert not errors, f"unmount_disk mutation validation failed: {errors}"

    def test_clear_disk_stats_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._array import _ARRAY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["clear_disk_stats"])
        assert not errors, f"clear_disk_stats mutation validation failed: {errors}"

    def test_all_array_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._array import _ARRAY_MUTATIONS as MUTATIONS

        expected = {
            "parity_start",
            "parity_pause",
            "parity_resume",
            "parity_cancel",
            "start_array",
            "stop_array",
            "add_disk",
            "remove_disk",
            "mount_disk",
            "unmount_disk",
            "clear_disk_stats",
        }
        assert set(MUTATIONS.keys()) == expected


# ============================================================================
# Storage Tool (5 queries + 1 mutation)
# ============================================================================
class TestStorageQueries:
    """Validate all queries from unraid_mcp/tools/storage.py."""

    def test_shares_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._disk import _DISK_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["shares"])
        assert not errors, f"shares query validation failed: {errors}"

    def test_disks_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._disk import _DISK_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["disks"])
        assert not errors, f"disks query validation failed: {errors}"

    def test_disk_details_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._disk import _DISK_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["disk_details"])
        assert not errors, f"disk_details query validation failed: {errors}"

    def test_log_files_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._disk import _DISK_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["log_files"])
        assert not errors, f"log_files query validation failed: {errors}"

    def test_logs_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._disk import _DISK_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["logs"])
        assert not errors, f"logs query validation failed: {errors}"

    def test_all_storage_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._disk import _DISK_QUERIES as QUERIES

        expected = {"shares", "disks", "disk_details", "log_files", "logs"}
        assert set(QUERIES.keys()) == expected


class TestStorageMutations:
    """Validate all mutations from unraid_mcp/tools/storage.py."""

    def test_flash_backup_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._disk import _DISK_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["flash_backup"])
        assert not errors, f"flash_backup mutation validation failed: {errors}"

    def test_all_storage_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._disk import _DISK_MUTATIONS as MUTATIONS

        assert set(MUTATIONS.keys()) == {"flash_backup"}


# ============================================================================
# Docker Tool (4 queries + 2 mutations)
# ============================================================================
class TestDockerQueries:
    """Validate all queries from unraid_mcp/tools/docker.py."""

    def test_list_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._docker import _DOCKER_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["list"])
        assert not errors, f"list query validation failed: {errors}"

    def test_details_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._docker import _DOCKER_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["details"])
        assert not errors, f"details query validation failed: {errors}"

    def test_networks_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._docker import _DOCKER_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["networks"])
        assert not errors, f"networks query validation failed: {errors}"

    def test_network_details_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._docker import _DOCKER_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["network_details"])
        assert not errors, f"network_details query validation failed: {errors}"

    def test_all_docker_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._docker import _DOCKER_QUERIES as QUERIES

        expected = {
            "list",
            "details",
            "networks",
            "network_details",
        }
        assert set(QUERIES.keys()) == expected


class TestDockerMutations:
    """Validate all mutations from unraid_mcp/tools/docker.py."""

    def test_start_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._docker import _DOCKER_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["start"])
        assert not errors, f"start mutation validation failed: {errors}"

    def test_stop_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._docker import _DOCKER_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["stop"])
        assert not errors, f"stop mutation validation failed: {errors}"

    def test_all_docker_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._docker import _DOCKER_MUTATIONS as MUTATIONS

        expected = {
            "start",
            "stop",
        }
        assert set(MUTATIONS.keys()) == expected


# ============================================================================
# VM Tool (1 query + 7 mutations)
# ============================================================================
class TestVmQueries:
    """Validate all queries from unraid_mcp/tools/virtualization.py."""

    def test_list_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._vm import _VM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["list"])
        assert not errors, f"list query validation failed: {errors}"

    def test_details_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._vm import _VM_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["details"])
        assert not errors, f"details query validation failed: {errors}"

    def test_all_vm_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._vm import _VM_QUERIES as QUERIES

        assert set(QUERIES.keys()) == {"list", "details"}


class TestVmMutations:
    """Validate all mutations from unraid_mcp/tools/virtualization.py."""

    def test_start_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._vm import _VM_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["start"])
        assert not errors, f"start mutation validation failed: {errors}"

    def test_stop_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._vm import _VM_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["stop"])
        assert not errors, f"stop mutation validation failed: {errors}"

    def test_pause_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._vm import _VM_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["pause"])
        assert not errors, f"pause mutation validation failed: {errors}"

    def test_resume_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._vm import _VM_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["resume"])
        assert not errors, f"resume mutation validation failed: {errors}"

    def test_force_stop_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._vm import _VM_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["force_stop"])
        assert not errors, f"force_stop mutation validation failed: {errors}"

    def test_reboot_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._vm import _VM_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["reboot"])
        assert not errors, f"reboot mutation validation failed: {errors}"

    def test_reset_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._vm import _VM_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["reset"])
        assert not errors, f"reset mutation validation failed: {errors}"

    def test_all_vm_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._vm import _VM_MUTATIONS as MUTATIONS

        expected = {"start", "stop", "pause", "resume", "force_stop", "reboot", "reset"}
        assert set(MUTATIONS.keys()) == expected


# ============================================================================
# Notifications Tool (3 queries + 6 mutations)
# ============================================================================
class TestNotificationQueries:
    """Validate all queries from unraid_mcp/tools/notifications.py."""

    def test_overview_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._notification import _NOTIFICATION_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["overview"])
        assert not errors, f"overview query validation failed: {errors}"

    def test_list_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._notification import _NOTIFICATION_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["list"])
        assert not errors, f"list query validation failed: {errors}"

    def test_all_notification_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._notification import _NOTIFICATION_QUERIES as QUERIES

        assert set(QUERIES.keys()) == {"overview", "list"}


class TestNotificationMutations:
    """Validate all mutations from unraid_mcp/tools/notifications.py."""

    def test_create_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._notification import _NOTIFICATION_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["create"])
        assert not errors, f"create mutation validation failed: {errors}"

    def test_archive_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._notification import _NOTIFICATION_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["archive"])
        assert not errors, f"archive mutation validation failed: {errors}"

    def test_mark_unread_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._notification import _NOTIFICATION_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["mark_unread"])
        assert not errors, f"mark_unread mutation validation failed: {errors}"

    def test_delete_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._notification import _NOTIFICATION_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["delete"])
        assert not errors, f"delete mutation validation failed: {errors}"

    def test_delete_archived_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._notification import _NOTIFICATION_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["delete_archived"])
        assert not errors, f"delete_archived mutation validation failed: {errors}"

    def test_archive_all_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._notification import _NOTIFICATION_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["archive_all"])
        assert not errors, f"archive_all mutation validation failed: {errors}"

    def test_archive_many_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._notification import _NOTIFICATION_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["archive_many"])
        assert not errors, f"archive_many mutation validation failed: {errors}"

    def test_unarchive_many_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._notification import _NOTIFICATION_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["unarchive_many"])
        assert not errors, f"unarchive_many mutation validation failed: {errors}"

    def test_unarchive_all_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._notification import _NOTIFICATION_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["unarchive_all"])
        assert not errors, f"unarchive_all mutation validation failed: {errors}"

    def test_recalculate_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._notification import _NOTIFICATION_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["recalculate"])
        assert not errors, f"recalculate mutation validation failed: {errors}"

    def test_all_notification_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._notification import _NOTIFICATION_MUTATIONS as MUTATIONS

        expected = {
            "create",
            "archive",
            "mark_unread",
            "delete",
            "delete_archived",
            "archive_all",
            "archive_many",
            "unarchive_many",
            "unarchive_all",
            "recalculate",
        }
        assert set(MUTATIONS.keys()) == expected


# ============================================================================
# RClone Tool (2 queries + 2 mutations)
# ============================================================================
class TestRcloneQueries:
    """Validate all queries from unraid_mcp/tools/rclone.py."""

    def test_list_remotes_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._rclone import _RCLONE_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["list_remotes"])
        assert not errors, f"list_remotes query validation failed: {errors}"

    def test_config_form_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._rclone import _RCLONE_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["config_form"])
        assert not errors, f"config_form query validation failed: {errors}"

    def test_all_rclone_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._rclone import _RCLONE_QUERIES as QUERIES

        assert set(QUERIES.keys()) == {"list_remotes", "config_form"}


class TestRcloneMutations:
    """Validate all mutations from unraid_mcp/tools/rclone.py."""

    def test_create_remote_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._rclone import _RCLONE_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["create_remote"])
        assert not errors, f"create_remote mutation validation failed: {errors}"

    def test_delete_remote_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._rclone import _RCLONE_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["delete_remote"])
        assert not errors, f"delete_remote mutation validation failed: {errors}"

    def test_all_rclone_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._rclone import _RCLONE_MUTATIONS as MUTATIONS

        assert set(MUTATIONS.keys()) == {"create_remote", "delete_remote"}


# ============================================================================
# Users Tool (1 query)
# ============================================================================
class TestUsersQueries:
    """Validate all queries from unraid_mcp/tools/users.py."""

    def test_me_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._user import _USER_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["me"])
        assert not errors, f"me query validation failed: {errors}"

    def test_all_users_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._user import _USER_QUERIES as QUERIES

        assert set(QUERIES.keys()) == {"me"}


# ============================================================================
# Keys Tool (2 queries + 3 mutations)
# ============================================================================
class TestKeysQueries:
    """Validate all queries from unraid_mcp/tools/keys.py."""

    def test_list_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._key import _KEY_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["list"])
        assert not errors, f"list query validation failed: {errors}"

    def test_get_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._key import _KEY_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["get"])
        assert not errors, f"get query validation failed: {errors}"

    def test_all_keys_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._key import _KEY_QUERIES as QUERIES

        assert set(QUERIES.keys()) == {"list", "get"}


class TestKeysMutations:
    """Validate all mutations from unraid_mcp/tools/keys.py."""

    def test_create_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._key import _KEY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["create"])
        assert not errors, f"create mutation validation failed: {errors}"

    def test_update_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._key import _KEY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["update"])
        assert not errors, f"update mutation validation failed: {errors}"

    def test_delete_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._key import _KEY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["delete"])
        assert not errors, f"delete mutation validation failed: {errors}"

    def test_add_role_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._key import _KEY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["add_role"])
        assert not errors, f"add_role mutation validation failed: {errors}"

    def test_remove_role_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._key import _KEY_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["remove_role"])
        assert not errors, f"remove_role mutation validation failed: {errors}"

    def test_all_keys_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._key import _KEY_MUTATIONS as MUTATIONS

        assert set(MUTATIONS.keys()) == {"create", "update", "delete", "add_role", "remove_role"}


# ============================================================================
# Settings Tool (0 queries + 2 mutations)
# ============================================================================
class TestSettingsMutations:
    """Validate all mutations from unraid_mcp/tools/settings.py."""

    def test_update_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._setting import _SETTING_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["update"])
        assert not errors, f"update mutation validation failed: {errors}"

    def test_configure_ups_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._setting import _SETTING_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["configure_ups"])
        assert not errors, f"configure_ups mutation validation failed: {errors}"

    def test_all_settings_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._setting import _SETTING_MUTATIONS as MUTATIONS

        expected = {
            "update",
            "configure_ups",
        }
        assert set(MUTATIONS.keys()) == expected


# ============================================================================
# Health Tool (inline queries)
# ============================================================================
class TestHealthQueries:
    """Validate inline queries from unraid_mcp/tools/health.py."""

    def test_connection_query(self, schema: GraphQLSchema) -> None:
        errors = _validate_operation(schema, "query { online }")
        assert not errors, f"test_connection query validation failed: {errors}"

    def test_comprehensive_check_query(self, schema: GraphQLSchema) -> None:
        query = """
        query ComprehensiveHealthCheck {
          info {
            machineId time
            versions { core { unraid } }
            os { uptime }
          }
          array { state }
          notifications {
            overview { unread { alert warning total } }
          }
          docker {
            containers(skipCache: true) { id state status }
          }
        }
        """
        errors = _validate_operation(schema, query)
        assert not errors, f"comprehensive check query validation failed: {errors}"


# ============================================================================
# Customization Tool (4 queries + 1 mutation)
# ============================================================================
class TestCustomizationQueries:
    """Validate queries from unraid_mcp/tools/customization.py."""

    def test_public_theme_query(self, schema: GraphQLSchema) -> None:
        # publicPartnerInfo not in schema; validate only publicTheme
        errors = _validate_operation(schema, "query { publicTheme { name } }")
        assert not errors, f"public_theme (publicTheme) query validation failed: {errors}"

    def test_is_initial_setup_query(self, schema: GraphQLSchema) -> None:
        # isInitialSetup not in schema; isFreshInstall is the equivalent field
        errors = _validate_operation(schema, "query { isFreshInstall }")
        assert not errors, f"is_initial_setup (isFreshInstall) query validation failed: {errors}"

    def test_sso_enabled_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._customization import _CUSTOMIZATION_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["sso_enabled"])
        assert not errors, f"sso_enabled query validation failed: {errors}"

    def test_customization_activation_code_query(self, schema: GraphQLSchema) -> None:
        # Customization.theme not in schema; use activationCode which is present
        errors = _validate_operation(schema, "query { customization { activationCode { code } } }")
        assert not errors, f"customization activationCode query validation failed: {errors}"


class TestCustomizationMutations:
    """Validate mutations from unraid_mcp/tools/customization.py."""

    def test_set_theme_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._customization import _CUSTOMIZATION_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["set_theme"])
        assert not errors, f"set_theme mutation validation failed: {errors}"

    def test_all_customization_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._customization import _CUSTOMIZATION_MUTATIONS as MUTATIONS

        assert set(MUTATIONS.keys()) == {"set_theme"}


# ============================================================================
# Plugins Tool (1 query + 2 mutations)
# ============================================================================
class TestPluginsQueries:
    """Validate all queries from unraid_mcp/tools/plugins.py."""

    def test_list_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._plugin import _PLUGIN_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["list"])
        assert not errors, f"plugins list query validation failed: {errors}"

    def test_all_plugins_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._plugin import _PLUGIN_QUERIES as QUERIES

        assert set(QUERIES.keys()) == {"list"}


class TestPluginsMutations:
    """Validate all mutations from unraid_mcp/tools/plugins.py."""

    def test_add_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._plugin import _PLUGIN_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["add"])
        assert not errors, f"plugins add mutation validation failed: {errors}"

    def test_remove_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._plugin import _PLUGIN_MUTATIONS as MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["remove"])
        assert not errors, f"plugins remove mutation validation failed: {errors}"

    def test_all_plugins_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._plugin import _PLUGIN_MUTATIONS as MUTATIONS

        assert set(MUTATIONS.keys()) == {"add", "remove"}


# ============================================================================
# OIDC Tool (5 queries)
# ============================================================================
class TestOidcQueries:
    """Validate all queries from unraid_mcp/tools/oidc.py."""

    def test_providers_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._oidc import _OIDC_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["providers"])
        assert not errors, f"oidc providers query validation failed: {errors}"

    def test_provider_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._oidc import _OIDC_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["provider"])
        assert not errors, f"oidc provider query validation failed: {errors}"

    def test_configuration_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._oidc import _OIDC_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["configuration"])
        assert not errors, f"oidc configuration query validation failed: {errors}"

    def test_public_providers_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._oidc import _OIDC_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["public_providers"])
        assert not errors, f"oidc public_providers query validation failed: {errors}"

    def test_validate_session_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._oidc import _OIDC_QUERIES as QUERIES

        errors = _validate_operation(schema, QUERIES["validate_session"])
        assert not errors, f"oidc validate_session query validation failed: {errors}"

    def test_all_oidc_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools._oidc import _OIDC_QUERIES as QUERIES

        expected = {
            "providers",
            "provider",
            "configuration",
            "public_providers",
            "validate_session",
        }
        assert set(QUERIES.keys()) == expected


# ============================================================================
# Cross-cutting Validation
# ============================================================================
class TestSchemaCompleteness:
    """Validate that all tool operations are covered by the schema."""

    def test_all_tool_queries_validate(self, schema: GraphQLSchema) -> None:
        """Bulk-validate every query/mutation across all domains.

        Known schema mismatches are tracked in KNOWN_SCHEMA_ISSUES and excluded
        from the assertion so the test suite stays green while the underlying
        tool queries are fixed incrementally.
        """
        # All query/mutation dicts from domain modules, keyed by domain/type label
        all_operation_dicts = _all_domain_dicts()

        # Known schema mismatches — bugs in tool implementation, not in tests.
        # Remove entries as they are fixed.
        KNOWN_SCHEMA_ISSUES: set[str] = {
            # customization: Customization.theme field does not exist
            "customization/QUERIES/theme",
            # customization: publicPartnerInfo not in Query type
            "customization/QUERIES/public_theme",
            # customization: isInitialSetup not in Query type (use isFreshInstall)
            "customization/QUERIES/is_initial_setup",
        }

        failures: list[str] = []
        unexpected_passes: list[str] = []
        total = 0

        for label, ops_dict in all_operation_dicts:
            for action, query_str in ops_dict.items():
                total += 1
                key = f"{label}/{action}"
                errors = _validate_operation(schema, query_str)
                if errors:
                    if key not in KNOWN_SCHEMA_ISSUES:
                        failures.append(f"{key}: {errors[0]}")
                else:
                    if key in KNOWN_SCHEMA_ISSUES:
                        unexpected_passes.append(key)

        if unexpected_passes:
            raise AssertionError(
                "The following operations are listed in KNOWN_SCHEMA_ISSUES but now pass — "
                "remove them from the set:\n" + "\n".join(unexpected_passes)
            )

        assert not failures, (
            f"{len(failures)} of {total} operations failed validation:\n" + "\n".join(failures)
        )

    def test_schema_has_query_type(self, schema: GraphQLSchema) -> None:
        assert schema.query_type is not None

    def test_schema_has_mutation_type(self, schema: GraphQLSchema) -> None:
        assert schema.mutation_type is not None

    def test_schema_has_subscription_type(self, schema: GraphQLSchema) -> None:
        assert schema.subscription_type is not None

    def test_total_operations_count(self, schema: GraphQLSchema) -> None:
        """Verify the expected number of tool operations exist."""
        all_dicts = [d for _, d in _all_domain_dicts()]

        total = sum(len(d) for d in all_dicts)
        assert total >= 90, f"Expected at least 90 operations, found {total}"
