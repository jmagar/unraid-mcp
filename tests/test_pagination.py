"""Unit tests for the shared client-side list-capping helper."""

from unraid_mcp.core.pagination import DEFAULT_LIST_LIMIT, cap_list


def test_under_limit_returns_all_not_truncated():
    items = [1, 2, 3]
    capped, meta = cap_list(items, limit=10)
    assert capped == items
    assert meta == {"returned": 3, "total": 3, "truncated": False}


def test_over_limit_truncates_with_hint():
    items = list(range(100))
    capped, meta = cap_list(items, limit=10)
    assert capped == list(range(10))
    assert meta["returned"] == 10
    assert meta["total"] == 100
    assert meta["truncated"] is True
    assert "limit=" in meta["hint"]


def test_none_limit_applies_default():
    items = list(range(DEFAULT_LIST_LIMIT + 5))
    capped, meta = cap_list(items, limit=None)
    assert len(capped) == DEFAULT_LIST_LIMIT
    assert meta["truncated"] is True
    assert meta["total"] == DEFAULT_LIST_LIMIT + 5


def test_zero_limit_returns_everything():
    items = list(range(200))
    capped, meta = cap_list(items, limit=0)
    assert capped == items
    assert meta["truncated"] is False
    assert meta["returned"] == 200


def test_negative_limit_returns_everything():
    items = list(range(30))
    capped, meta = cap_list(items, limit=-1)
    assert capped == items
    assert meta["truncated"] is False


def test_exactly_at_limit_not_truncated():
    items = list(range(10))
    capped, meta = cap_list(items, limit=10)
    assert capped == items
    assert meta["truncated"] is False


def test_empty_list():
    capped, meta = cap_list([], limit=10)
    assert capped == []
    assert meta == {"returned": 0, "total": 0, "truncated": False}


def test_custom_default():
    items = list(range(20))
    capped, meta = cap_list(items, limit=None, default=5)
    assert len(capped) == 5
    assert meta["truncated"] is True
