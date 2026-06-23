"""Root-field parity report between Unraid GraphQL schema and exposed operations."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from graphql import FieldNode, GraphQLObjectType, OperationDefinitionNode, parse

from tests.schema.mock_unraid import schema
from tests.schema.operation_inventory import all_operation_cases


INTENTIONAL_QUERY_GAPS: dict[str, str] = {
    "connect": (
        "Connect reads are exposed through narrower remoteAccess/cloud actions; "
        "connect mutations cover the write surface."
    ),
    "customization": (
        "Customization reads use publicTheme/isFreshInstall/isSSOEnabled roots, "
        "with writes routed through the customization mutation namespace."
    ),
    "display": "Display data is exposed through system/display via info.display.",
    "network": "Network data is exposed through system/network via servers/vars.",
    "server": "Server data is exposed through system/server, system/servers, and related info roots.",
}

_SUBSCRIPTION_GAP_REASON = (
    "Subscription roots are covered by live resources and subscription diagnostics, "
    "not by the owned query/mutation operation inventory."
)
INTENTIONAL_SUBSCRIPTION_GAPS: dict[str, str] = dict.fromkeys(
    (
        "arraySubscription",
        "displaySubscription",
        "dockerContainerStats",
        "logFile",
        "notificationAdded",
        "notificationsOverview",
        "notificationsWarningsAndAlerts",
        "ownerSubscription",
        "parityHistorySubscription",
        "pluginInstallUpdates",
        "serversSubscription",
        "systemMetricsCpu",
        "systemMetricsCpuTelemetry",
        "systemMetricsMemory",
        "systemMetricsTemperature",
        "upsUpdates",
    ),
    _SUBSCRIPTION_GAP_REASON,
)
INTENTIONAL_MUTATION_GAPS: dict[str, str] = {}


def api_parity_report() -> dict[str, Any]:
    """Return schema root-field coverage for the current operation inventory."""
    used_by_kind = _used_root_fields_by_kind()
    sections = {
        "query": _section(
            schema_fields=_root_fields("query"),
            used_fields=used_by_kind["query"],
            intentional_gaps=INTENTIONAL_QUERY_GAPS,
        ),
        "mutation": _section(
            schema_fields=_root_fields("mutation"),
            used_fields=used_by_kind["mutation"],
            intentional_gaps=INTENTIONAL_MUTATION_GAPS,
        ),
        "subscription": _section(
            schema_fields=_root_fields("subscription"),
            used_fields=used_by_kind["subscription"],
            intentional_gaps=INTENTIONAL_SUBSCRIPTION_GAPS,
        ),
    }
    return {
        "operation_count": len(all_operation_cases()),
        **sections,
    }


def _section(
    *,
    schema_fields: set[str],
    used_fields: set[str],
    intentional_gaps: dict[str, str],
) -> dict[str, Any]:
    missing = schema_fields - used_fields
    intentional_missing = missing & set(intentional_gaps)
    return {
        "total": len(schema_fields),
        "used": len(used_fields & schema_fields),
        "missing": sorted(missing),
        "intentional": {name: intentional_gaps[name] for name in sorted(intentional_missing)},
        "unclassified_missing": sorted(missing - set(intentional_gaps)),
        "stale_intentional_gaps": sorted(set(intentional_gaps) - missing),
        "unknown_used_fields": sorted(used_fields - schema_fields),
    }


def _root_fields(kind: str) -> set[str]:
    graphql_schema = schema()
    root_type = {
        "query": graphql_schema.query_type,
        "mutation": graphql_schema.mutation_type,
        "subscription": graphql_schema.subscription_type,
    }[kind]
    if not isinstance(root_type, GraphQLObjectType):
        return set()
    return set(root_type.fields)


def _used_root_fields_by_kind() -> dict[str, set[str]]:
    used: dict[str, set[str]] = defaultdict(set)
    for _action, _subaction, operation in all_operation_cases():
        doc = parse(operation)
        for definition in doc.definitions:
            if not isinstance(definition, OperationDefinitionNode):
                continue
            kind = definition.operation.value
            for selection in definition.selection_set.selections:
                if isinstance(selection, FieldNode):
                    used[kind].add(selection.name.value)
    return used
