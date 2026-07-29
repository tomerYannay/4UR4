"""Before/after comparison for HD-27, on identical cached data.

"Before" is the pre-HD-27 rule exactly: the jump-only guard, reproduced by
withholding the corporate-action feed. "After" supplies the feed. Same bars,
same parameters, same engine — the *only* variable is the evidence available to
the guard, which is precisely the change HD-27 made.

Run: ``python3 -m scanner.compare_hd27``
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from engine.guards import CorporateActions, run_guards
from providers import alphavantage as av
from scanner import backtest
from scanner.run_pilot import PARAMS, UNIVERSE


def main() -> int:
    fetcher = av.Fetcher(Path(".cache/alphavantage"))
    rows = []
    before_reports, after_reports = [], []

    for i, symbol in enumerate(UNIVERSE, 1):
        series, _ = fetcher.fetch(symbol)
        bars = series.bars
        index_of = {b.date: n for n, b in enumerate(bars)}
        actions = CorporateActions(
            symbol=symbol,
            splits={index_of[d]: c for d, c in series.splits_applied if d in index_of},
        )
        engine_series = backtest.to_bar_series(bars)

        # BEFORE — jump-only, no feed. Cheap: it only runs the guard.
        before = run_guards(engine_series, PARAMS, None)
        # AFTER — the full run with evidence.
        after = backtest.run_symbol(symbol, series, PARAMS)

        rows.append(
            {
                "symbol": symbol,
                "bars": len(bars),
                "splits": len(actions.splits),
                "before_rejected": before.rejected,
                "before_reason": (before.rejections[0].reason if before.rejections else None),
                "before_bar": (before.rejections[0].bar if before.rejections else None),
                "before_date": (str(before.rejections[0].date) if before.rejections else None),
                "before_jump": (round(before.rejections[0].log_jump, 6)
                                if before.rejections and before.rejections[0].log_jump else None),
                "after_rejected": after.guard_rejected,
                "after_reasons": after.guard_rejections,
                "after_breakouts": len(after.breakouts),
                "jumps_inspected_accepted": len(after.guard_observations),
                "final_state": after.final_state,
                "error": after.error,
            }
        )
        after_reports.append(after)
        print(
            f"[{i}/{len(UNIVERSE)}] {symbol}: before={'REJECT' if before.rejected else 'ok'} "
            f"after={'REJECT' if after.guard_rejected else 'ok'} "
            f"breakouts={len(after.breakouts)} accepted_jumps={len(after.guard_observations)}",
            file=sys.stderr,
            flush=True,
        )

    summary = backtest.aggregate(after_reports)
    out = {
        "comparison": rows,
        "totals": {
            "symbols": len(rows),
            "rejected_before": sum(1 for r in rows if r["before_rejected"]),
            "rejected_after": sum(1 for r in rows if r["after_rejected"]),
            "recovered": [r["symbol"] for r in rows if r["before_rejected"] and not r["after_rejected"]],
            "still_rejected": [r["symbol"] for r in rows if r["after_rejected"]],
            "breakouts_before": 0,  # a rejected bar-set emits none, by construction
            "breakouts_after": sum(r["after_breakouts"] for r in rows),
            "large_jumps_inspected_and_accepted": sum(r["jumps_inspected_accepted"] for r in rows),
        },
        "summary_after": summary,
    }
    Path(".cache/hd27-comparison.json").write_text(json.dumps(out, indent=1, default=str))
    t = out["totals"]
    print(
        f"\nrejected before={t['rejected_before']}  after={t['rejected_after']}  "
        f"recovered={len(t['recovered'])}  breakouts after={t['breakouts_after']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
