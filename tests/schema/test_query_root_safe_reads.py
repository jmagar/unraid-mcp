"""Safety contracts for direct query-root read subactions."""

from typing import Any
from unittest.mock import AsyncMock

import pytest
from conftest import make_tool_fn


pytestmark = pytest.mark.asyncio


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.unraid", "register_unraid_tool", "unraid")


def _contains_key(value: Any, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(_contains_key(child, key) for child in value.values())
    if isinstance(value, list):
        return any(_contains_key(child, key) for child in value)
    return False


async def test_system_server_details_omits_apikey(mock_graphql_request: AsyncMock) -> None:
    mock_graphql_request.return_value = {
        "server": {
            "id": "server-1",
            "owner": {
                "id": "owner-1",
                "username": "root",
                "url": "https://example.com/u/root",
                "avatar": "https://example.com/avatar.png",
            },
            "guid": "guid-1",
            "name": "tower",
            "comment": "media server",
            "status": "ONLINE",
            "wanip": "203.0.113.10",
            "lanip": "192.0.2.10",
            "localurl": "https://tower.local",
            "remoteurl": "https://tower.example.com",
        }
    }

    result = await _make_tool()(action="system", subaction="server_details")

    assert result["server"]["name"] == "tower"
    assert not _contains_key(result, "apikey")
    emitted_query = mock_graphql_request.call_args.args[0]
    assert "apikey" not in emitted_query


async def test_connect_status_omits_settings_values(mock_graphql_request: AsyncMock) -> None:
    mock_graphql_request.return_value = {
        "connect": {
            "id": "connect-1",
            "dynamicRemoteAccess": {
                "enabledType": "DISABLED",
                "runningType": "DISABLED",
                "error": None,
            },
            "settings": {
                "id": "settings-1",
                "dataSchema": {},
                "uiSchema": {},
            },
        }
    }

    result = await _make_tool()(action="connect", subaction="status")

    assert result["success"] is True
    assert "settings" in result["connect"]
    assert not _contains_key(result, "values")
    emitted_query = mock_graphql_request.call_args.args[0]
    assert "values" not in emitted_query


async def test_customization_details_omits_activation_codes(
    mock_graphql_request: AsyncMock,
) -> None:
    mock_graphql_request.return_value = {
        "customization": {
            "onboarding": {
                "status": "COMPLETE",
                "isPartnerBuild": False,
                "completed": True,
                "completedAtVersion": "7.2.0",
                "shouldOpen": False,
                "onboardingState": {
                    "registrationState": "REGISTERED",
                    "isRegistered": True,
                    "isFreshInstall": False,
                    "hasActivationCode": False,
                    "activationRequired": False,
                },
            },
            "availableLanguages": [
                {"code": "en_US", "name": "English", "url": "https://example.com/en"}
            ],
        }
    }

    result = await _make_tool()(action="customization", subaction="details")

    assert result["customization"]["onboarding"]["completed"] is True
    assert not _contains_key(result, "activationCode")
    assert (
        not _contains_key(result, "code")
        or result["customization"]["availableLanguages"][0]["code"] == "en_US"
    )
    emitted_query = mock_graphql_request.call_args.args[0]
    assert "activationCode" not in emitted_query
