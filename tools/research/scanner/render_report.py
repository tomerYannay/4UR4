"""Render the pilot's two result summaries and disclosure block as Markdown.

Reads the JSON written by ``compare_hd27`` and formats it. Deliberately does no
arithmetic of its own beyond percentages: every number it prints is one the
measurement run computed, so the report cannot disagree with the evidence file.

Run: ``python3 -m tools.research.scanner.render_report B.json A.json``
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def pct(x):
    return "—" if x is None else f"{x * 100:.2f}%"


def num(x, places=4):
    return "—" if x is None else f"{x:.{places}f}"


def horizon_table(bucket) -> str:
    lines = [
        "| horizon | n | hit rate | mean | median | stdev | min | max | excluded (incomplete window) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for h, st in sorted(bucket["horizons"].items(), key=lambda kv: int(kv[0])):
        lines.append(
            f"| {h}d | {st['n']} | {pct(st['hit_rate'])} | {pct(st['mean'])} | "
            f"{pct(st['median'])} | {pct(st['stdev'])} | {pct(st['min'])} | "
            f"{pct(st['max'])} | {st['excluded_incomplete']} |"
        )
    ex = bucket["excursions"]
    lines += [
        "",
        "| excursion | n | mean | median | min | max |",
        "|---|---|---|---|---|---|",
        f"| MFE | {ex['mfe']['n']} | {pct(ex['mfe']['mean'])} | {pct(ex['mfe']['median'])} | "
        f"{pct(ex['mfe']['min'])} | {pct(ex['mfe']['max'])} |",
        f"| MAE | {ex['mae']['n']} | {pct(ex['mae']['mean'])} | {pct(ex['mae']['median'])} | "
        f"{pct(ex['mae']['min'])} | {pct(ex['mae']['max'])} |",
    ]
    return "\n".join(lines)


def status_table(d) -> str:
    fu = d["summary_full_universe"]
    lines = ["| terminal status | symbols | rate | meaning |", "|---|---|---|---|"]
    meaning = {
        "COMPLETE": "engine ran the full causal fold; contributes to return statistics",
        "INPUT_REJECTED": "§18 guard rejected the bar-set, with a structured reason",
        "PROVIDER_ERROR": "vendor fetch failed",
        "INSUFFICIENT_DATA": "too few bars to form a line and carry a forward window",
        "COMPUTE_TIMEOUT": "**MISSING DATA** — excluded from every denominator, never a zero",
    }
    total = fu["attempted"]
    for s, n in fu["by_status"].items():
        lines.append(f"| `{s}` | {n} | {n / total * 100:.1f}% | {meaning[s]} |")
    return "\n".join(lines)


def main(argv):
    b = json.loads(Path(argv[0]).read_text())
    a = json.loads(Path(argv[1]).read_text()) if len(argv) > 1 else None

    d = b["disclosure"]
    sc = b["summary_completed_only"]
    out = []
    out.append("## Summary 1 — completed symbols only\n")
    out.append(f"Breakouts before HD-27: **{sc['breakouts_before_hd27']}** · "
               f"after HD-27: **{sc['breakouts_after_hd27']}**\n")
    out.append("### Including overlapping events\n")
    out.append(horizon_table(sc["including_overlapping"]))
    out.append("\n### Excluding overlapping events (greedy earliest-first, 20-bar windows)\n")
    out.append(horizon_table(sc["excluding_overlapping"]))
    out.append("\n### Engine outcome mix (non-overlapping)\n")
    for k, v in sorted(sc["excluding_overlapping"]["engine_outcomes"].items()):
        out.append(f"- `{k}`: {v}")

    out.append("\n## Summary 2 — full attempted universe\n")
    out.append(status_table(b))

    out.append("\n## Disclosure\n")
    # The scope rider travels with the NUMBERS, not just with the evidence file.
    # HD-26 requires the limits to accompany every figure the pilot produces; an
    # earlier version wrote the rider into the JSON and printed only the seven
    # quantitative items, so the report a person actually reads carried none of
    # it. A caveat that stays in a file nobody opens is not a caveat.
    out.append(f"> **Scope:** {b['run']['scope']}\n")
    out.append(f"> Per-symbol compute budget: {b['run']['budget_seconds']}s"
               + (f" · causal prefix: first {b['run']['max_bars']} bars"
                  if b["run"].get("max_bars") else " · full delivered history")
               + "\n")
    for k, v in d.items():
        out.append(f"- **{k.replace('_', ' ')}**: {v}")

    h = b["hd27"]
    out.append("\n## HD-27 effect\n")
    out.append(f"- symbols rejected BEFORE (jump-only rule): **{h['rejected_before']}**")
    out.append(f"- symbols rejected AFTER (with split evidence): **{h['rejected_after']}**")
    out.append(f"- recovered by HD-27: **{len(h['recovered_by_hd27'])}** — "
               f"{', '.join(h['recovered_by_hd27']) or 'none'}")
    out.append(f"- large jumps inspected and ACCEPTED as real movement: "
               f"**{h['large_jumps_inspected_and_accepted']}**")
    if h["still_rejected"]:
        out.append("- still rejected, with exact reasons:")
        for r in h["still_rejected"]:
            out.append(f"  - `{r['symbol']}` — {r['reasons']}")

    if a is not None:
        out.append("\n## Full-history pass (scalability measurement)\n")
        out.append(status_table(a))
        if a["timeouts"]:
            out.append("\n| symbol | bars | elapsed | budget | last stage | "
                       "select_second_anchor | y_hat | hull re-binds | peak RSS |")
            out.append("|---|---|---|---|---|---|---|---|---|")
            for t in a["timeouts"]:
                p = t.get("profile") or {}
                out.append(
                    f"| {t['symbol']} | {t['bars']} | {t['elapsed_seconds']}s | "
                    f"{t['budget_seconds']}s | {t['last_stage']} | "
                    f"{p.get('select_second_anchor_calls', '—')} | "
                    f"{p.get('y_hat_calls', '—')} | {p.get('hull_rebinds', '—')} | "
                    f"{t.get('peak_rss_mb', '—')} MB |"
                )
    print("\n".join(out))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
