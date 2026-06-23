"""Safety contracts for direct query-root read subactions."""

from typing import Any
from unittest.mock import AsyncMock

import pytest
from conftest import make_tool_fn


pytestmark = pytest.mark.asyncio


def _make_tool() -> Any:
    return make_tool_fn("unraid_mcp.tools.unraid", "register_unraid_tool", "unraid")


def _dict_keys(value: Any) -> set[str]:
    if not isinstance(value, dict):
        return set()
    return set(value)


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
    assert "apikey" not in _dict_keys(result["server"])
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
    assert "values" not in _dict_keys(result["connect"]["settings"])
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
    assert "activationCode" not in _dict_keys(result["customization"]["onboarding"])
    assert result["customization"]["availableLanguages"][0]["code"] == "en_US"
    emitted_query = mock_graphql_request.call_args.args[0]
    assert "activationCode" not in emitted_query
