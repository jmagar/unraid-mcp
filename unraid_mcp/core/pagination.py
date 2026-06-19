"""Client-side list capping for tool responses.

The Unraid GraphQL API exposes no server-side pagination for most collections
(only ``notifications.list`` accepts ``offset``/``limit``). To keep large lists
from flooding an agent's context window, list subactions slice the result in the
handler and surface a small metadata dict describing the truncation.

This is the shared primitive every list subaction should use so the truncation
signal is consistent across the whole tool surface.
"""

from typing import Any


# Default number of items returned when the caller does not specify a limit.
DEFAULT_LIST_LIMIT: int = 50


def cap_list(
    items: list[Any], limit: int | None, *, default: int = DEFAULT_LIST_LIMIT
) -> tuple[list[Any], dict[str, Any]]:
    """Cap a list client-side and describe the result.

    Args:
        items: The full list returned by the upstream query.
        limit: Caller-requested maximum. ``None`` applies ``default``. A value
            ``<= 0`` disables capping (returns everything) — use it as an
            explicit "give me all" escape hatch.
        default: Limit applied when ``limit`` is ``None``.

    Returns:
        A ``(capped_items, meta)`` tuple. ``meta`` always carries ``returned``,
        ``total`` and ``truncated``; when truncated it also carries a ``hint``
        telling the agent how to widen the window. Surface ``meta`` in the
        subaction response (e.g. under a ``page`` key) so the agent knows whether
        more rows exist.
    """
    total = len(items)
    effective = default if limit is None else limit

    if effective is not None and effective > 0 and total > effective:
        return items[:effective], {
            "returned": effective,
            "total": total,
            "truncated": True,
            "hint": (
                f"showing {effective} of {total} items; pass a larger limit= "
                "to see more (limit=0 for all)"
            ),
        }

    return items, {"returned": total, "total": total, "truncated": False}
