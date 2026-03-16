"""System settings, time, UPS, and remote access mutations.

Provides the `unraid_settings` tool with 9 actions for updating system
configuration, time settings, UPS, API settings, and Unraid Connect.
"""

from typing import Any, Literal, get_args

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler


MUTATIONS: dict[str, str] = {
    "update": """
        mutation UpdateSettings($input: JSON!) {
          updateSettings(input: $input) { restartRequired values warnings }
        }
    """,
    "update_temperature": """
        mutation UpdateTemperatureConfig($input: TemperatureConfigInput!) {
          updateTemperatureConfig(input: $input)
        }
    """,
    "update_time": """
        mutation UpdateSystemTime($input: UpdateSystemTimeInput!) {
          updateSystemTime(input: $input) { currentTime timeZone useNtp ntpServers }
        }
    """,
    "configure_ups": """
        mutation ConfigureUps($config: UPSConfigInput!) {
          configureUps(config: $config)
        }
    """,
    "update_api": """
        mutation UpdateApiSettings($input: ConnectSettingsInput!) {
          updateApiSettings(input: $input) { accessType forwardType port }
        }
    """,
    "connect_sign_in": """
        mutation ConnectSignIn($input: ConnectSignInInput!) {
          connectSignIn(input: $input)
        }
    """,
    "connect_sign_out": """
        mutation ConnectSignOut {
          connectSignOut
        }
    """,
    "setup_remote_access": """
        mutation SetupRemoteAccess($input: SetupRemoteAccessInput!) {
          setupRemoteAccess(input: $input)
        }
    """,
    "enable_dynamic_remote_access": """
        mutation EnableDynamicRemoteAccess($input: EnableDynamicRemoteAccessInput!) {
          enableDynamicRemoteAccess(input: $input)
        }
    """,
    "update_ssh": """
        mutation UpdateSshSettings($input: UpdateSshInput!) {
          updateSshSettings(input: $input) { useSsh portssh }
        }
    """,
}

DESTRUCTIVE_ACTIONS = {
    "configure_ups",
    "setup_remote_access",
    "enable_dynamic_remote_access",
    "update_ssh",
}
ALL_ACTIONS = set(MUTATIONS)

SETTINGS_ACTIONS = Literal[
    "configure_ups",
    "connect_sign_in",
    "connect_sign_out",
    "enable_dynamic_remote_access",
    "setup_remote_access",
    "update",
    "update_api",
    "update_ssh",
    "update_temperature",
    "update_time",
]

if set(get_args(SETTINGS_ACTIONS)) != ALL_ACTIONS:
    _missing = ALL_ACTIONS - set(get_args(SETTINGS_ACTIONS))
    _extra = set(get_args(SETTINGS_ACTIONS)) - ALL_ACTIONS
    raise RuntimeError(
        f"SETTINGS_ACTIONS and ALL_ACTIONS are out of sync. "
        f"Missing from Literal: {_missing or 'none'}. Extra in Literal: {_extra or 'none'}"
    )


def register_settings_tool(mcp: FastMCP) -> None:
    """Register the unraid_settings tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_settings(
        action: SETTINGS_ACTIONS,
        confirm: bool = False,
        settings_input: dict[str, Any] | None = None,
        temperature_config: dict[str, Any] | None = None,
        time_zone: str | None = None,
        use_ntp: bool | None = None,
        ntp_servers: list[str] | None = None,
        manual_datetime: str | None = None,
        ups_config: dict[str, Any] | None = None,
        access_type: str | None = None,
        forward_type: str | None = None,
        port: int | None = None,
        api_key: str | None = None,
        username: str | None = None,
        email: str | None = None,
        avatar: str | None = None,
        access_url_type: str | None = None,
        access_url_name: str | None = None,
        access_url_ipv4: str | None = None,
        access_url_ipv6: str | None = None,
        dynamic_enabled: bool | None = None,
        ssh_enabled: bool | None = None,
        ssh_port: int | None = None,
    ) -> dict[str, Any]:
        """Update Unraid system settings, time, UPS, and remote access configuration.

        Actions:
          update - Update system settings (requires settings_input dict)
          update_temperature - Update temperature sensor config (requires temperature_config dict)
          update_time - Update time/timezone/NTP (requires at least one of: time_zone, use_ntp, ntp_servers, manual_datetime)
          configure_ups - Configure UPS monitoring (requires ups_config dict, confirm=True)
          update_api - Update API/Connect settings (requires at least one of: access_type, forward_type, port)
          connect_sign_in - Sign in to Unraid Connect (requires api_key)
          connect_sign_out - Sign out from Unraid Connect
          setup_remote_access - Configure remote access (requires access_type, confirm=True)
          enable_dynamic_remote_access - Enable/disable dynamic remote access (requires access_url_type, dynamic_enabled, confirm=True)
          update_ssh - Enable/disable SSH and set port (requires ssh_enabled, ssh_port, confirm=True)
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        if action in DESTRUCTIVE_ACTIONS and not confirm:
            raise ToolError(f"Action '{action}' is destructive. Set confirm=True to proceed.")

        with tool_error_handler("settings", action, logger):
            logger.info(f"Executing unraid_settings action={action}")

            if action == "update":
                if settings_input is None:
                    raise ToolError("settings_input is required for 'update' action")
                data = await make_graphql_request(MUTATIONS["update"], {"input": settings_input})
                return {"success": True, "action": "update", "data": data.get("updateSettings")}

            if action == "update_temperature":
                if temperature_config is None:
                    raise ToolError(
                        "temperature_config is required for 'update_temperature' action"
                    )
                data = await make_graphql_request(
                    MUTATIONS["update_temperature"], {"input": temperature_config}
                )
                return {
                    "success": True,
                    "action": "update_temperature",
                    "result": data.get("updateTemperatureConfig"),
                }

            if action == "update_time":
                time_input: dict[str, Any] = {}
                if time_zone is not None:
                    time_input["timeZone"] = time_zone
                if use_ntp is not None:
                    time_input["useNtp"] = use_ntp
                if ntp_servers is not None:
                    time_input["ntpServers"] = ntp_servers
                if manual_datetime is not None:
                    time_input["manualDateTime"] = manual_datetime
                if not time_input:
                    raise ToolError(
                        "update_time requires at least one of: time_zone, use_ntp, ntp_servers, manual_datetime"
                    )
                data = await make_graphql_request(MUTATIONS["update_time"], {"input": time_input})
                return {
                    "success": True,
                    "action": "update_time",
                    "data": data.get("updateSystemTime"),
                }

            if action == "configure_ups":
                if ups_config is None:
                    raise ToolError("ups_config is required for 'configure_ups' action")
                data = await make_graphql_request(
                    MUTATIONS["configure_ups"], {"config": ups_config}
                )
                return {
                    "success": True,
                    "action": "configure_ups",
                    "result": data.get("configureUps"),
                }

            if action == "update_api":
                api_input: dict[str, Any] = {}
                if access_type is not None:
                    api_input["accessType"] = access_type
                if forward_type is not None:
                    api_input["forwardType"] = forward_type
                if port is not None:
                    api_input["port"] = port
                if not api_input:
                    raise ToolError(
                        "update_api requires at least one of: access_type, forward_type, port"
                    )
                data = await make_graphql_request(MUTATIONS["update_api"], {"input": api_input})
                return {
                    "success": True,
                    "action": "update_api",
                    "data": data.get("updateApiSettings"),
                }

            if action == "connect_sign_in":
                if not api_key:
                    raise ToolError("api_key is required for 'connect_sign_in' action")
                sign_in_input: dict[str, Any] = {"apiKey": api_key}
                user_info: dict[str, Any] = {}
                if username:
                    user_info["preferred_username"] = username
                if email:
                    user_info["email"] = email
                if avatar:
                    user_info["avatar"] = avatar
                if user_info:
                    sign_in_input["userInfo"] = user_info
                data = await make_graphql_request(
                    MUTATIONS["connect_sign_in"], {"input": sign_in_input}
                )
                return {
                    "success": True,
                    "action": "connect_sign_in",
                    "result": data.get("connectSignIn"),
                }

            if action == "connect_sign_out":
                data = await make_graphql_request(MUTATIONS["connect_sign_out"])
                return {
                    "success": True,
                    "action": "connect_sign_out",
                    "result": data.get("connectSignOut"),
                }

            if action == "setup_remote_access":
                if not access_type:
                    raise ToolError("access_type is required for 'setup_remote_access' action")
                remote_input: dict[str, Any] = {"accessType": access_type}
                if forward_type is not None:
                    remote_input["forwardType"] = forward_type
                if port is not None:
                    remote_input["port"] = port
                data = await make_graphql_request(
                    MUTATIONS["setup_remote_access"], {"input": remote_input}
                )
                return {
                    "success": True,
                    "action": "setup_remote_access",
                    "result": data.get("setupRemoteAccess"),
                }

            if action == "enable_dynamic_remote_access":
                if not access_url_type:
                    raise ToolError(
                        "access_url_type is required for 'enable_dynamic_remote_access' action"
                    )
                if dynamic_enabled is None:
                    raise ToolError(
                        "dynamic_enabled is required for 'enable_dynamic_remote_access' action"
                    )
                url_input: dict[str, Any] = {"type": access_url_type}
                if access_url_name is not None:
                    url_input["name"] = access_url_name
                if access_url_ipv4 is not None:
                    url_input["ipv4"] = access_url_ipv4
                if access_url_ipv6 is not None:
                    url_input["ipv6"] = access_url_ipv6
                dra_vars = {"input": {"url": url_input, "enabled": dynamic_enabled}}
                data = await make_graphql_request(
                    MUTATIONS["enable_dynamic_remote_access"],
                    dra_vars,
                )
                return {
                    "success": True,
                    "action": "enable_dynamic_remote_access",
                    "result": data.get("enableDynamicRemoteAccess"),
                }

            if action == "update_ssh":
                if ssh_enabled is None:
                    raise ToolError("ssh_enabled is required for 'update_ssh' action")
                if ssh_port is None:
                    raise ToolError("ssh_port is required for 'update_ssh' action")
                data = await make_graphql_request(
                    MUTATIONS["update_ssh"],
                    {"input": {"enabled": ssh_enabled, "port": ssh_port}},
                )
                return {
                    "success": True,
                    "action": "update_ssh",
                    "data": data.get("updateSshSettings"),
                }

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

    logger.info("Settings tool registered successfully")
