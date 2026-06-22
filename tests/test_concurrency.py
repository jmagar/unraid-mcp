"""Concurrency tests for the autostart double-checked lock and the rate limiter.

Two independent concurrency-safety properties are covered:

1. ``ensure_subscriptions_started`` uses double-checked locking so the
   underlying ``autostart_subscriptions`` fan-out runs at most once even when
   many coroutines race into it concurrently.
2. ``_RateLimiter`` (token bucket) must never over-issue under contention:
   the bucket may go to zero but never negative, and acquiring more tokens
   than the bucket capacity must take at least the refill-bounded time.
"""

import asyncio
import contextlib
import time
from unittest.mock import AsyncMock, patch

from unraid_mcp.core.client import _RateLimiter
from unraid_mcp.subscriptions import resources as res


# ---------------------------------------------------------------------------
# Autostart double-checked lock
# ---------------------------------------------------------------------------


class TestAutostartDoubleCheckedLock:
    """ensure_subscriptions_started must fan out exactly once under a stampede."""

    async def test_autostart_runs_once_under_concurrency(self) -> None:
        original_flag = res._subscriptions_started
        try:
            with patch.object(
                res, "autostart_subscriptions", new_callable=AsyncMock
            ) as mock_autostart:
                # Reset the latch so the slow-path actually runs.
                res._subscriptions_started = False

                await asyncio.gather(*[res.ensure_subscriptions_started() for _ in range(20)])

                # Despite 20 racing callers, the fan-out fired exactly once.
                mock_autostart.assert_awaited_once()
                # And the flag is latched so future callers fast-path out.
                assert res._subscriptions_started is True
        finally:
            res._subscriptions_started = original_flag

    async def test_fast_path_skips_autostart_when_already_started(self) -> None:
        """When the flag is already latched, no autostart is attempted at all."""
        original_flag = res._subscriptions_started
        try:
            with patch.object(
                res, "autostart_subscriptions", new_callable=AsyncMock
            ) as mock_autostart:
                res._subscriptions_started = True

                await asyncio.gather(*[res.ensure_subscriptions_started() for _ in range(10)])

                mock_autostart.assert_not_awaited()
        finally:
            res._subscriptions_started = original_flag


# ---------------------------------------------------------------------------
# Rate limiter under contention
# ---------------------------------------------------------------------------


class TestRateLimiterUnderContention:
    """The token bucket must never over-issue tokens under concurrent acquire()."""

    async def test_bucket_never_goes_negative(self) -> None:
        """Gathering more acquires than capacity must keep tokens >= 0 throughout."""
        # Small, fast bucket: 5 tokens, fast refill so the test stays quick.
        limiter = _RateLimiter(max_tokens=5, refill_rate=50.0)

        observed_min = float("inf")
        original_refill = limiter._refill

        def _spy_refill() -> None:
            nonlocal observed_min
            original_refill()
            observed_min = min(observed_min, limiter.tokens)

        with patch.object(limiter, "_refill", side_effect=_spy_refill):
            # 25 acquires against a 5-token bucket forces heavy contention.
            await asyncio.gather(*[limiter.acquire() for _ in range(25)])

        # The bucket may hit zero but must never be over-issued (negative).
        assert limiter.tokens >= 0.0
        assert observed_min >= 0.0

    async def test_does_not_over_issue_within_initial_capacity(self) -> None:
        """With refill effectively frozen, only `max_tokens` acquires complete."""
        max_tokens = 4
        limiter = _RateLimiter(max_tokens=max_tokens, refill_rate=1.0)

        # Freeze time so no tokens refill during the window: every acquire beyond
        # the initial capacity would have to wait on refill (which never advances).
        frozen = time.monotonic()
        with patch("unraid_mcp.core.client.time.monotonic", return_value=frozen):
            # Exactly max_tokens acquires should complete instantly without waiting.
            await asyncio.wait_for(
                asyncio.gather(*[limiter.acquire() for _ in range(max_tokens)]),
                timeout=2.0,
            )
            # The bucket is now drained — never negative.
            assert limiter.tokens >= 0.0
            assert limiter.tokens < 1.0

            # One more acquire must block (no refill while time is frozen).
            with_extra = asyncio.ensure_future(limiter.acquire())
            await asyncio.sleep(0)  # let it run up to the wait
            assert not with_extra.done()
            with_extra.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await with_extra

    async def test_refill_bounded_total_time(self) -> None:
        """Acquiring beyond capacity must take at least the refill-bounded time."""
        # 2 tokens, slow-ish refill. Acquiring 4 needs 2 refilled tokens, each
        # taking 1/refill_rate seconds -> a measurable, deterministic lower bound.
        refill_rate = 20.0  # tokens/sec -> 0.05s per refilled token
        limiter = _RateLimiter(max_tokens=2, refill_rate=refill_rate)

        start = time.monotonic()
        await asyncio.gather(*[limiter.acquire() for _ in range(4)])
        elapsed = time.monotonic() - start

        # 2 tokens are immediate; the other 2 must wait on refill. Lower bound is
        # ~2 / refill_rate = 0.1s. Use a conservative fraction to avoid flake.
        min_expected = (2 / refill_rate) * 0.8
        assert elapsed >= min_expected
        assert limiter.tokens >= 0.0
