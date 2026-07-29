"""Before/after comparison for HD-27, on identical cached data.

"Before" is the pre-HD-27 rule exactly: the jump-only guard, reproduced by
withholding the corporate-action feed. "After" supplies the feed. Same bars,
same parameters, same engine — the **only** variable is the evidence available
to the guard, which is precisely what HD-27 changed.

A **per-symbol compute budget** applies. The engine's §21.4 Lemma gives an O(1)
rolling update in the common case, but every hull re-bind falls back to §8's
brute-force domination scan, so cost varies by orders of magnitude across names.
A symbol that exceeds the budget is recorded as ``COMPUTE_TIMEOUT`` — a
**missing-data** outcome, never a zero — because silently reporting it as "no
breakouts" is the same class of defect HD-27 exists to end.

Run: ``python3 -m tools.research.scanner.compare_hd27 [--budget SECONDS]``
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import signal
import statistics
import sys
import time
from pathlib import Path

from engine.guards import CorporateActions, run_guards
from tools.research.providers import alphavantage as av
from tools.research.scanner import backtest
from tools.research.scanner.instrument import Instrumented, peak_rss_mb
from tools.research.scanner.run_pilot import PARAMS, UNIVERSE

#: Terminal statuses. Every symbol lands in exactly one; none is a silent zero.
STATUSES = ("COMPLETE", "INPUT_REJECTED", "PROVIDER_ERROR", "INSUFFICIENT_DATA", "COMPUTE_TIMEOUT")

#: A series shorter than this cannot form a line (min_formation_bars) and then
#: carry a 20-bar forward window, so it is INSUFFICIENT_DATA rather than a zero.
MIN_USABLE_BARS = 40


class _Budget(BaseException):
    """Deliberately a ``BaseException``.

    ``backtest.run_symbol`` wraps the engine in ``except Exception`` so a
    provider defect cannot kill the run. A budget signal that subclassed
    ``Exception`` would be caught there and reported as an engine *error* —
    i.e. the timeout would be laundered into a completed symbol with zero
    breakouts, which is exactly the silent-zero failure HD-27 exists to end.
    """


def _alarm(_signum, _frame):
    raise _Budget()


def _overlap_filter(outcomes):
    """Keep only breakouts whose 20-bar window does not overlap a kept one.

    Overlapping windows share bars, so their forward returns are **not
    independent observations**: one sustained move can be counted several times
    and will inflate any hit rate computed over them. Greedy earliest-first per
    symbol — the standard non-overlap rule, and it does not look at outcomes when
    choosing, so the selection cannot be biased by the returns it will report.
    """
    kept, last_end = [], {}
    for o in sorted(outcomes, key=lambda x: (x.symbol, x.breakout_bar)):
        end = last_end.get(o.symbol)
        if end is None or o.breakout_bar > end:
            kept.append(o)
            last_end[o.symbol] = o.breakout_bar + backtest.MAX_HORIZON
    return kept


def _stats(vals):
    present = [v for v in vals if v is not None]
    if not present:
        return {"n": 0, "mean": None, "median": None, "stdev": None,
                "min": None, "max": None, "hit_rate": None}
    return {
        "n": len(present),
        "mean": statistics.fmean(present),
        "median": statistics.median(present),
        "stdev": statistics.stdev(present) if len(present) > 1 else None,
        "min": min(present),
        "max": max(present),
        "hit_rate": sum(1 for v in present if v > 0) / len(present),
    }


def _bucket(outcomes, label):
    out = {"label": label, "breakouts": len(outcomes), "horizons": {}, "excursions": {}}
    for h in backtest.HORIZONS:
        vals = [o.forward_returns[h] for o in outcomes]
        st = _stats(vals)
        st["excluded_incomplete"] = sum(1 for v in vals if v is None)
        out["horizons"][h] = st
    out["excursions"]["mfe"] = _stats([o.mfe for o in outcomes])
    out["excursions"]["mae"] = _stats([o.mae for o in outcomes])
    engine_outcomes: dict = {}
    for o in outcomes:
        engine_outcomes[o.engine_outcome] = engine_outcomes.get(o.engine_outcome, 0) + 1
    out["engine_outcomes"] = engine_outcomes
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=240, help="per-symbol compute budget, seconds")
    ap.add_argument("--limit", type=int, default=len(UNIVERSE))
    ap.add_argument(
        "--max-bars", type=int, default=0,
        help="run only the first N bars of each symbol (0 = full history). "
             "A PREFIX, never a suffix: the engine's anchor is the highest high "
             "seen so far, so a prefix run computes exactly what the full run "
             "would have computed for those bars, whereas a recent-N window "
             "would anchor on a windowed high and report a different product.",
    )
    ap.add_argument("--out", default=".cache/hd27-comparison.json")
    args = ap.parse_args(argv)

    signal.signal(signal.SIGALRM, _alarm)
    fetcher = av.Fetcher(Path(".cache/alphavantage"))
    rows, all_outcomes = [], []

    for i, symbol in enumerate(UNIVERSE[: args.limit], 1):
        try:
            series, _ = fetcher.fetch(symbol)
        except av.ProviderError as exc:
            rows.append({"symbol": symbol, "status": "PROVIDER_ERROR", "detail": str(exc)})
            print(f"[{i}] {symbol}: PROVIDER_ERROR", file=sys.stderr, flush=True)
            continue

        bars = series.bars
        window_note = None
        if args.max_bars and len(bars) > args.max_bars:
            window_note = f"causal prefix: first {args.max_bars} of {len(bars)} bars"
            bars = bars[: args.max_bars]
            kept = {b.date for b in bars}
            series = dataclasses.replace(
                series,
                bars=bars,
                splits_applied=tuple(x for x in series.splits_applied if x[0] in kept),
            )
        index_of = {b.date: n for n, b in enumerate(bars)}
        splits = {index_of[d]: c for d, c in series.splits_applied if d in index_of}
        engine_series = backtest.to_bar_series(bars)

        before = run_guards(engine_series, PARAMS, None)  # jump-only: cheap
        row = {
            "symbol": symbol,
            "bars": len(bars),
            "first_date": bars[0].date,
            "last_date": bars[-1].date,
            "splits": len(splits),
            "window": window_note,
            "before_rejected": before.rejected,
            "before_reason": before.rejections[0].reason if before.rejections else None,
            "before_date": str(before.rejections[0].date) if before.rejections else None,
            "before_jump": (round(before.rejections[0].log_jump, 6)
                            if before.rejections and before.rejections[0].log_jump is not None
                            else None),
        }

        if len(bars) < MIN_USABLE_BARS:
            row.update(status="INSUFFICIENT_DATA",
                       detail=f"{len(bars)} bars < {MIN_USABLE_BARS} minimum usable")
            rows.append(row)
            print(f"[{i}] {symbol}: INSUFFICIENT_DATA", file=sys.stderr, flush=True)
            continue

        started = time.monotonic()
        inst_counters = []
        signal.alarm(args.budget)
        try:
            with Instrumented() as inst:
                inst_counters.append(inst.counters)
                after = backtest.run_symbol(symbol, series, PARAMS)
            signal.alarm(0)
            inst.assert_wired()
            elapsed = time.monotonic() - started
            row.update(
                status=("INPUT_REJECTED" if after.guard_rejected else "COMPLETE"),
                elapsed_seconds=round(elapsed, 2),
                profile=inst.counters.snapshot(),
                peak_rss_mb=peak_rss_mb(),
                after_rejected=after.guard_rejected,
                after_reasons=after.guard_rejections,
                after_breakouts=len(after.breakouts),
                jumps_inspected_accepted=len(after.guard_observations),
                accepted_jump_detail=after.guard_observations,
                final_state=after.final_state,
                error=after.error,
            )
            all_outcomes.extend(after.breakouts)
            print(
                f"[{i}] {symbol}: before={'REJECT' if before.rejected else 'ok'} "
                f"after={'REJECT' if after.guard_rejected else 'ok'} "
                f"breakouts={len(after.breakouts)} accepted_jumps={len(after.guard_observations)}",
                file=sys.stderr, flush=True,
            )
        except _Budget:
            signal.alarm(0)
            elapsed = time.monotonic() - started
            snap = inst_counters[0].snapshot() if inst_counters else {}
            row.update(
                status="COMPUTE_TIMEOUT",
                after_breakouts=None,          # MISSING DATA, never zero
                elapsed_seconds=round(elapsed, 2),
                budget_seconds=args.budget,
                bars=len(bars),
                last_stage="causal fold (§21.2) — guards passed, geometry incomplete",
                profile=snap,
                hull_rebinding_observed=(snap.get("hull_rebinds", 0) > 0),
                peak_rss_mb=peak_rss_mb(),
                detail=f"exceeded {args.budget}s compute budget; MISSING DATA, not zero",
            )
            print(f"[{i}] {symbol}: COMPUTE_TIMEOUT (>{args.budget}s) — missing data",
                  file=sys.stderr, flush=True)
        rows.append(row)

    independent = _overlap_filter(all_outcomes)
    ok = [r for r in rows if r.get("status") in ("COMPLETE", "INPUT_REJECTED")]
    complete = [r for r in rows if r.get("status") == "COMPLETE"]
    by_status = {s: [r["symbol"] for r in rows if r.get("status") == s] for s in STATUSES}
    attempted = args.limit

    contributing = [r["symbol"] for r in complete if (r.get("after_breakouts") or 0) > 0]
    # A breakout within MAX_HORIZON bars of the series end has no complete forward
    # window; it is excluded from the horizon statistics rather than counted as 0%.
    incomplete = sum(1 for o in all_outcomes
                     if o.forward_returns.get(backtest.MAX_HORIZON) is None)

    out = {
        "run": {
            "budget_seconds": args.budget,
            "max_bars": args.max_bars or None,
            "scope": "survivor-biased exploratory real-market validation; "
                     "NOT Phase 4 entry, implementation or exit evidence",
        },
        # ---- Summary 1: completed symbols only -------------------------------
        "summary_completed_only": {
            "symbols": len(complete),
            "symbols_contributing_at_least_one_breakout": len(contributing),
            "contributing": contributing,
            "breakouts_before_hd27": 0,
            "breakouts_after_hd27": sum(r.get("after_breakouts") or 0 for r in complete),
            "including_overlapping": _bucket(all_outcomes, "all breakouts (windows may overlap)"),
            "excluding_overlapping": _bucket(
                independent, "non-overlapping only (greedy earliest-first, 20-bar windows)"
            ),
        },
        # ---- Summary 2: full attempted universe ------------------------------
        "summary_full_universe": {
            "attempted": attempted,
            "by_status": {s: len(by_status[s]) for s in STATUSES},
            "symbols_by_status": by_status,
            "completion_rate": round(len(complete) / attempted, 4) if attempted else None,
            "rejection_rate": round(len(by_status["INPUT_REJECTED"]) / attempted, 4) if attempted else None,
            "timeout_rate": round(len(by_status["COMPUTE_TIMEOUT"]) / attempted, 4) if attempted else None,
            "note": "COMPUTE_TIMEOUT symbols are MISSING DATA. They are excluded "
                    "from every return-rate denominator and are never reported as "
                    "zero breakouts.",
        },
        # ---- Seven disclosure items -----------------------------------------
        "disclosure": {
            "total_attempted_symbols": attempted,
            "completed_symbols": len(complete),
            "symbols_contributing_at_least_one_breakout": len(contributing),
            "raw_event_count": len(all_outcomes),
            "non_overlapping_event_count": len(independent),
            "events_excluded_incomplete_forward_window": incomplete,
            "return_statistics_denominator": "completed symbols only",
        },
        "hd27": {
            "rejected_before": sum(1 for r in ok if r["before_rejected"]),
            "rejected_after": sum(1 for r in ok if r.get("after_rejected")),
            "recovered_by_hd27": [r["symbol"] for r in ok
                                  if r["before_rejected"] and not r.get("after_rejected")],
            "still_rejected": [{"symbol": r["symbol"], "reasons": r.get("after_reasons")}
                               for r in ok if r.get("after_rejected")],
            "large_jumps_inspected_and_accepted": sum(
                r.get("jumps_inspected_accepted") or 0 for r in ok
            ),
        },
        "timeouts": [
            {k: r.get(k) for k in ("symbol", "bars", "elapsed_seconds", "budget_seconds",
                                   "last_stage", "profile", "hull_rebinding_observed",
                                   "peak_rss_mb")}
            for r in rows if r.get("status") == "COMPUTE_TIMEOUT"
        ],
        "per_symbol": rows,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=1, default=str))
    d = out["disclosure"]
    fu = out["summary_full_universe"]["by_status"]
    print(
        f"\nattempted={d['total_attempted_symbols']} " + " ".join(
            f"{k}={v}" for k, v in fu.items()
        ) + f"\ncontributing={d['symbols_contributing_at_least_one_breakout']} "
        f"raw_events={d['raw_event_count']} independent={d['non_overlapping_event_count']} "
        f"excluded_incomplete_window={d['events_excluded_incomplete_forward_window']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
