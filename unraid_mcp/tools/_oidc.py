"""OIDC domain handler for the Unraid MCP tool.

Covers: providers, provider, configuration, public_providers, validate_session (5 subactions).
"""

from typing import Any

from ..config.logging import logger
from ..core import client as _client
from ..core.exceptions import ToolError, tool_error_handler


# ===========================================================================
# OIDC
# ===========================================================================

_OIDC_QUERIES: dict[str, str] = {
    "providers": "query GetOidcProviders { oidcProviders { id name clientId issuer authorizationEndpoint tokenEndpoint jwksUri scopes authorizationRules { claim operator value } authorizationRuleMode buttonText buttonIcon buttonVariant buttonStyle } }",
    "provider": "query GetOidcProvider($id: PrefixedID!) { oidcProvider(id: $id) { id name clientId issuer scopes authorizationRules { claim operator value } authorizationRuleMode buttonText buttonIcon } }",
    "configuration": "query GetOidcConfiguration { oidcConfiguration { providers { id name clientId scopes } defaultAllowedOrigins } }",
    "public_providers": "query GetPublicOidcProviders { publicOidcProviders { id name buttonText buttonIcon buttonVariant buttonStyle } }",
    "validate_session": "query ValidateOidcSession($token: String!) { validateOidcSession(token: $token) { valid username } }",
}

_OIDC_SUBACTIONS: set[str] = set(_OIDC_QUERIES)


async def _handle_oidc(
    subaction: str, provider_id: str | None, token: str | None
) -> dict[str, Any]:
    if subaction not in _OIDC_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for oidc. Must be one of: {sorted(_OIDC_SUBACTIONS)}"
        )

    if subaction == "provider" and not provider_id:
        raise ToolError("provider_id is required for oidc/provider")
    if subaction == "validate_session" and not token:
        raise ToolError("token is required for oidc/validate_session")

    variables: dict[str, Any] | None = None
    if subaction == "provider":
        variables = {"id": provider_id}
    elif subaction == "validate_session":
        variables = {"token": token}

    with tool_error_handler("oidc", subaction, logger):
        logger.info(f"Executing unraid action=oidc subaction={subaction}")
        data = await _client.make_graphql_request(_OIDC_QUERIES[subaction], variables)

        if subaction == "providers":
            return {"providers": data.get("oidcProviders", [])}
        if subaction == "provider":
            return dict(data.get("oidcProvider") or {})
        if subaction == "configuration":
            return dict(data.get("oidcConfiguration") or {})
        if subaction == "public_providers":
            return {"providers": data.get("publicOidcProviders", [])}
        if subaction == "validate_session":
            return dict(data.get("validateOidcSession") or {})

        raise ToolError(f"Unhandled oidc subaction '{subaction}' — this is a bug")
