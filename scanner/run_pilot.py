"""Run the exploratory, survivor-biased pilot and write a JSON result blob.

    python3 -m scanner.run_pilot [--limit N] [--cache DIR] [--out FILE]

Requires ``ALPHA_VANTAGE_API_KEY`` in the environment. Nothing here prints,
stores or commits the key.

EXPLORATORY ONLY (HD-26). Not a Phase 4 increment: Phase 4's exit criterion is a
backtest over the historical 4UR4 US Large-Cap 500 at each date's point-in-time
membership. This is a fixed list of names that exist **today**.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from engine.params import DetectorParams
from providers import alphavantage as av
from scanner import backtest

#: 40 large, liquid US names across sectors. Chosen before any result was seen,
#: and fixed here so the universe cannot be tuned after the fact — but note it
#: is still a *survivor* list: every one of these exists today.
UNIVERSE = (
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO",
    "JPM", "V", "UNH", "XOM", "WMT", "MA", "JNJ", "PG",
    "HD", "CVX", "ABBV", "MRK", "COST", "PEP", "KO", "ADBE",
    "CSCO", "CRM", "ACN", "AMD", "NFLX", "INTC", "TMO", "MCD",
    "ABT", "WFC", "BAC", "DIS", "QCOM", "TXN", "PFE", "ORCL",
)

#: The ratified illustrative set. `eps_break` has no default by design (HD-03 /
#: §13.5), so it is named here explicitly rather than inherited.
PARAMS = DetectorParams(
    eps=0.02,
    eps_break=0.01,
    min_formation_bars=8,
    min_ath_age_bars=3,
    tolerance_version="tol-2026.07-illustrative",
    spec_version="UNVERSIONED-PENDING-OQ-J",
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=len(UNIVERSE))
    ap.add_argument("--cache", default=".cache/alphavantage")
    ap.add_argument("--out", default=".cache/pilot-results.json")
    args = ap.parse_args(argv)

    symbols = UNIVERSE[: args.limit]
    fetcher = av.Fetcher(Path(args.cache))
    reports: list[backtest.SymbolReport] = []
    fetch_errors: dict[str, str] = {}

    for i, symbol in enumerate(symbols, 1):
        try:
            series, from_cache = fetcher.fetch(symbol)
        except av.ProviderError as exc:
            # Message is already redacted by the provider.
            fetch_errors[symbol] = f"{type(exc).__name__}: {exc}"
            print(f"[{i}/{len(symbols)}] {symbol}: FETCH FAILED — {type(exc).__name__}", file=sys.stderr)
            continue

        report = backtest.run_symbol(symbol, series, PARAMS)
        reports.append(report)
        src = "cache" if from_cache else "network"
        print(
            f"[{i}/{len(symbols)}] {symbol}: {report.bars} bars "
            f"({report.first_date}..{report.last_date}) {src} — "
            f"{len(report.breakouts)} breakout(s), final {report.final_state}"
            + (f" ERROR {report.error}" if report.error else ""),
            file=sys.stderr,
        )

    summary = backtest.aggregate(reports)
    summary["fetch_errors"] = fetch_errors
    summary["requests_made"] = fetcher.requests_made
    summary["universe"] = list(symbols)
    summary["params"] = {
        "eps": PARAMS.eps, "eps_break": PARAMS.eps_break,
        "min_formation_bars": PARAMS.min_formation_bars,
        "min_ath_age_bars": PARAMS.min_ath_age_bars,
        "eps_fail": PARAMS.eps_fail, "F_fail": PARAMS.F_fail,
        "eps_retest": PARAMS.eps_retest, "W_retest": PARAMS.W_retest,
        "h_hold": PARAMS.h_hold, "E_expiry": PARAMS.E_expiry,
    }
    summary["adjustment_basis"] = av.ADJUSTMENT_BASIS
    summary["limits"] = [
        "SURVIVORSHIP BIAS: universe is names that exist today; delisted and "
        "acquired names are absent, which biases aggregates upward by an "
        "unknown amount (HD-07 unresolved).",
        "NO MULTIPLE-COMPARISON CONTROL: one parameter set, one window, every "
        "metric reported.",
        "FORWARD RETURNS ARE MEASURED, NOT TRADED: entry is the breakout bar's "
        "close, which is not obtainable; no costs, slippage, borrow or fills.",
        "NOT A PHASE 4 INCREMENT (HD-26).",
    ]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "summary": summary,
                "symbols": [
                    {
                        **{k: v for k, v in asdict(r).items() if k != "breakouts"},
                        "breakouts": [asdict(b) for b in r.breakouts],
                    }
                    for r in reports
                ],
            },
            indent=1,
            default=str,
        )
    )
    print(f"\nwrote {out}  ({summary['total_breakouts']} breakouts across "
          f"{summary['symbols_with_data']} symbols)", file=sys.stderr)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
