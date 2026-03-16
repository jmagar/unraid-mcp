"""Interactive credential setup via MCP elicitation.

When UNRAID_API_URL or UNRAID_API_KEY are absent, tools call
`elicit_and_configure(ctx)` to collect them from the user and persist
them to ~/.unraid-mcp/.env with restricted permissions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from fastmcp import Context

from ..config.logging import logger
from ..config.settings import (
    CREDENTIALS_DIR,
    CREDENTIALS_ENV_PATH,
    PROJECT_ROOT,
    apply_runtime_config,
)


@dataclass
class _UnraidCredentials:
    api_url: str
    api_key: str


async def elicit_reset_confirmation(ctx: Context | None, current_url: str) -> bool:
    """Ask the user whether to overwrite already-working credentials.

    Args:
        ctx: The MCP context for elicitation. If None, returns False immediately.
        current_url: The currently configured URL (displayed for context).

    Returns:
        True if the user confirmed the reset, False otherwise.
    """
    if ctx is None:
        return False

    try:
        result = await ctx.elicit(
            message=(
                "Credentials are already configured and working.\n\n"
                f"**Current URL:** `{current_url}`\n\n"
                "Do you want to reset your API URL and key?"
            ),
            response_type=bool,
        )
    except NotImplementedError:
        # Client doesn't support elicitation — treat as "proceed with reset" so
        # non-interactive clients (stdio, CI) are not permanently blocked from
        # reconfiguring credentials.
        logger.warning(
            "MCP client does not support elicitation for reset confirmation — proceeding with reset."
        )
        return True

    if result.action != "accept":
        logger.info("Credential reset declined by user (%s).", result.action)
        return False

    confirmed: bool = result.data  # type: ignore[union-attr]
    return confirmed


async def elicit_and_configure(ctx: Context | None) -> bool:
    """Prompt the user for Unraid credentials via MCP elicitation.

    Writes accepted credentials to CREDENTIALS_ENV_PATH and applies them
    to the running process via apply_runtime_config().

    Args:
        ctx: The MCP context for elicitation. If None, returns False immediately
             (no context available to prompt the user).

    Returns:
        True if credentials were accepted and applied, False if declined/cancelled
        or if the MCP client does not support elicitation.
    """
    if ctx is None:
        logger.warning(
            "Cannot elicit credentials: no MCP context available. "
            "Run unraid(action=health, subaction=setup) to configure credentials."
        )
        return False

    try:
        result = await ctx.elicit(
            message=(
                "Unraid MCP needs your Unraid server credentials to connect.\n\n"
                "• **API URL**: Your Unraid GraphQL endpoint "
                "(e.g. `https://10-1-0-2.xxx.myunraid.net:31337`)\n"
                "• **API Key**: Found in Unraid → Settings → Management Access → API Keys"
            ),
            response_type=_UnraidCredentials,
        )
    except NotImplementedError:
        logger.warning(
            "MCP client does not support elicitation. "
            "Use unraid(action=health, subaction=setup) or create %s manually.",
            CREDENTIALS_ENV_PATH,
        )
        return False

    if result.action != "accept":
        logger.warning("Credential elicitation %s — server remains unconfigured.", result.action)
        return False

    api_url: str = result.data.api_url.rstrip("/")  # type: ignore[union-attr]
    api_key: str = result.data.api_key.strip()  # type: ignore[union-attr]

    _write_env(api_url, api_key)
    apply_runtime_config(api_url, api_key)

    logger.info("Credentials configured via elicitation and persisted to %s.", CREDENTIALS_ENV_PATH)
    return True


def _write_env(api_url: str, api_key: str) -> None:
    """Write or update credentials in CREDENTIALS_ENV_PATH.

    Creates CREDENTIALS_DIR (mode 700) if needed. On first run, seeds from
    .env.example to preserve comments and structure. Sets file mode to 600.
    """
    # Ensure directory exists with restricted permissions (chmod after to bypass umask)
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_DIR.chmod(0o700)

    if CREDENTIALS_ENV_PATH.exists():
        template_lines = CREDENTIALS_ENV_PATH.read_text().splitlines()
    else:
        example_path = PROJECT_ROOT / ".env.example"
        template_lines = example_path.read_text().splitlines() if example_path.exists() else []

    # Replace credentials in-place; append at end if not found in template
    url_written = False
    key_written = False
    new_lines: list[str] = []
    for line in template_lines:
        stripped = line.strip()
        if stripped.startswith("UNRAID_API_URL="):
            new_lines.append(f"UNRAID_API_URL={api_url}")
            url_written = True
        elif stripped.startswith("UNRAID_API_KEY="):
            new_lines.append(f"UNRAID_API_KEY={api_key}")
            key_written = True
        else:
            new_lines.append(line)

    # If not found in template (empty or missing keys), append at end
    if not url_written:
        new_lines.append(f"UNRAID_API_URL={api_url}")
    if not key_written:
        new_lines.append(f"UNRAID_API_KEY={api_key}")

    CREDENTIALS_ENV_PATH.write_text("\n".join(new_lines) + "\n")
    CREDENTIALS_ENV_PATH.chmod(0o600)
    logger.info("Credentials written to %s (mode 600)", CREDENTIALS_ENV_PATH)
