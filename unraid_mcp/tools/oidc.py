"""OIDC/SSO provider management and session validation.

Provides the `unraid_oidc` tool with 5 read-only actions for querying
OIDC provider configuration and validating sessions.
"""

from __future__ import annotations

from typing import Any, Literal, get_args

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler


QUERIES: dict[str, str] = {
    "providers": """
        query GetOidcProviders {
          oidcProviders {
            id name clientId issuer authorizationEndpoint tokenEndpoint jwksUri
            scopes authorizationRules { claim operator value }
            authorizationRuleMode buttonText buttonIcon buttonVariant buttonStyle
          }
        }
    """,
    "provider": """
        query GetOidcProvider($id: PrefixedID!) {
          oidcProvider(id: $id) {
            id name clientId issuer scopes
            authorizationRules { claim operator value }
            authorizationRuleMode buttonText buttonIcon
          }
        }
    """,
    "configuration": """
        query GetOidcConfiguration {
          oidcConfiguration {
            providers { id name clientId scopes }
            defaultAllowedOrigins
          }
        }
    """,
    "public_providers": """
        query GetPublicOidcProviders {
          publicOidcProviders { id name buttonText buttonIcon buttonVariant buttonStyle }
        }
    """,
    "validate_session": """
        query ValidateOidcSession($token: String!) {
          validateOidcSession(token: $token) { valid username }
        }
    """,
}

ALL_ACTIONS = set(QUERIES)

OIDC_ACTIONS = Literal[
    "configuration",
    "provider",
    "providers",
    "public_providers",
    "validate_session",
]

if set(get_args(OIDC_ACTIONS)) != ALL_ACTIONS:
    _missing = ALL_ACTIONS - set(get_args(OIDC_ACTIONS))
    _extra = set(get_args(OIDC_ACTIONS)) - ALL_ACTIONS
    raise RuntimeError(
        f"OIDC_ACTIONS and ALL_ACTIONS are out of sync. "
        f"Missing: {_missing or 'none'}. Extra: {_extra or 'none'}"
    )


def register_oidc_tool(mcp: FastMCP) -> None:
    """Register the unraid_oidc tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_oidc(
        action: OIDC_ACTIONS,
        provider_id: str | None = None,
        token: str | None = None,
    ) -> dict[str, Any]:
        """Query Unraid OIDC/SSO provider configuration and validate sessions.

        Actions:
          providers        - List all configured OIDC providers (admin only)
          provider         - Get a specific OIDC provider by ID (requires provider_id)
          configuration    - Get full OIDC configuration including default origins (admin only)
          public_providers - Get public OIDC provider info for login buttons (no auth)
          validate_session - Validate an OIDC session token (requires token)
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        if action == "provider" and not provider_id:
            raise ToolError("provider_id is required for 'provider' action")

        if action == "validate_session" and not token:
            raise ToolError("token is required for 'validate_session' action")

        with tool_error_handler("oidc", action, logger):
            logger.info(f"Executing unraid_oidc action={action}")

            if action == "provider":
                data = await make_graphql_request(QUERIES[action], {"id": provider_id})
                return {"success": True, "action": action, "data": data}

            if action == "validate_session":
                data = await make_graphql_request(QUERIES[action], {"token": token})
                return {"success": True, "action": action, "data": data}

            data = await make_graphql_request(QUERIES[action])
            return {"success": True, "action": action, "data": data}

    logger.info("OIDC tool registered successfully")
