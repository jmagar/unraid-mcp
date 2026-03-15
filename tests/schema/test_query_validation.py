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


# ============================================================================
# Info Tool (19 queries)
# ============================================================================
class TestInfoQueries:
    """Validate all queries from unraid_mcp/tools/info.py."""

    def test_overview_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["overview"])
        assert not errors, f"overview query validation failed: {errors}"

    def test_array_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["array"])
        assert not errors, f"array query validation failed: {errors}"

    def test_network_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["network"])
        assert not errors, f"network query validation failed: {errors}"

    def test_registration_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["registration"])
        assert not errors, f"registration query validation failed: {errors}"

    def test_variables_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["variables"])
        assert not errors, f"variables query validation failed: {errors}"

    def test_metrics_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["metrics"])
        assert not errors, f"metrics query validation failed: {errors}"

    def test_services_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["services"])
        assert not errors, f"services query validation failed: {errors}"

    def test_display_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["display"])
        assert not errors, f"display query validation failed: {errors}"

    def test_config_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["config"])
        assert not errors, f"config query validation failed: {errors}"

    def test_online_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["online"])
        assert not errors, f"online query validation failed: {errors}"

    def test_owner_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["owner"])
        assert not errors, f"owner query validation failed: {errors}"

    def test_settings_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["settings"])
        assert not errors, f"settings query validation failed: {errors}"

    def test_server_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["server"])
        assert not errors, f"server query validation failed: {errors}"

    def test_servers_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["servers"])
        assert not errors, f"servers query validation failed: {errors}"

    def test_flash_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["flash"])
        assert not errors, f"flash query validation failed: {errors}"

    def test_ups_devices_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["ups_devices"])
        assert not errors, f"ups_devices query validation failed: {errors}"

    def test_ups_device_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["ups_device"])
        assert not errors, f"ups_device query validation failed: {errors}"

    def test_ups_config_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.info import QUERIES

        errors = _validate_operation(schema, QUERIES["ups_config"])
        assert not errors, f"ups_config query validation failed: {errors}"

    def test_all_info_actions_covered(self, schema: GraphQLSchema) -> None:
        """Ensure every key in QUERIES has a corresponding test."""
        from unraid_mcp.tools.info import QUERIES

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
# Array Tool (1 query + 4 mutations)
# ============================================================================
class TestArrayQueries:
    """Validate all queries from unraid_mcp/tools/array.py."""

    def test_parity_status_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.array import QUERIES

        errors = _validate_operation(schema, QUERIES["parity_status"])
        assert not errors, f"parity_status query validation failed: {errors}"

    def test_all_array_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.array import QUERIES

        assert set(QUERIES.keys()) == {"parity_status"}


class TestArrayMutations:
    """Validate all mutations from unraid_mcp/tools/array.py."""

    def test_parity_start_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.array import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["parity_start"])
        assert not errors, f"parity_start mutation validation failed: {errors}"

    def test_parity_pause_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.array import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["parity_pause"])
        assert not errors, f"parity_pause mutation validation failed: {errors}"

    def test_parity_resume_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.array import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["parity_resume"])
        assert not errors, f"parity_resume mutation validation failed: {errors}"

    def test_parity_cancel_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.array import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["parity_cancel"])
        assert not errors, f"parity_cancel mutation validation failed: {errors}"

    def test_all_array_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.array import MUTATIONS

        expected = {"parity_start", "parity_pause", "parity_resume", "parity_cancel"}
        assert set(MUTATIONS.keys()) == expected


# ============================================================================
# Storage Tool (5 queries + 1 mutation)
# ============================================================================
class TestStorageQueries:
    """Validate all queries from unraid_mcp/tools/storage.py."""

    def test_shares_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.storage import QUERIES

        errors = _validate_operation(schema, QUERIES["shares"])
        assert not errors, f"shares query validation failed: {errors}"

    def test_disks_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.storage import QUERIES

        errors = _validate_operation(schema, QUERIES["disks"])
        assert not errors, f"disks query validation failed: {errors}"

    def test_disk_details_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.storage import QUERIES

        errors = _validate_operation(schema, QUERIES["disk_details"])
        assert not errors, f"disk_details query validation failed: {errors}"

    def test_log_files_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.storage import QUERIES

        errors = _validate_operation(schema, QUERIES["log_files"])
        assert not errors, f"log_files query validation failed: {errors}"

    def test_logs_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.storage import QUERIES

        errors = _validate_operation(schema, QUERIES["logs"])
        assert not errors, f"logs query validation failed: {errors}"

    def test_all_storage_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.storage import QUERIES

        expected = {"shares", "disks", "disk_details", "log_files", "logs"}
        assert set(QUERIES.keys()) == expected


class TestStorageMutations:
    """Validate all mutations from unraid_mcp/tools/storage.py."""

    def test_flash_backup_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.storage import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["flash_backup"])
        assert not errors, f"flash_backup mutation validation failed: {errors}"

    def test_all_storage_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.storage import MUTATIONS

        assert set(MUTATIONS.keys()) == {"flash_backup"}


# ============================================================================
# Docker Tool (4 queries + 2 mutations)
# ============================================================================
class TestDockerQueries:
    """Validate all queries from unraid_mcp/tools/docker.py."""

    def test_list_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.docker import QUERIES

        errors = _validate_operation(schema, QUERIES["list"])
        assert not errors, f"list query validation failed: {errors}"

    def test_details_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.docker import QUERIES

        errors = _validate_operation(schema, QUERIES["details"])
        assert not errors, f"details query validation failed: {errors}"

    def test_networks_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.docker import QUERIES

        errors = _validate_operation(schema, QUERIES["networks"])
        assert not errors, f"networks query validation failed: {errors}"

    def test_network_details_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.docker import QUERIES

        errors = _validate_operation(schema, QUERIES["network_details"])
        assert not errors, f"network_details query validation failed: {errors}"

    def test_all_docker_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.docker import QUERIES

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
        from unraid_mcp.tools.docker import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["start"])
        assert not errors, f"start mutation validation failed: {errors}"

    def test_stop_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.docker import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["stop"])
        assert not errors, f"stop mutation validation failed: {errors}"

    def test_all_docker_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.docker import MUTATIONS

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
        from unraid_mcp.tools.virtualization import QUERIES

        errors = _validate_operation(schema, QUERIES["list"])
        assert not errors, f"list query validation failed: {errors}"

    def test_details_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.virtualization import QUERIES

        errors = _validate_operation(schema, QUERIES["details"])
        assert not errors, f"details query validation failed: {errors}"

    def test_all_vm_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.virtualization import QUERIES

        assert set(QUERIES.keys()) == {"list", "details"}


class TestVmMutations:
    """Validate all mutations from unraid_mcp/tools/virtualization.py."""

    def test_start_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.virtualization import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["start"])
        assert not errors, f"start mutation validation failed: {errors}"

    def test_stop_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.virtualization import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["stop"])
        assert not errors, f"stop mutation validation failed: {errors}"

    def test_pause_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.virtualization import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["pause"])
        assert not errors, f"pause mutation validation failed: {errors}"

    def test_resume_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.virtualization import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["resume"])
        assert not errors, f"resume mutation validation failed: {errors}"

    def test_force_stop_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.virtualization import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["force_stop"])
        assert not errors, f"force_stop mutation validation failed: {errors}"

    def test_reboot_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.virtualization import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["reboot"])
        assert not errors, f"reboot mutation validation failed: {errors}"

    def test_reset_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.virtualization import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["reset"])
        assert not errors, f"reset mutation validation failed: {errors}"

    def test_all_vm_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.virtualization import MUTATIONS

        expected = {"start", "stop", "pause", "resume", "force_stop", "reboot", "reset"}
        assert set(MUTATIONS.keys()) == expected


# ============================================================================
# Notifications Tool (3 queries + 6 mutations)
# ============================================================================
class TestNotificationQueries:
    """Validate all queries from unraid_mcp/tools/notifications.py."""

    def test_overview_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.notifications import QUERIES

        errors = _validate_operation(schema, QUERIES["overview"])
        assert not errors, f"overview query validation failed: {errors}"

    def test_list_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.notifications import QUERIES

        errors = _validate_operation(schema, QUERIES["list"])
        assert not errors, f"list query validation failed: {errors}"

    def test_all_notification_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.notifications import QUERIES

        assert set(QUERIES.keys()) == {"overview", "list"}


class TestNotificationMutations:
    """Validate all mutations from unraid_mcp/tools/notifications.py."""

    def test_create_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.notifications import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["create"])
        assert not errors, f"create mutation validation failed: {errors}"

    def test_archive_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.notifications import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["archive"])
        assert not errors, f"archive mutation validation failed: {errors}"

    def test_unread_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.notifications import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["unread"])
        assert not errors, f"unread mutation validation failed: {errors}"

    def test_delete_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.notifications import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["delete"])
        assert not errors, f"delete mutation validation failed: {errors}"

    def test_delete_archived_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.notifications import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["delete_archived"])
        assert not errors, f"delete_archived mutation validation failed: {errors}"

    def test_archive_all_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.notifications import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["archive_all"])
        assert not errors, f"archive_all mutation validation failed: {errors}"

    def test_archive_many_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.notifications import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["archive_many"])
        assert not errors, f"archive_many mutation validation failed: {errors}"

    def test_unarchive_many_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.notifications import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["unarchive_many"])
        assert not errors, f"unarchive_many mutation validation failed: {errors}"

    def test_unarchive_all_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.notifications import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["unarchive_all"])
        assert not errors, f"unarchive_all mutation validation failed: {errors}"

    def test_recalculate_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.notifications import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["recalculate"])
        assert not errors, f"recalculate mutation validation failed: {errors}"

    def test_all_notification_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.notifications import MUTATIONS

        expected = {
            "create",
            "archive",
            "unread",
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
        from unraid_mcp.tools.rclone import QUERIES

        errors = _validate_operation(schema, QUERIES["list_remotes"])
        assert not errors, f"list_remotes query validation failed: {errors}"

    def test_config_form_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.rclone import QUERIES

        errors = _validate_operation(schema, QUERIES["config_form"])
        assert not errors, f"config_form query validation failed: {errors}"

    def test_all_rclone_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.rclone import QUERIES

        assert set(QUERIES.keys()) == {"list_remotes", "config_form"}


class TestRcloneMutations:
    """Validate all mutations from unraid_mcp/tools/rclone.py."""

    def test_create_remote_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.rclone import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["create_remote"])
        assert not errors, f"create_remote mutation validation failed: {errors}"

    def test_delete_remote_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.rclone import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["delete_remote"])
        assert not errors, f"delete_remote mutation validation failed: {errors}"

    def test_all_rclone_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.rclone import MUTATIONS

        assert set(MUTATIONS.keys()) == {"create_remote", "delete_remote"}


# ============================================================================
# Users Tool (1 query)
# ============================================================================
class TestUsersQueries:
    """Validate all queries from unraid_mcp/tools/users.py."""

    def test_me_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.users import QUERIES

        errors = _validate_operation(schema, QUERIES["me"])
        assert not errors, f"me query validation failed: {errors}"

    def test_all_users_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.users import QUERIES

        assert set(QUERIES.keys()) == {"me"}


# ============================================================================
# Keys Tool (2 queries + 3 mutations)
# ============================================================================
class TestKeysQueries:
    """Validate all queries from unraid_mcp/tools/keys.py."""

    def test_list_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.keys import QUERIES

        errors = _validate_operation(schema, QUERIES["list"])
        assert not errors, f"list query validation failed: {errors}"

    def test_get_query(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.keys import QUERIES

        errors = _validate_operation(schema, QUERIES["get"])
        assert not errors, f"get query validation failed: {errors}"

    def test_all_keys_queries_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.keys import QUERIES

        assert set(QUERIES.keys()) == {"list", "get"}


class TestKeysMutations:
    """Validate all mutations from unraid_mcp/tools/keys.py."""

    def test_create_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.keys import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["create"])
        assert not errors, f"create mutation validation failed: {errors}"

    def test_update_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.keys import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["update"])
        assert not errors, f"update mutation validation failed: {errors}"

    def test_delete_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.keys import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["delete"])
        assert not errors, f"delete mutation validation failed: {errors}"

    def test_add_role_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.keys import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["add_role"])
        assert not errors, f"add_role mutation validation failed: {errors}"

    def test_remove_role_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.keys import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["remove_role"])
        assert not errors, f"remove_role mutation validation failed: {errors}"

    def test_all_keys_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.keys import MUTATIONS

        assert set(MUTATIONS.keys()) == {"create", "update", "delete", "add_role", "remove_role"}


# ============================================================================
# Settings Tool (0 queries + 2 mutations)
# ============================================================================
class TestSettingsMutations:
    """Validate all mutations from unraid_mcp/tools/settings.py."""

    def test_update_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.settings import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["update"])
        assert not errors, f"update mutation validation failed: {errors}"

    def test_configure_ups_mutation(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.settings import MUTATIONS

        errors = _validate_operation(schema, MUTATIONS["configure_ups"])
        assert not errors, f"configure_ups mutation validation failed: {errors}"

    def test_all_settings_mutations_covered(self, schema: GraphQLSchema) -> None:
        from unraid_mcp.tools.settings import MUTATIONS

        assert set(MUTATIONS.keys()) == {"update", "configure_ups"}


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
# Cross-cutting Validation
# ============================================================================
class TestSchemaCompleteness:
    """Validate that all tool operations are covered by the schema."""

    def test_all_tool_queries_validate(self, schema: GraphQLSchema) -> None:
        """Bulk-validate every query across all tools."""
        import importlib

        tool_modules = [
            "unraid_mcp.tools.info",
            "unraid_mcp.tools.array",
            "unraid_mcp.tools.storage",
            "unraid_mcp.tools.docker",
            "unraid_mcp.tools.virtualization",
            "unraid_mcp.tools.notifications",
            "unraid_mcp.tools.rclone",
            "unraid_mcp.tools.users",
            "unraid_mcp.tools.keys",
            "unraid_mcp.tools.settings",
        ]

        failures: list[str] = []
        total = 0

        for module_path in tool_modules:
            mod = importlib.import_module(module_path)
            tool_name = module_path.split(".")[-1]

            queries = getattr(mod, "QUERIES", {})
            for action, query_str in queries.items():
                total += 1
                errors = _validate_operation(schema, query_str)
                if errors:
                    failures.append(f"{tool_name}/QUERIES/{action}: {errors[0]}")

            mutations = getattr(mod, "MUTATIONS", {})
            for action, query_str in mutations.items():
                total += 1
                errors = _validate_operation(schema, query_str)
                if errors:
                    failures.append(f"{tool_name}/MUTATIONS/{action}: {errors[0]}")

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
        import importlib

        tool_modules = [
            "unraid_mcp.tools.info",
            "unraid_mcp.tools.array",
            "unraid_mcp.tools.storage",
            "unraid_mcp.tools.docker",
            "unraid_mcp.tools.virtualization",
            "unraid_mcp.tools.notifications",
            "unraid_mcp.tools.rclone",
            "unraid_mcp.tools.users",
            "unraid_mcp.tools.keys",
            "unraid_mcp.tools.settings",
        ]

        total = 0
        for module_path in tool_modules:
            mod = importlib.import_module(module_path)
            total += len(getattr(mod, "QUERIES", {}))
            total += len(getattr(mod, "MUTATIONS", {}))

        # Operations across all tools (queries + mutations in dicts)
        assert total >= 40, f"Expected at least 40 operations, found {total}"
