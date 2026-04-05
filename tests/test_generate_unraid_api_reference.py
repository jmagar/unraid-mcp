from __future__ import annotations

from scripts.generate_unraid_api_reference import _build_changes_markdown


def _type_ref(
    name: str | None = None, *, kind: str = "OBJECT", of_type: dict | None = None
) -> dict:
    return {"kind": kind, "name": name, "ofType": of_type}


def _field(
    name: str,
    return_type: dict,
    *,
    args: list[dict] | None = None,
    description: str | None = None,
) -> dict:
    return {
        "name": name,
        "description": description,
        "isDeprecated": False,
        "deprecationReason": None,
        "args": args or [],
        "type": return_type,
    }


def _arg(name: str, arg_type: dict, *, default: str | None = None) -> dict:
    return {
        "name": name,
        "description": None,
        "defaultValue": default,
        "type": arg_type,
    }


def _schema(
    *,
    query_fields: list[dict],
    mutation_fields: list[dict] | None = None,
    subscription_fields: list[dict] | None = None,
    extra_types: list[dict] | None = None,
) -> dict:
    types = [
        {
            "kind": "OBJECT",
            "name": "Query",
            "description": None,
            "fields": query_fields,
            "inputFields": None,
            "interfaces": [],
            "enumValues": None,
            "possibleTypes": None,
        },
        {
            "kind": "OBJECT",
            "name": "Mutation",
            "description": None,
            "fields": mutation_fields or [],
            "inputFields": None,
            "interfaces": [],
            "enumValues": None,
            "possibleTypes": None,
        },
        {
            "kind": "OBJECT",
            "name": "Subscription",
            "description": None,
            "fields": subscription_fields or [],
            "inputFields": None,
            "interfaces": [],
            "enumValues": None,
            "possibleTypes": None,
        },
    ]
    if extra_types:
        types.extend(extra_types)
    return {
        "queryType": {"name": "Query"},
        "mutationType": {"name": "Mutation"},
        "subscriptionType": {"name": "Subscription"},
        "directives": [],
        "types": types,
    }


def test_changes_report_handles_missing_previous_snapshot() -> None:
    current = _schema(query_fields=[_field("online", _type_ref("Boolean", kind="SCALAR"))])

    report = _build_changes_markdown(
        None,
        current,
        source="https://tower.local/graphql",
        generated_at="2026-04-05T18:00:00+00:00",
        include_introspection=False,
    )

    assert "No previous introspection snapshot was available" in report
    assert "https://tower.local/graphql" in report


def test_changes_report_lists_root_and_type_signature_deltas() -> None:
    previous = _schema(
        query_fields=[
            _field("online", _type_ref("Boolean", kind="SCALAR")),
            _field("server", _type_ref("Server")),
        ],
        mutation_fields=[_field("connectSignIn", _type_ref("Boolean", kind="SCALAR"))],
        subscription_fields=[_field("ownerSubscription", _type_ref("Owner"))],
        extra_types=[
            {
                "kind": "OBJECT",
                "name": "Server",
                "description": None,
                "fields": [_field("id", _type_ref("ID", kind="SCALAR"))],
                "inputFields": None,
                "interfaces": [],
                "enumValues": None,
                "possibleTypes": None,
            }
        ],
    )
    current = _schema(
        query_fields=[
            _field("online", _type_ref("Boolean", kind="SCALAR")),
            _field(
                "server",
                _type_ref("Server"),
                args=[_arg("verbose", _type_ref("Boolean", kind="SCALAR"), default="false")],
            ),
            _field("cloud", _type_ref("Cloud")),
        ],
        mutation_fields=[],
        subscription_fields=[
            _field("ownerSubscription", _type_ref("Owner")),
            _field("dockerContainerStats", _type_ref("DockerContainerStats")),
        ],
        extra_types=[
            {
                "kind": "OBJECT",
                "name": "Server",
                "description": None,
                "fields": [
                    _field("id", _type_ref("ID", kind="SCALAR")),
                    _field("name", _type_ref("String", kind="SCALAR")),
                ],
                "inputFields": None,
                "interfaces": [],
                "enumValues": None,
                "possibleTypes": None,
            },
            {
                "kind": "OBJECT",
                "name": "Cloud",
                "description": None,
                "fields": [],
                "inputFields": None,
                "interfaces": [],
                "enumValues": None,
                "possibleTypes": None,
            },
        ],
    )

    report = _build_changes_markdown(
        previous,
        current,
        source="https://tower.local/graphql",
        generated_at="2026-04-05T18:00:00+00:00",
        include_introspection=False,
    )

    assert "## Query fields" in report
    assert "`cloud`" in report
    assert "## Mutation fields" in report
    assert "`connectSignIn`" in report
    assert "## Subscription fields" in report
    assert "`dockerContainerStats`" in report
    assert "### OBJECT" in report
    assert "### `Server` (OBJECT)" in report
    assert "`name(): String`" in report
    assert "`server(verbose: Boolean = false): Server`" in report
