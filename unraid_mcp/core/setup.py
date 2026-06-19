"""Non-interactive credential setup for the Unraid MCP server.

Configuration is delivered by the plugin's ``userConfig`` form (Claude Code
injects it as ``CLAUDE_PLUGIN_OPTION_*`` environment variables) or by a
hand-edited ``~/.unraid-mcp/.env``. This module maps those plugin options to
the canonical ``.env`` file with restricted permissions, mirroring the
``setup plugin-hook`` pattern used across the rmcp-template Rust servers.

There is no interactive elicitation: the plugin config form is the UI, and
``run_plugin_hook()`` persists it to disk so the server, the CLI, and Docker
all read the same source of truth at startup.
"""

from __future__ import annotations

import json
import os

from ..config.logging import logger
from ..config.settings import (
    CREDENTIALS_DIR,
    CREDENTIALS_ENV_PATH,
    PROJECT_ROOT,
)


# Maps Claude Code plugin-option env vars -> canonical server env vars.
# Mirrors rmcp-template's env_registry plugin_option_mappings().
PLUGIN_OPTION_MAP: dict[str, str] = {
    "CLAUDE_PLUGIN_OPTION_UNRAID_API_URL": "UNRAID_API_URL",
    "CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY": "UNRAID_API_KEY",
}


def _safe_env_value(value: str) -> str | None:
    """Return the value if safe to write to a .env file, else None.

    Rejects empty values and values containing newlines, carriage returns, or
    NUL bytes (which could inject extra .env lines). Mirrors apply_plugin_options
    in the Rust template.
    """
    if not value:
        return None
    if any(ch in value for ch in ("\n", "\r", "\0")):
        return None
    return value


def apply_plugin_options() -> dict[str, str]:
    """Resolve canonical credentials from CLAUDE_PLUGIN_OPTION_* env vars.

    Returns a dict of ``{canonical_env_name: value}`` for every plugin option
    that is present and safe. Missing, empty, or unsafe options are skipped.
    The URL has any trailing slash stripped; all values are whitespace-trimmed.
    """
    resolved: dict[str, str] = {}
    for option, canonical in PLUGIN_OPTION_MAP.items():
        raw = os.environ.get(option)
        if raw is None:
            continue
        safe = _safe_env_value(raw.strip())
        if safe is None:
            continue
        resolved[canonical] = safe.rstrip("/") if canonical == "UNRAID_API_URL" else safe
    return resolved


def run_plugin_hook() -> int:
    """Persist plugin userConfig credentials to CREDENTIALS_ENV_PATH.

    Designed to run from the plugin's SessionStart / ConfigChange hooks. When
    both URL and key are supplied via CLAUDE_PLUGIN_OPTION_*, writes them to
    ``~/.unraid-mcp/.env`` (mode 600). Always returns 0 (advisory) so a missing
    config never blocks the session — the server reports the unconfigured state
    at request time instead. Emits a JSON report to stdout.
    """
    resolved = apply_plugin_options()
    report: dict[str, object] = {
        "ran_repair": False,
        "env_path": str(CREDENTIALS_ENV_PATH),
        "advisory_failures": [],
    }

    api_url = resolved.get("UNRAID_API_URL")
    api_key = resolved.get("UNRAID_API_KEY")

    if api_url and api_key:
        try:
            _write_env(api_url, api_key)
            report["ran_repair"] = True
            logger.info("Plugin setup hook wrote credentials to %s", CREDENTIALS_ENV_PATH)
        except OSError as e:
            # Record the write failure in the advisory channel rather than letting it
            # escape — the documented contract is "always returns 0" so the hook never
            # blocks a session. The server still reports unconfigured at request time.
            report["advisory_failures"] = [
                f"Failed to write {CREDENTIALS_ENV_PATH}: {type(e).__name__}: {e}"
            ]
            logger.error(
                "Plugin setup hook failed to write %s: %s",
                CREDENTIALS_ENV_PATH,
                e,
                exc_info=True,
            )
    else:
        # Distinguish "not supplied" from "supplied but rejected as unsafe": a present
        # env var that failed _safe_env_value is absent from `resolved` but should still
        # be surfaced so the operator knows why it was dropped.
        failures: list[str] = []
        for option, canonical in PLUGIN_OPTION_MAP.items():
            if canonical in resolved:
                continue
            if option in os.environ:
                # Present (key set) but absent from `resolved` → empty or unsafe value.
                # Use key presence, not truthiness, so an explicit empty value is
                # classified as "rejected", not "not supplied".
                failures.append(
                    f"{canonical} was supplied but rejected (empty or unsafe characters) — "
                    "check the value in the plugin config form."
                )
            else:
                failures.append(
                    f"{canonical} not supplied via plugin userConfig — set it in the plugin "
                    f"config form or edit {CREDENTIALS_ENV_PATH} directly."
                )
        report["advisory_failures"] = failures
        logger.info(
            "Plugin setup hook: credentials not fully supplied; no .env written. %s",
            " ".join(failures),
        )

    print(json.dumps(report, indent=2))
    return 0


def _dotenv_value(value: str) -> str:
    """Render a value for a .env assignment, quoting only when necessary.

    Plain values (the common case — alphanumeric keys, scheme://host URLs) are
    written unquoted. Values containing whitespace or characters that would break
    unquoted parsing (`#`, quotes, backslash) are double-quoted with backslash and
    double-quote escaped, so they round-trip through python-dotenv and the skill's
    load-env.sh parser. Mirrors rmcp-template's dotenv_value.
    """
    if value and not any(ch in value for ch in (" ", "\t", "#", '"', "'", "\\")):
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


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
            new_lines.append(f"UNRAID_API_URL={_dotenv_value(api_url)}")
            url_written = True
        elif stripped.startswith("UNRAID_API_KEY="):
            new_lines.append(f"UNRAID_API_KEY={_dotenv_value(api_key)}")
            key_written = True
        else:
            new_lines.append(line)

    # If not found in template (empty or missing keys), append at end
    if not url_written:
        new_lines.append(f"UNRAID_API_URL={_dotenv_value(api_url)}")
    if not key_written:
        new_lines.append(f"UNRAID_API_KEY={_dotenv_value(api_key)}")

    # Atomic write: write to tmp file, set permissions, then rename into place.
    # os.replace is atomic on POSIX — prevents a crash from leaving a partial .env.
    tmp_path = CREDENTIALS_ENV_PATH.with_suffix(".tmp")
    try:
        tmp_path.write_text("\n".join(new_lines) + "\n")
        tmp_path.chmod(0o600)
        os.replace(tmp_path, CREDENTIALS_ENV_PATH)  # noqa: PTH105
    finally:
        # Clean up tmp on failure (may not exist if os.replace succeeded). Swallow any
        # cleanup error so it can't mask the real write exception propagating from try.
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError as cleanup_err:
            logger.warning("Could not remove temp env file %s: %s", tmp_path, cleanup_err)
    logger.info("Credentials written to %s (mode 600)", CREDENTIALS_ENV_PATH)
