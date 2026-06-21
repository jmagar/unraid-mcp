"""Drift guard: the `unraid` tool's docs must match the live subaction sets.

The single `unraid` tool is agent-facing, and `action="help"` returns `_HELP_TEXT`
verbatim. An incomplete or stale table is a real defect — an agent reading the help
reference would not know a subaction exists. This module converts that silent
documentation drift into a CI failure by asserting the help reference (and the
module docstrings that quote counts) agree with the authoritative `_*_SUBACTIONS`
sets imported directly from the domain modules.

If this test fails after you add or rename a subaction, update:
  - `unraid_mcp/tools/unraid.py`  -> `_HELP_TEXT` table + module docstring counts
  - `unraid_mcp/tools/__init__.py` -> the "(N actions, M subactions)" header
  - `CLAUDE.md` / `README.md` / `docs/**` tables (kept consistent by review)
"""

from __future__ import annotations

import re

from unraid_mcp import tools as _tools_pkg
from unraid_mcp.subscriptions.diagnostics import _SUBSCRIPTIONS_SUBACTIONS
from unraid_mcp.subscriptions.queries import COLLECT_ACTIONS, SNAPSHOT_ACTIONS
from unraid_mcp.tools import (
    _array,
    _connect,
    _customization,
    _disk,
    _docker,
    _health,
    _key,
    _notification,
    _oidc,
    _onboarding,
    _plugin,
    _rclone,
    _setting,
    _system,
    _user,
    _vm,
)
from unraid_mcp.tools import (
    unraid as _unraid_mod,
)
from unraid_mcp.tools.unraid import _HELP_TEXT


# Module docstrings carry the human-facing counts these tests guard.
_TOOLS_INIT_DOC = _tools_pkg.__doc__
_UNRAID_MODULE_DOC = _unraid_mod.__doc__


def _live_subactions() -> set[str]:
    return set(SNAPSHOT_ACTIONS) | set(COLLECT_ACTIONS)


# action name -> authoritative subaction set, sourced straight from the modules.
# `help` has no subactions; it is the action that returns `_HELP_TEXT`.
LIVE_SUBACTIONS: dict[str, set[str]] = {
    "system": set(_system._SYSTEM_SUBACTIONS),
    "health": set(_health._HEALTH_SUBACTIONS),
    "array": set(_array._ARRAY_SUBACTIONS),
    "disk": set(_disk._DISK_SUBACTIONS),
    "docker": set(_docker._DOCKER_SUBACTIONS),
    "vm": set(_vm._VM_SUBACTIONS),
    "notification": set(_notification._NOTIFICATION_SUBACTIONS),
    "key": set(_key._KEY_SUBACTIONS),
    "plugin": set(_plugin._PLUGIN_SUBACTIONS),
    "rclone": set(_rclone._RCLONE_SUBACTIONS),
    "setting": set(_setting._SETTING_SUBACTIONS),
    "connect": set(_connect._CONNECT_SUBACTIONS),
    "customization": set(_customization._CUSTOMIZATION_SUBACTIONS),
    "oidc": set(_oidc._OIDC_SUBACTIONS),
    "onboarding": set(_onboarding._ONBOARDING_SUBACTIONS),
    "user": set(_user._USER_SUBACTIONS),
    "live": _live_subactions(),
    "subscriptions": set(_SUBSCRIPTIONS_SUBACTIONS),
}

# `help` is an action with no subactions.
LIVE_ACTION_COUNT = len(LIVE_SUBACTIONS) + 1  # + help
LIVE_SUBACTION_TOTAL = sum(len(s) for s in LIVE_SUBACTIONS.values())


def _help_row_subactions(action: str) -> set[str]:
    """Pull the backtick-wrapped subaction tokens out of the help table row.

    Rows look like::

        | `system` | `overview`, `array`, ... | |

    We locate the row whose first cell is the action, then collect every
    `` `token` `` from the second (subactions) cell. The destructive `*` suffix
    sits outside the backticks, so the tokens are clean subaction names.
    """
    # Match a markdown table row starting with the action in backticks.
    pattern = re.compile(
        r"^\|\s*`" + re.escape(action) + r"`\s*\|(?P<cell>.*?)\|.*$",
        re.MULTILINE,
    )
    m = pattern.search(_HELP_TEXT)
    assert m is not None, f"action {action!r} not found as a table row in _HELP_TEXT"
    cell = m.group("cell")
    return set(re.findall(r"`([a-z_]+)`", cell))


class TestHelpTextTableMatchesCode:
    def test_every_action_row_lists_exactly_its_live_subactions(self) -> None:
        mismatches: dict[str, dict[str, list[str]]] = {}
        for action, live in LIVE_SUBACTIONS.items():
            documented = _help_row_subactions(action)
            missing = sorted(live - documented)
            extra = sorted(documented - live)
            if missing or extra:
                mismatches[action] = {"missing_from_docs": missing, "not_in_code": extra}
        assert not mismatches, (
            "`_HELP_TEXT` action/subaction table is out of sync with the live "
            f"`_*_SUBACTIONS` sets:\n{mismatches}\n"
            "Update the table in unraid_mcp/tools/unraid.py (`_HELP_TEXT`)."
        )

    def test_help_action_row_has_no_subactions(self) -> None:
        # `help` is documented but takes no subaction.
        assert "| `help` |" in _HELP_TEXT


class TestModuleDocstringCounts:
    def test_unraid_module_docstring_total_action_count(self) -> None:
        assert _UNRAID_MODULE_DOC is not None
        m = re.search(r"with (\d+) actions", _UNRAID_MODULE_DOC)
        assert m is not None, "could not find action count in unraid.py module docstring"
        assert int(m.group(1)) == LIVE_ACTION_COUNT, (
            f"unraid.py module docstring says {m.group(1)} actions; "
            f"live count is {LIVE_ACTION_COUNT}"
        )

    def test_unraid_module_docstring_per_action_subaction_counts(self) -> None:
        assert _UNRAID_MODULE_DOC is not None
        # Lines look like: "  system       - ... (20 subactions)"
        documented: dict[str, int] = {}
        for line in _UNRAID_MODULE_DOC.splitlines():
            m = re.match(r"\s*([a-z_]+)\s+-\s+.*\((\d+) subactions?\)", line)
            if m:
                documented[m.group(1)] = int(m.group(2))
        mismatches = {
            action: (documented.get(action), len(live))
            for action, live in LIVE_SUBACTIONS.items()
            if documented.get(action) != len(live)
        }
        assert not mismatches, (
            "unraid.py module docstring per-action subaction counts are stale "
            f"(documented, live): {mismatches}"
        )

    def test_tools_init_docstring_counts(self) -> None:
        assert _TOOLS_INIT_DOC is not None
        m = re.search(r"\((\d+) actions,\s*(\d+) subactions\)", _TOOLS_INIT_DOC)
        assert m is not None, (
            "could not find '(N actions, M subactions)' header in tools/__init__.py docstring"
        )
        actions, subactions = int(m.group(1)), int(m.group(2))
        assert actions == LIVE_ACTION_COUNT, (
            f"tools/__init__.py says {actions} actions; live is {LIVE_ACTION_COUNT}"
        )
        assert subactions == LIVE_SUBACTION_TOTAL, (
            f"tools/__init__.py says {subactions} subactions; live is {LIVE_SUBACTION_TOTAL}"
        )


class TestSpecificDriftedSubactions:
    """Lock in the four subactions the prior review flagged as missing from docs."""

    def test_known_previously_missing_subactions_are_documented(self) -> None:
        for action, subaction in (
            ("system", "server_time"),
            ("system", "timezones"),
            ("notification", "notify_if_unique"),
            ("docker", "logs"),
        ):
            assert subaction in LIVE_SUBACTIONS[action], (
                f"{action}/{subaction} disappeared from code — update this guard"
            )
            assert subaction in _help_row_subactions(action), (
                f"{action}/{subaction} is missing from the `_HELP_TEXT` table"
            )
