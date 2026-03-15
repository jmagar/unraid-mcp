"""Interactive credential setup via MCP elicitation.

When UNRAID_API_URL or UNRAID_API_KEY are absent, tools call
`elicit_and_configure(ctx)` to collect them from the user and persist
them to ~/.unraid-mcp/.env with restricted permissions.
"""

from __future__ import annotations

from dataclasses import dataclass

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


async def elicit_destructive_confirmation(
    ctx: Context | None, action: str, description: str
) -> bool:
    """Prompt the user to confirm a destructive action via MCP elicitation.

    Args:
        ctx: The MCP context for elicitation. If None, returns False immediately.
        action: The action name (for display in the prompt).
        description: Human-readable description of what the action will do.

    Returns:
        True if the user accepted, False if declined, cancelled, or no context.
    """
    if ctx is None:
        logger.warning(
            "Cannot elicit confirmation for '%s': no MCP context available. "
            "Re-run with confirm=True to bypass elicitation.",
            action,
        )
        return False

    try:
        result = await ctx.elicit(
            message=(
                f"**Confirm destructive action: `{action}`**\n\n"
                f"{description}\n\n"
                "Are you sure you want to proceed?"
            ),
            response_type=bool,
        )
    except NotImplementedError:
        logger.warning(
            "MCP client does not support elicitation for action '%s'. "
            "Re-run with confirm=True to bypass.",
            action,
        )
        return False

    if result.action != "accept":
        logger.info("Destructive action '%s' declined by user (%s).", action, result.action)
        return False

    confirmed: bool = result.data
    if not confirmed:
        logger.info("Destructive action '%s' not confirmed by user.", action)
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
            "Run unraid_health action=setup to configure credentials."
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
            "Use unraid_health action=setup or create %s manually.",
            CREDENTIALS_ENV_PATH,
        )
        return False

    if result.action != "accept":
        logger.warning("Credential elicitation %s — server remains unconfigured.", result.action)
        return False

    api_url: str = result.data.api_url.rstrip("/")
    api_key: str = result.data.api_key.strip()

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
