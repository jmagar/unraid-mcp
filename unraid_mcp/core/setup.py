"""Interactive credential setup via MCP elicitation.

When UNRAID_API_URL or UNRAID_API_KEY are absent, tools call
`elicit_and_configure(ctx)` to collect them from the user and persist
them to .env in the server root directory.
"""

from __future__ import annotations

from dataclasses import dataclass

from fastmcp import Context

from ..config.logging import logger
from ..config.settings import PROJECT_ROOT, apply_runtime_config


@dataclass
class _UnraidCredentials:
    api_url: str
    api_key: str


async def elicit_and_configure(ctx: Context) -> bool:
    """Prompt the user for Unraid credentials via MCP elicitation.

    Writes accepted credentials to .env in PROJECT_ROOT and applies them
    to the running process via apply_runtime_config().

    Returns:
        True if credentials were accepted and applied, False if declined/cancelled.
    """
    result = await ctx.elicit(
        message=(
            "Unraid MCP needs your Unraid server credentials to connect.\n\n"
            "• **API URL**: Your Unraid GraphQL endpoint "
            "(e.g. `https://10-1-0-2.xxx.myunraid.net:31337`)\n"
            "• **API Key**: Found in Unraid → Settings → Management Access → API Keys"
        ),
        response_type=_UnraidCredentials,
    )

    if result.action != "accept":
        logger.warning("Credential elicitation %s — server remains unconfigured.", result.action)
        return False

    api_url: str = result.data.api_url.rstrip("/")
    api_key: str = result.data.api_key.strip()

    _write_env(api_url, api_key)
    apply_runtime_config(api_url, api_key)

    logger.info("Credentials configured via elicitation and persisted to .env.")
    return True


def _write_env(api_url: str, api_key: str) -> None:
    """Write or update .env in PROJECT_ROOT with credential values.

    Preserves any existing lines that are not UNRAID_API_URL or UNRAID_API_KEY.
    """
    env_path = PROJECT_ROOT / ".env"
    existing_lines: list[str] = []

    if env_path.exists():
        for line in env_path.read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("UNRAID_API_URL=") or stripped.startswith("UNRAID_API_KEY="):
                continue  # Will be replaced below
            existing_lines.append(line)

    new_lines = [
        f"UNRAID_API_URL={api_url}",
        f"UNRAID_API_KEY={api_key}",
        *existing_lines,
    ]
    env_path.write_text("\n".join(new_lines) + "\n")
    logger.debug("Wrote credentials to %s", env_path)
