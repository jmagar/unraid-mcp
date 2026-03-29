"""Setting domain handler for the Unraid MCP tool.

Covers: update, configure_ups* (2 subactions).
"""

import re
from typing import Any

from fastmcp import Context

from ..config.logging import logger
from ..core import client as _client
from ..core.exceptions import ToolError, tool_error_handler
from ..core.guards import gate_destructive_action


# ===========================================================================
# SETTING
# ===========================================================================

# Input validation constants for settings_input (modeled on _validate_rclone_config)
_MAX_SETTINGS_KEYS = 100
_DANGEROUS_KEY_PATTERN = re.compile(r"\.\.|[/\\;|`$(){}]")
_MAX_VALUE_LENGTH = 4096


def _validate_settings_input(settings_input: dict[str, Any]) -> dict[str, Any]:
    """Validate settings_input before forwarding to the Unraid API.

    Enforces a key count cap and rejects dangerous key names and oversized values
    to prevent unvalidated bulk input from reaching the API. Modeled on
    _validate_rclone_config in _rclone.py.
    """
    if len(settings_input) > _MAX_SETTINGS_KEYS:
        raise ToolError(f"settings_input has {len(settings_input)} keys (max {_MAX_SETTINGS_KEYS})")
    validated: dict[str, Any] = {}
    for key, value in settings_input.items():
        if not isinstance(key, str) or not key.strip():
            raise ToolError(
                f"settings_input keys must be non-empty strings, got: {type(key).__name__}"
            )
        if _DANGEROUS_KEY_PATTERN.search(key):
            raise ToolError(f"settings_input key '{key}' contains disallowed characters")
        str_value = str(value) if not isinstance(value, (dict, list)) else repr(value)
        if len(str_value) > _MAX_VALUE_LENGTH:
            raise ToolError(
                f"settings_input['{key}'] value exceeds max length ({len(str_value)} > {_MAX_VALUE_LENGTH})"
            )
        validated[key] = value
    return validated


_SETTING_MUTATIONS: dict[str, str] = {
    "update": "mutation UpdateSettings($input: JSON!) { updateSettings(input: $input) { restartRequired values warnings } }",
    "configure_ups": "mutation ConfigureUps($config: UPSConfigInput!) { configureUps(config: $config) }",
}

_SETTING_SUBACTIONS: set[str] = set(_SETTING_MUTATIONS)
_SETTING_DESTRUCTIVE: set[str] = {"configure_ups"}


async def _handle_setting(
    subaction: str,
    settings_input: dict[str, Any] | None,
    ups_config: dict[str, Any] | None,
    ctx: Context | None,
    confirm: bool,
) -> dict[str, Any]:
    if subaction not in _SETTING_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for setting. Must be one of: {sorted(_SETTING_SUBACTIONS)}"
        )

    await gate_destructive_action(
        ctx,
        subaction,
        _SETTING_DESTRUCTIVE,
        confirm,
        "Configure UPS monitoring. This will overwrite the current UPS daemon settings.",
    )

    with tool_error_handler("setting", subaction, logger):
        logger.info(f"Executing unraid action=setting subaction={subaction}")

        if subaction == "update":
            if settings_input is None:
                raise ToolError("settings_input is required for setting/update")
            validated_input = _validate_settings_input(settings_input)
            data = await _client.make_graphql_request(
                _SETTING_MUTATIONS["update"], {"input": validated_input}
            )
            return {"success": True, "subaction": "update", "data": data.get("updateSettings")}

        if subaction == "configure_ups":
            if ups_config is None:
                raise ToolError("ups_config is required for setting/configure_ups")
            data = await _client.make_graphql_request(
                _SETTING_MUTATIONS["configure_ups"], {"config": ups_config}
            )
            return {
                "success": True,
                "subaction": "configure_ups",
                "result": data.get("configureUps"),
            }

        raise ToolError(f"Unhandled setting subaction '{subaction}' — this is a bug")
