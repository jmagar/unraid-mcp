"""Contract tests for the consolidated `unraid` dispatcher.

Two invariants the review flagged:

* #4 — the flat tool signature and the `UnraidInput` model are now coupled by a
  `locals()`-based pack, so their field sets MUST stay identical (extra="forbid"
  would otherwise reject a dispatch at runtime).
* #5 / TEST-H2 — the "mutation subaction not in the query dict -> KeyError"
  gotcha. Every domain handler ends with an explicit fall-through guard; this
  sweep proves each domain's guard actually fires for an in-set-but-unhandled
  subaction instead of leaking a raw KeyError (which `tool_error_handler` would
  mask as a generic "likely a bug"). Only `docker` was previously covered.
"""

from __future__ import annotations

import importlib
import inspect

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.unraid import UnraidInput


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.unraid", "register_unraid_tool", "unraid")


def test_unraid_input_fields_match_tool_signature() -> None:
    """#4: UnraidInput fields == the tool signature params (minus ctx).

    The packing block builds the model straight from locals(); if a parameter is
    added to one side and not the other this assertion fails at CI time instead of
    a confusing runtime ValidationError on a single subaction.
    """
    tool_fn = _make_tool()
    sig_params = set(inspect.signature(tool_fn).parameters) - {"ctx"}
    model_fields = set(UnraidInput.model_fields)
    assert sig_params == model_fields, (
        f"signature/model drift — only in signature: {sig_params - model_fields}; "
        f"only in model: {model_fields - sig_params}"
    )


# Domains whose handler ends with an explicit "Unhandled <domain> subaction ...
# — this is a bug" guard, plus the module + subactions-set attribute to monkeypatch
# so an in-set-but-unhandled subaction reaches that guard. (vm/user have no guard:
# they are structurally exhaustive. live/health use special dispatch and are
# covered by their own suites.)
_GUARDED_DOMAINS = {
    "system": ("unraid_mcp.tools._system", "_SYSTEM_SUBACTIONS"),
    "array": ("unraid_mcp.tools._array", "_ARRAY_SUBACTIONS"),
    "disk": ("unraid_mcp.tools._disk", "_DISK_SUBACTIONS"),
    "docker": ("unraid_mcp.tools._docker", "_DOCKER_SUBACTIONS"),
    "notification": ("unraid_mcp.tools._notification", "_NOTIFICATION_SUBACTIONS"),
    "key": ("unraid_mcp.tools._key", "_KEY_SUBACTIONS"),
    "plugin": ("unraid_mcp.tools._plugin", "_PLUGIN_SUBACTIONS"),
    "rclone": ("unraid_mcp.tools._rclone", "_RCLONE_SUBACTIONS"),
    "setting": ("unraid_mcp.tools._setting", "_SETTING_SUBACTIONS"),
    "connect": ("unraid_mcp.tools._connect", "_CONNECT_SUBACTIONS"),
    "onboarding": ("unraid_mcp.tools._onboarding", "_ONBOARDING_SUBACTIONS"),
    "customization": ("unraid_mcp.tools._customization", "_CUSTOMIZATION_SUBACTIONS"),
    "oidc": ("unraid_mcp.tools._oidc", "_OIDC_SUBACTIONS"),
}


@pytest.mark.parametrize("domain", sorted(_GUARDED_DOMAINS))
async def test_domain_fallthrough_guard_fires(
    domain: str, monkeypatch: pytest.MonkeyPatch, mock_graphql_request
) -> None:
    """#5: an in-set-but-unhandled subaction must raise the domain's clean
    fall-through guard, never a raw KeyError from a query-dict lookup."""
    module_name, attr = _GUARDED_DOMAINS[domain]
    module = importlib.import_module(module_name)
    fake = "__unhandled_probe__"
    current = getattr(module, attr)
    monkeypatch.setattr(module, attr, current | {fake})

    # Return value is irrelevant — the fake subaction falls through before any
    # GraphQL request is made. confirm=True keeps a (hypothetically destructive)
    # fake from being gated.
    mock_graphql_request.return_value = {}
    tool_fn = _make_tool()
    with pytest.raises(ToolError, match=rf"Unhandled {domain} subaction"):
        await tool_fn(action=domain, subaction=fake, confirm=True)
