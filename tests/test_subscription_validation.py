"""Tests for _validate_subscription_query in diagnostics.py.

Security-critical: this function is the only guard against arbitrary GraphQL
operations (mutations, queries) being sent over the WebSocket subscription channel.
"""

import pytest

from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.subscriptions.diagnostics import (
    _ALLOWED_SUBSCRIPTION_NAMES,
    _validate_subscription_query,
)


class TestValidateSubscriptionQueryAllowed:
    """All whitelisted subscription names must be accepted."""

    @pytest.mark.parametrize("sub_name", sorted(_ALLOWED_SUBSCRIPTION_NAMES))
    def test_all_allowed_names_accepted(self, sub_name: str) -> None:
        query = f"subscription {{ {sub_name} {{ data }} }}"
        result = _validate_subscription_query(query)
        assert result == sub_name

    def test_returns_extracted_subscription_name(self) -> None:
        query = "subscription { cpuSubscription { usage } }"
        assert _validate_subscription_query(query) == "cpuSubscription"

    def test_leading_whitespace_accepted(self) -> None:
        query = "  subscription { memorySubscription { free } }"
        assert _validate_subscription_query(query) == "memorySubscription"

    def test_multiline_query_accepted(self) -> None:
        query = "subscription {\n  logFileSubscription {\n    content\n  }\n}"
        assert _validate_subscription_query(query) == "logFileSubscription"

    def test_case_insensitive_subscription_keyword(self) -> None:
        """'SUBSCRIPTION' should be accepted (regex uses IGNORECASE)."""
        query = "SUBSCRIPTION { cpuSubscription { usage } }"
        assert _validate_subscription_query(query) == "cpuSubscription"


class TestValidateSubscriptionQueryForbiddenKeywords:
    """Queries containing 'mutation' or 'query' as standalone keywords must be rejected."""

    def test_mutation_keyword_rejected(self) -> None:
        query = 'mutation { docker { start(id: "abc") } }'
        with pytest.raises(ToolError, match="must be a subscription"):
            _validate_subscription_query(query)

    def test_query_keyword_rejected(self) -> None:
        query = "query { info { os { platform } } }"
        with pytest.raises(ToolError, match="must be a subscription"):
            _validate_subscription_query(query)

    def test_mutation_embedded_in_subscription_rejected(self) -> None:
        """'mutation' anywhere in the string triggers rejection."""
        query = "subscription { cpuSubscription { mutation data } }"
        with pytest.raises(ToolError, match="must be a subscription"):
            _validate_subscription_query(query)

    def test_query_embedded_in_subscription_rejected(self) -> None:
        query = "subscription { cpuSubscription { query data } }"
        with pytest.raises(ToolError, match="must be a subscription"):
            _validate_subscription_query(query)

    def test_mutation_case_insensitive_rejection(self) -> None:
        query = 'MUTATION { docker { start(id: "abc") } }'
        with pytest.raises(ToolError, match="must be a subscription"):
            _validate_subscription_query(query)

    def test_mutation_field_identifier_not_rejected(self) -> None:
        """'mutationField' as an identifier must NOT be rejected — only standalone 'mutation'."""
        # This tests the \b word boundary in _FORBIDDEN_KEYWORDS
        query = "subscription { cpuSubscription { mutationField } }"
        # Should not raise — "mutationField" is an identifier, not the keyword
        result = _validate_subscription_query(query)
        assert result == "cpuSubscription"

    def test_query_field_identifier_not_rejected(self) -> None:
        """'queryResult' as an identifier must NOT be rejected."""
        query = "subscription { cpuSubscription { queryResult } }"
        result = _validate_subscription_query(query)
        assert result == "cpuSubscription"


class TestValidateSubscriptionQueryInvalidFormat:
    """Queries that don't match the expected subscription format must be rejected."""

    def test_empty_string_rejected(self) -> None:
        with pytest.raises(ToolError, match="must start with 'subscription'"):
            _validate_subscription_query("")

    def test_plain_identifier_rejected(self) -> None:
        with pytest.raises(ToolError, match="must start with 'subscription'"):
            _validate_subscription_query("cpuSubscription { usage }")

    def test_missing_operation_body_rejected(self) -> None:
        with pytest.raises(ToolError, match="must start with 'subscription'"):
            _validate_subscription_query("subscription")

    def test_subscription_without_field_rejected(self) -> None:
        """subscription { } with no field name doesn't match the pattern."""
        with pytest.raises(ToolError, match="must start with 'subscription'"):
            _validate_subscription_query("subscription {  }")


class TestValidateSubscriptionQueryUnknownName:
    """Subscription names not in the whitelist must be rejected even if format is valid."""

    def test_unknown_subscription_name_rejected(self) -> None:
        query = "subscription { unknownSubscription { data } }"
        with pytest.raises(ToolError, match="not allowed"):
            _validate_subscription_query(query)

    def test_error_message_includes_allowed_list(self) -> None:
        """Error message must list the allowed subscription names for usability."""
        query = "subscription { badSub { data } }"
        with pytest.raises(ToolError, match="Allowed subscriptions"):
            _validate_subscription_query(query)

    def test_arbitrary_field_name_rejected(self) -> None:
        query = "subscription { users { id email } }"
        with pytest.raises(ToolError, match="not allowed"):
            _validate_subscription_query(query)

    def test_close_but_not_whitelisted_rejected(self) -> None:
        """'cpu' without 'Subscription' suffix is not in the allow-list."""
        query = "subscription { cpu { usage } }"
        with pytest.raises(ToolError, match="not allowed"):
            _validate_subscription_query(query)
