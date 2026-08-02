"""Tests for the Alpha Vantage provider. **No test here touches the network.**

Every payload below is a real shape observed from the live endpoint on
2026-07-29 (keys removed), not an invented one — the point is that the
classifier handles what the provider *actually* sends. Alpha Vantage answers
**HTTP 200 for every failure mode**, so the body is the only signal.

The split-adjustment tests use NVDA's real 10:1 of 2024-06-10 and its real
closes, because that is the one transformation HD-01 turns on and an invented
number would prove nothing.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from tools.research.providers import alphavantage as av

# --- Real observed payloads, keys redacted -------------------------------------

RATE_LIMITED = {
    "Information": (
        "Thank you for using Alpha Vantage! Please consider spreading out your "
        "free API requests more sparingly (1 request per second). You may "
        "subscribe to any of the premium plans at "
        "https://www.alphavantage.co/premium/ to lift the free key rate limit "
        "(25 requests per day)."
    )
}

PREMIUM_REQUIRED = {
    "Information": (
        "Thank you for using Alpha Vantage! The outputsize=full parameter value "
        "is a premium feature for the TIME_SERIES_DAILY endpoint. You may "
        "subscribe to any of the premium plans at "
        "https://www.alphavantage.co/premium/ to instantly unlock all premium "
        "features"
    )
}

INVALID_SYMBOL = {
    "Error Message": (
        "Invalid API call. Please retry or visit the documentation for "
        "TIME_SERIES_DAILY_ADJUSTED."
    )
}


def bar(o, h, lo, c, v="1000000", split="1.0", adj=None):
    return {
        "1. open": str(o), "2. high": str(h), "3. low": str(lo), "4. close": str(c),
        "5. adjusted close": str(adj if adj is not None else c),
        "6. volume": str(v), "7. dividend amount": "0.0000",
        "8. split coefficient": str(split),
    }


GOOD = {
    "Meta Data": {"2. Symbol": "AAPL", "3. Last Refreshed": "2026-07-28", "4. Output Size": "Full size"},
    "Time Series (Daily)": {
        "2026-07-27": bar(334.54, 339.57, 333.00, 338.10),
        "2026-07-28": bar(340.03, 342.89, 335.60, 340.08),
    },
}

#: NVDA's real 10:1. Raw closes are as-traded either side of the split.
NVDA_SPLIT = {
    "Meta Data": {"2. Symbol": "NVDA", "3. Last Refreshed": "2024-06-10", "4. Output Size": "Full size"},
    "Time Series (Daily)": {
        # pre-split, as-traded; vendor's dividend-adjusted close is 120.68
        "2024-06-07": bar(1206.00, 1210.00, 1200.00, 1208.88, v="10000000", adj=120.68274034078189),
        # split effective; coefficient lives on this bar
        "2024-06-10": bar(120.00, 123.10, 118.00, 121.79, v="100000000", split="10.0",
                          adj=121.58320880570302),
    },
}


class Classification(unittest.TestCase):
    """The provider returns 200 for refusals, so the body must be classified."""

    def test_rate_limit_is_distinguished_from_a_bad_symbol(self):
        with self.assertRaises(av.RateLimited):
            av.classify(RATE_LIMITED, "AAPL")

    def test_premium_gate_is_not_reported_as_a_rate_limit(self):
        # Both mention "premium plans"; only one is retryable. Misclassifying
        # this would make the runner back off and retry forever.
        with self.assertRaises(av.PremiumRequired):
            av.classify(PREMIUM_REQUIRED, "MSFT")

    def test_invalid_symbol(self):
        with self.assertRaises(av.InvalidSymbol):
            av.classify(INVALID_SYMBOL, "ZZZZNOTREAL")

    def test_an_unrecognised_advisory_is_still_a_refusal(self):
        # Never treat an unknown envelope as data — that is how a refusal
        # becomes a silently empty series.
        with self.assertRaises(av.ProviderError):
            av.classify({"Note": "something new the provider started sending"}, "X")

    def test_missing_series_key(self):
        with self.assertRaises(av.MalformedResponse):
            av.classify({"Meta Data": {}}, "X")

    def test_a_good_payload_classifies_clean(self):
        av.classify(GOOD, "AAPL")  # must not raise


class SplitAdjustment(unittest.TestCase):
    """HD-01's basis: split-adjusted, dividend-UNadjusted."""

    def test_prices_before_a_split_are_divided_by_its_coefficient(self):
        s = av.normalize(NVDA_SPLIT, "NVDA")
        pre, post = s.bars[0], s.bars[1]
        # 1208.88 / 10 — the ruled basis
        self.assertAlmostEqual(pre.close, 120.888, places=6)
        self.assertAlmostEqual(pre.split_factor, 10.0)
        # the split bar itself is already post-split and must not move
        self.assertAlmostEqual(post.close, 121.79, places=6)
        self.assertAlmostEqual(post.split_factor, 1.0)

    def test_the_dividend_adjusted_close_is_NOT_used(self):
        # This is the whole point of HD-01. The vendor's adjusted close for
        # 2024-06-07 is 120.68...; split-only gives 120.888. If the two ever
        # coincide this test is worthless, so assert they differ.
        s = av.normalize(NVDA_SPLIT, "NVDA")
        vendor_adjusted = 120.68274034078189
        self.assertNotAlmostEqual(s.bars[0].close, vendor_adjusted, places=3)
        self.assertAlmostEqual(s.bars[0].close, 1208.88 / 10.0, places=9)

    def test_volume_scales_the_other_way(self):
        s = av.normalize(NVDA_SPLIT, "NVDA")
        self.assertEqual(s.bars[0].volume, 100000000)  # 10,000,000 x 10

    def test_splits_applied_are_recorded_for_audit(self):
        s = av.normalize(NVDA_SPLIT, "NVDA")
        self.assertEqual(s.splits_applied, (("2024-06-10", 10.0),))
        self.assertEqual(s.adjustment_basis, "SPLIT_ADJUSTED_DIVIDEND_UNADJUSTED")

    def test_a_series_with_no_splits_is_untouched(self):
        s = av.normalize(GOOD, "AAPL")
        self.assertEqual(s.splits_applied, ())
        self.assertAlmostEqual(s.bars[-1].close, 340.08)
        self.assertTrue(all(b.split_factor == 1.0 for b in s.bars))

    def test_ordering_is_ascending_after_a_reverse_pass(self):
        # The adjustment walks newest->oldest; the output must still ascend.
        s = av.normalize(NVDA_SPLIT, "NVDA")
        self.assertEqual([b.date for b in s.bars], ["2024-06-07", "2024-06-10"])


class Normalization(unittest.TestCase):
    def test_symbol_mismatch_is_rejected(self):
        payload = json.loads(json.dumps(GOOD))
        payload["Meta Data"]["2. Symbol"] = "MSFT"
        with self.assertRaises(av.MalformedResponse):
            av.normalize(payload, "AAPL")

    def test_a_single_bad_bar_rejects_the_whole_series(self):
        # Dropping it would leave a hole in a causal series.
        payload = json.loads(json.dumps(GOOD))
        payload["Time Series (Daily)"]["2026-07-28"]["3. low"] = "-1"
        with self.assertRaises(av.MalformedResponse):
            av.normalize(payload, "AAPL")

    def test_low_above_high_is_rejected(self):
        payload = json.loads(json.dumps(GOOD))
        payload["Time Series (Daily)"]["2026-07-28"]["3. low"] = "999999"
        with self.assertRaises(av.MalformedResponse):
            av.normalize(payload, "AAPL")

    def test_a_missing_split_coefficient_is_rejected(self):
        # Without it the ruled basis cannot be constructed, so proceeding would
        # silently produce raw prices — the basis HD-01 rejects.
        payload = json.loads(json.dumps(GOOD))
        del payload["Time Series (Daily)"]["2026-07-28"]["8. split coefficient"]
        with self.assertRaises(av.MalformedResponse):
            av.normalize(payload, "AAPL")

    def test_a_non_positive_split_coefficient_is_rejected(self):
        payload = json.loads(json.dumps(NVDA_SPLIT))
        payload["Time Series (Daily)"]["2024-06-10"]["8. split coefficient"] = "0"
        with self.assertRaises(av.MalformedResponse):
            av.normalize(payload, "NVDA")


class SecretHandling(unittest.TestCase):
    def test_missing_key_raises_and_names_the_env_var(self):
        saved = os.environ.pop(av.API_KEY_ENV, None)
        try:
            with self.assertRaises(av.MissingApiKey) as ctx:
                av.api_key()
            self.assertIn(av.API_KEY_ENV, str(ctx.exception))
        finally:
            if saved is not None:
                os.environ[av.API_KEY_ENV] = saved

    def test_redaction_removes_the_key(self):
        secret = "SUPERSECRETKEY01"
        url = av._request_url("AAPL", secret, "full")
        self.assertIn(secret, url)  # it is in the URL by construction...
        self.assertNotIn(secret, av._redact(url, secret))  # ...and never escapes

    def test_the_cache_never_stores_a_key_or_a_url(self):
        s = av.normalize(GOOD, "AAPL")
        with tempfile.TemporaryDirectory() as tmp:
            blob = av.store_cached(Path(tmp), s).read_text()
        self.assertNotIn("apikey", blob.lower())
        self.assertNotIn("alphavantage.co", blob)
        self.assertNotIn("http", blob)


class Caching(unittest.TestCase):
    def test_round_trip_preserves_the_basis(self):
        s = av.normalize(NVDA_SPLIT, "NVDA")
        with tempfile.TemporaryDirectory() as tmp:
            av.store_cached(Path(tmp), s)
            back = av.load_cached(Path(tmp), "NVDA")
        self.assertIsNotNone(back)
        self.assertEqual(back.adjustment_basis, av.ADJUSTMENT_BASIS)
        self.assertAlmostEqual(back.bars[0].close, 120.888, places=6)

    def test_an_entry_on_a_stale_basis_is_discarded(self):
        # A cache written before the HD-01 fix must not poison a later run.
        s = av.normalize(GOOD, "AAPL")
        with tempfile.TemporaryDirectory() as tmp:
            path = av.store_cached(Path(tmp), s)
            blob = json.loads(path.read_text())
            blob["adjustment_basis"] = "RAW_UNADJUSTED"
            path.write_text(json.dumps(blob))
            self.assertIsNone(av.load_cached(Path(tmp), "AAPL"))

    def test_a_corrupt_entry_returns_none_rather_than_raising(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "AAPL.json").write_text("{not json")
            self.assertIsNone(av.load_cached(Path(tmp), "AAPL"))

    def test_a_cache_hit_makes_no_request(self):
        s = av.normalize(GOOD, "AAPL")

        def explode(*_a, **_k):  # pragma: no cover - must never be called
            raise AssertionError("network was used despite a valid cache entry")

        with tempfile.TemporaryDirectory() as tmp:
            av.store_cached(Path(tmp), s)
            f = av.Fetcher(Path(tmp), opener=explode)
            got, from_cache = f.fetch("AAPL")
        self.assertTrue(from_cache)
        self.assertEqual(f.requests_made, 0)
        self.assertEqual(len(got.bars), 2)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
