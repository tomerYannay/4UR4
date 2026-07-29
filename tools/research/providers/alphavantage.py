"""Alpha Vantage TIME_SERIES_DAILY_ADJUSTED fetch, validation, split adjustment and cache.

**SURVIVOR-BIASED EXPLORATORY REAL-MARKET VALIDATION.** Authorized by HD-26.
This lives under ``tools/`` — deliberately NOT a product-code directory — so no
GOV-015 scope change was needed or made. This is **not** HD-06: no provider is selected for production, no
recurring spend is authorized, and nothing here may be cited as a Phase-1 or
Phase-4 increment.

WHY THE *ADJUSTED* ENDPOINT, AND WHY NOT ITS ADJUSTED CLOSE
-----------------------------------------------------------
HD-01 rules the price basis: **split-adjusted, dividend-UNadjusted** ("as-traded"),
and the engine enforces it as a precondition — ``Provenance.ACCEPTED_BASIS ==
"SPLIT_ADJUSTED_DIVIDEND_UNADJUSTED"``. HD-01 rejects raw unadjusted explicitly,
because *"splits inject false ATHs/breakouts"*.

That makes ``TIME_SERIES_DAILY`` unusable: it returns raw OHLC with **no split
coefficient**, so the ruled basis cannot be reconstructed from it at all. A 10:1
split would look like a 90% crash and would reset the all-time high.

``TIME_SERIES_DAILY_ADJUSTED`` returns raw OHLC **plus** ``8. split coefficient``,
which is exactly the missing ingredient. So this module:

* takes ``1. open`` / ``2. high`` / ``3. low`` / ``4. close`` — these are **raw,
  as-traded** (verified: NVDA closes 1208.88 on 2024-06-07 and 121.79 on
  2024-06-10 across its 10:1);
* divides them by the **cumulative product of every split occurring after that
  bar**, giving split-adjusted prices; and
* **never reads ``5. adjusted close``**, which is dividend-adjusted and is the
  basis HD-01 rejected.

Verified end to end: NVDA raw 1208.88 on 2024-06-07 becomes 120.888 under
split-only adjustment, where the vendor's dividend-adjusted close is 120.68. The
difference is the dividend stream, and HD-01 says it must not be there.

SECRET HANDLING — the whole of it
---------------------------------
* The key is read from ``ALPHA_VANTAGE_API_KEY`` and from nowhere else. No
  default, no fallback, no config file.
* It is never logged, never included in an exception message, never written to
  the cache, and never placed in a URL that is returned, printed or stored.
  ``_redact`` scrubs it from everything this module emits, so a stack trace
  carrying a request URL cannot leak it.
* Raw vendor payloads are never committed. The cache lives under ``.cache/``,
  which ``.gitignore`` excludes, and holds **normalized** OHLCV only.

LICENCE POSITION
----------------
``product/data-provider-findings.md`` §E records, VERIFIED against the Terms of
Service PDF, that Alpha Vantage grants use *"for personal, non-commercial use,
unless you and Alpha Vantage have agreed otherwise in writing"*, and that
"Professional" use covers *"any type of commercial activity that allows
individuals or entities other than User to access information directly or
indirectly"*. This module therefore exists to produce **internal,
non-redistributed exploratory evidence**. Redistributing the data, or shipping it
in a product surface, is outside what HD-26 authorizes.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ENDPOINT = "https://www.alphavantage.co/query"
FUNCTION = "TIME_SERIES_DAILY_ADJUSTED"

#: Env var holding the key. There is deliberately no other source.
API_KEY_ENV = "ALPHA_VANTAGE_API_KEY"

#: Courtesy spacing between requests. The premium key showed no throttling on
#: four rapid full-history calls (2026-07-29), but the provider asks for
#: restraint and a pilot is not worth a ban.
MIN_REQUEST_INTERVAL_SECONDS = 0.35

#: The basis HD-01 rules and the engine enforces.
ADJUSTMENT_BASIS = "SPLIT_ADJUSTED_DIVIDEND_UNADJUSTED"

_PRICE_FIELDS = ("1. open", "2. high", "3. low", "4. close")
_REQUIRED_FIELDS = _PRICE_FIELDS + ("6. volume", "8. split coefficient")


class ProviderError(RuntimeError):
    """Base for every provider-side failure. Message is always redacted."""


class MissingApiKey(ProviderError):
    """``ALPHA_VANTAGE_API_KEY`` is unset or empty."""


class RateLimited(ProviderError):
    """Refused for rate-limit reasons — back off and retry, do not blacklist."""


class PremiumRequired(ProviderError):
    """A requested parameter is gated behind a paid plan.

    Distinct from :class:`RateLimited` because retrying never helps, and buying
    the plan is a **spend decision reserved to the Product Owner (HD-06)**.
    """


class InvalidSymbol(ProviderError):
    """The provider did not recognise the ticker."""


class MalformedResponse(ProviderError):
    """The payload parsed but does not carry a usable series."""


@dataclass(frozen=True)
class Bar:
    """One normalized daily bar, **split-adjusted and dividend-unadjusted**.

    ``date`` is ISO ``YYYY-MM-DD``. ``split_factor`` is the cumulative divisor
    applied to the raw vendor price, retained so the adjustment is auditable
    rather than a silent transformation.
    """

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    split_factor: float


@dataclass(frozen=True)
class Series:
    """Normalized OHLCV for one ticker, ascending by date."""

    symbol: str
    bars: tuple[Bar, ...]
    last_refreshed: str
    output_size: str
    adjustment_basis: str = ADJUSTMENT_BASIS
    #: ``(date, coefficient)`` for every split applied, oldest first.
    splits_applied: tuple[tuple[str, float], ...] = ()

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.bars)


def api_key() -> str:
    """Return the key from the environment, or raise. Never logged."""
    key = os.environ.get(API_KEY_ENV, "").strip()
    if not key:
        raise MissingApiKey(
            f"{API_KEY_ENV} is not set. Export it in the environment; it must "
            f"not be hardcoded, committed, or written to a source file."
        )
    return key


def _redact(text: str, key: str) -> str:
    """Remove the key from ``text``. Applied to everything this module emits."""
    if key and key in text:
        text = text.replace(key, "***REDACTED***")
    return text


def _request_url(symbol: str, key: str, output_size: str) -> str:
    """Build the request URL. **Never log or return this** — it carries the key."""
    query = urllib.parse.urlencode(
        {
            "function": FUNCTION,
            "symbol": symbol,
            "outputsize": output_size,
            "apikey": key,
        }
    )
    return f"{ENDPOINT}?{query}"


def classify(payload: dict[str, Any], symbol: str) -> None:
    """Raise the specific error a payload represents, or return if usable.

    Alpha Vantage answers **HTTP 200 for every one of these**, so status codes
    carry no signal and the body must be classified. The provider has changed
    which envelope key it uses over time (``Note`` -> ``Information``), so both
    are inspected.
    """
    if not isinstance(payload, dict):
        raise MalformedResponse(f"{symbol}: response was not a JSON object")

    advisory = ""
    for envelope in ("Note", "Information", "Error Message"):
        value = payload.get(envelope)
        if isinstance(value, str) and value.strip():
            advisory = value.strip()
            break

    if advisory:
        lowered = advisory.lower()
        # Order matters: a premium-gated parameter also mentions "premium
        # plans", so it must be tested before the rate-limit branch.
        if "premium" in lowered and ("parameter" in lowered or "endpoint" in lowered):
            raise PremiumRequired(f"{symbol}: {advisory}")
        if any(
            marker in lowered
            for marker in ("rate limit", "requests per day", "per minute", "sparingly")
        ):
            raise RateLimited(f"{symbol}: {advisory}")
        if "invalid api call" in lowered or "Error Message" in payload:
            raise InvalidSymbol(f"{symbol}: {advisory}")
        raise ProviderError(f"{symbol}: {advisory}")

    if "Time Series (Daily)" not in payload:
        raise MalformedResponse(
            f"{symbol}: no 'Time Series (Daily)' key; got {sorted(payload)}"
        )


def normalize(payload: dict[str, Any], symbol: str) -> Series:
    """Validate, split-adjust, and convert a classified payload into a Series.

    **The split adjustment is the load-bearing step.** For a bar on date ``d``,
    every split with an effective date **after** ``d`` must divide that bar's
    prices, because the vendor's OHLC is as-traded. Walking newest to oldest and
    accumulating the coefficient does that in one pass:

    * process bar ``d``: ``price_adj = price_raw / factor``
    * *then*, if ``d`` itself carries coefficient ``c != 1``, ``factor *= c`` so
      every **earlier** bar is divided by it too.

    Volume is multiplied by the same factor — a 10:1 split multiplies share
    count by ten, so as-traded volume must scale the other way to stay
    comparable.

    Every bar is validated: all fields present and parseable, prices strictly
    positive, ``low <= high``. A bar that fails rejects the **whole series**
    rather than being dropped — silently skipping a bar puts a hole in a causal
    series and the engine would never know.
    """
    meta = payload.get("Meta Data", {})
    if not isinstance(meta, dict):
        raise MalformedResponse(f"{symbol}: 'Meta Data' was not an object")

    returned = str(meta.get("2. Symbol", "")).strip().upper()
    if returned and returned != symbol.upper():
        raise MalformedResponse(f"{symbol}: provider returned data for {returned!r}")

    raw = payload["Time Series (Daily)"]
    if not isinstance(raw, dict) or not raw:
        raise MalformedResponse(f"{symbol}: empty or non-object series")

    dates = sorted(raw)
    # --- validate first, so a defect cannot be half-applied -------------------
    for date in dates:
        row = raw[date]
        if not isinstance(row, dict):
            raise MalformedResponse(f"{symbol}: bar {date} was not an object")
        missing = [f for f in _REQUIRED_FIELDS if f not in row]
        if missing:
            raise MalformedResponse(f"{symbol}: bar {date} missing {missing}")

    # --- split-adjust, newest to oldest ---------------------------------------
    factor = 1.0
    adjusted: dict[str, Bar] = {}
    splits: list[tuple[str, float]] = []
    for date in reversed(dates):
        row = raw[date]
        try:
            o, h, lo, c = (float(row[f]) for f in _PRICE_FIELDS)
            v = float(row["6. volume"])
            coeff = float(row["8. split coefficient"])
        except (TypeError, ValueError) as exc:
            raise MalformedResponse(f"{symbol}: bar {date} unparseable: {exc}") from None

        if min(o, h, lo, c) <= 0:
            raise MalformedResponse(f"{symbol}: bar {date} has a non-positive raw price")
        if lo > h:
            raise MalformedResponse(f"{symbol}: bar {date} has low {lo} > high {h}")
        if v < 0:
            raise MalformedResponse(f"{symbol}: bar {date} has negative volume")
        if coeff <= 0:
            raise MalformedResponse(f"{symbol}: bar {date} has split coefficient {coeff}")

        adjusted[date] = Bar(
            date=date,
            open=o / factor,
            high=h / factor,
            low=lo / factor,
            close=c / factor,
            volume=int(round(v * factor)),
            split_factor=factor,
        )
        if coeff != 1.0:
            splits.append((date, coeff))
            factor *= coeff

    bars = tuple(adjusted[d] for d in dates)
    for b in bars:
        if min(b.open, b.high, b.low, b.close) <= 0:
            raise MalformedResponse(f"{symbol}: bar {b.date} non-positive after adjustment")

    return Series(
        symbol=symbol.upper(),
        bars=bars,
        last_refreshed=str(meta.get("3. Last Refreshed", "")),
        output_size=str(meta.get("4. Output Size", "")),
        splits_applied=tuple(reversed(splits)),
    )


def _cache_path(cache_dir: Path, symbol: str) -> Path:
    return cache_dir / f"{symbol.upper()}.json"


def load_cached(cache_dir: Path, symbol: str) -> Series | None:
    """Return a cached Series, or ``None`` if absent, corrupt, or on a stale basis.

    An entry whose ``adjustment_basis`` is not the ruled one is discarded rather
    than used — a cache written before the HD-01 fix must not silently poison a
    later run.
    """
    path = _cache_path(cache_dir, symbol)
    if not path.exists():
        return None
    try:
        blob = json.loads(path.read_text())
        if blob.get("adjustment_basis") != ADJUSTMENT_BASIS:
            return None
        bars = tuple(
            Bar(
                date=b["date"], open=b["open"], high=b["high"], low=b["low"],
                close=b["close"], volume=b["volume"], split_factor=b.get("split_factor", 1.0),
            )
            for b in blob["bars"]
        )
        if not bars:
            return None
        return Series(
            symbol=blob["symbol"],
            bars=bars,
            last_refreshed=blob.get("last_refreshed", ""),
            output_size=blob.get("output_size", ""),
            adjustment_basis=blob["adjustment_basis"],
            splits_applied=tuple(tuple(s) for s in blob.get("splits_applied", ())),
        )
    except (OSError, ValueError, KeyError, TypeError):
        return None


def store_cached(cache_dir: Path, series: Series) -> Path:
    """Write the **normalized** series. No key, no URL, no request metadata."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = _cache_path(cache_dir, series.symbol)
    path.write_text(
        json.dumps(
            {
                "symbol": series.symbol,
                "adjustment_basis": series.adjustment_basis,
                "last_refreshed": series.last_refreshed,
                "output_size": series.output_size,
                "splits_applied": [list(s) for s in series.splits_applied],
                "bars": [
                    {
                        "date": b.date, "open": b.open, "high": b.high, "low": b.low,
                        "close": b.close, "volume": b.volume, "split_factor": b.split_factor,
                    }
                    for b in series.bars
                ],
            }
        )
    )
    return path


class Fetcher:
    """Throttled, cache-first fetcher. A cache hit makes no network call."""

    def __init__(
        self,
        cache_dir: Path,
        *,
        min_interval: float = MIN_REQUEST_INTERVAL_SECONDS,
        opener=urllib.request.urlopen,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.min_interval = min_interval
        self._opener = opener
        self._last_request_at: float | None = None
        self.requests_made = 0

    def _throttle(self) -> None:
        if self._last_request_at is None:
            return
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

    def fetch_uncached(self, symbol: str, *, output_size: str = "full") -> Series:
        """Always hit the network. Raises a specific :class:`ProviderError`."""
        key = api_key()
        url = _request_url(symbol, key, output_size)
        self._throttle()
        try:
            with self._opener(url, timeout=120) as response:
                body = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            raise ProviderError(_redact(f"{symbol}: transport failure: {exc}", key)) from None
        finally:
            self._last_request_at = time.monotonic()
            self.requests_made += 1

        try:
            payload = json.loads(body)
        except ValueError:
            raise MalformedResponse(
                _redact(f"{symbol}: response was not JSON: {body[:200]!r}", key)
            ) from None

        try:
            classify(payload, symbol)
            return normalize(payload, symbol)
        except ProviderError as exc:
            raise type(exc)(_redact(str(exc), key)) from None

    def fetch(self, symbol: str, *, output_size: str = "full") -> tuple[Series, bool]:
        """Return ``(series, from_cache)``, preferring a valid cache entry."""
        cached = load_cached(self.cache_dir, symbol)
        if cached is not None:
            return cached, True
        series = self.fetch_uncached(symbol, output_size=output_size)
        store_cached(self.cache_dir, series)
        return series, False
