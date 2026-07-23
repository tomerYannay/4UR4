# 4UR4 — Explainable Confidence Specification (v1 heuristic)

Status: design/context under GOV-015 build-freeze — not an implementation order.

> **Authority:** Technical design (Architect). Defines the deterministic,
> decomposable **Confidence v1** score for a confirmed breakout, its output
> schema, explainability requirements, later-ML feature candidates and success
> labels, calibration goals, and safeguards. It authorizes **no build**
> ([GOV-013](../governance/approval-gate.md), [GOV-015](../governance/build-freeze.md)).
> It depends on and references the geometry defined in
> [`trendline-specification.md`](trendline-specification.md).

---

## 0. Scope, principles, and the sentiment boundary

Confidence v1 answers: *"How structurally trustworthy is this breakout signal?"*
It is a **transparent heuristic**, **not a probability**. Every point is
traceable to a named, inspectable contribution (Explainability is first-class,
per vision).

**GOV-014 boundary (explicit):** **Confidence v1 does NOT depend on market
sentiment.** No Fear & Greed, no market-regime score, no sentiment input feeds
v1 in any way. Sentiment remains research-context only
([GOV-014](../governance/market-sentiment-context.md)); it may modulate a
**future** version **only after** human approval, a Ready ticket, and a
**backtest**. Presenting an un-backtested sentiment-modulated score is
prohibited.

**Correctness/robustness principle:** v1 is a **heuristic on structure**, computed
purely from the trendline geometry and price/volume around the breakout — all
already-deterministic per the trendline spec. Same inputs → same score
(reproducibility).

---

## 1. What v1 is and is NOT

| v1 IS | v1 is NOT |
|-------|-----------|
| A 0–100 **quality heuristic** for a confirmed breakout. | A probability / "% chance it works." |
| A **sum of named, bounded contributions**. | A black box or a fitted model. |
| Fully **deterministic** and reproducible. | Dependent on sentiment/regime (GOV-014). |
| **Explainable** — each point has a reason string. | A trading recommendation or advice. |

> **Decision D-CF-01 — Score meaning** · Default: 0–100 **heuristic quality
> score**, explicitly NOT a probability, never labeled "% chance." · Alternative:
> present as 0–1 or as star tiers. · Materiality: **high** (mis-presentation is a
> user-trust/compliance risk). · **Human-approval: yes** for any UI wording that
> could imply probability.

---

## 2. Score construction (deterministic, decomposable)

```
Confidence = clamp( Σ_i  w_i · s_i ,  0, 100 )
```

- `s_i` = a **sub-score in [0, 1]** for component `i`, computed by a stated
  formula.
- `w_i` = a **weight in points**, `Σ w_i = 100` (so a perfect signal scores 100).
- Each `(component, s_i, w_i, contribution = w_i·s_i, reason)` is emitted for
  explainability.

**Weights are tunable defaults.** Per the tasking, tuning weights **within the
confidence workstream** does **not** require human approval; only changing the
*meaning* of the score (D-CF-01) or adding sentiment (GOV-014) does.

### 2.1 Components, formulas, and default weights

| # | Component | What it measures | Sub-score `s_i` formula (all clamp to [0,1]) | Default `w_i` (pts) |
|---|-----------|------------------|----------------------------------------------|--------------------:|
| C1 | **Line fit quality** | How cleanly highs hug the log line (R² of pivot highs vs `ŷ`). | `s = max(0, R²_log)` over the touching pivot highs. | 20 |
| C2 | **Touch count & spacing** | More, well-spaced touches = more-tested resistance. | `s = min(1, (n_touch−2)/(N_target−2)) · spacingFactor`, `N_target=5`; `spacingFactor = min(1, meanGap/minGapTarget)`. | 18 |
| C3 | **Breakout strength** | How decisively the close cleared the line. | `s = clamp( (ln C_bo − ŷ_bo) / margin_ref , 0, 1)`, `margin_ref = 0.05` (≈5%). | 18 |
| C4 | **Volume confirmation** | Volume expansion on breakout. | `s = clamp( (V_bo/SMA20_vol − 1) / (f_target − 1), 0, 1)`, `f_target = 2.0`. | 14 |
| C5 | **Retest success** | Did price retest and hold the line as support? | `s = 1` if `RETESTED`; `0.5` if clean no-retest hold; `0` if not yet / failed. | 15 |
| C6 | **Line maturity / age** | Longer-established resistance = more meaningful break. | `s = clamp( (tB − tA)/span_ref, 0, 1)`, `span_ref = 250` bars (~1yr daily). | 10 |
| C7 | **Cleanliness penalty** | Penalize many prior wick-breaks / near-pierces (false pressure). | `s = clamp(1 − n_wickbreak/wick_ref, 0, 1)`, `wick_ref = 5`. | 5 |
|   | **Total** | | | **100** |

> **Decision D-CF-02 — Component set & default weights** · Default: C1–C7 as
> above, weights summing to 100. · Alternative: fold C7 into C2, or add an
> "ATR-normalized breakout strength." · Materiality: med (tunable; does not change
> score *meaning*). · Human-approval: no (tunable within the confidence
> workstream).

### 2.2 Worked example

A breakout with: `R²_log = 0.94`; `n_touch = 4`, good spacing (`spacingFactor =
1.0`); breakout close margin `ln C_bo − ŷ_bo = 0.03`; `V_bo/SMA20 = 1.6`;
`RETESTED`; `tB−tA = 180`; `n_wickbreak = 1`.

| C | `s_i` | `w_i` | contribution |
|---|------:|------:|-------------:|
| C1 | 0.94 | 20 | 18.80 |
| C2 | `min(1,(4−2)/3)·1.0 = 0.667` | 18 | 12.01 |
| C3 | `0.03/0.05 = 0.60` | 18 | 10.80 |
| C4 | `(1.6−1)/(2.0−1) = 0.60` | 14 | 8.40 |
| C5 | 1.0 (RETESTED) | 15 | 15.00 |
| C6 | `180/250 = 0.72` | 10 | 7.20 |
| C7 | `1 − 1/5 = 0.80` | 5 | 4.00 |
| **Confidence** | | | **76.21 → 76** |

Reasons emitted, e.g. C5: *"Retest held on bar 90: low touched line (−0.4%) and
close reclaimed it — support confirmed."*

---

## 3. Explainability requirements (binding)

1. **Full decomposition:** output MUST list every component with its `s_i`,
   `w_i`, `contribution`, and a **human-readable `reason` string**.
2. **No hidden terms:** `Σ contributions` (clamped) MUST equal the reported
   score exactly — no undisclosed adjustments.
3. **Deterministic reasons:** reason strings are templated from the same inputs
   (reproducible), not free-form.
4. **Traceability:** output carries `spec_version` and the `detector spec_version`
   it scored, so a score traces to exact geometry.
5. **Negative contributions are shown** (e.g. C7 penalty, low volume) — the user
   sees *why points were lost*, not only gained.

---

## 4. Output schema (JSON)

```json
{
  "schema": "4ur4.confidence.v1",
  "version": "1.0.0",
  "detector_spec_version": "trendline-1.0.0",
  "symbol": "AAAA",
  "breakout_bar": 81,
  "confirmed_bar": 82,
  "score": 76,
  "score_kind": "heuristic",            // never "probability"
  "components": [
    { "id": "C1", "name": "line_fit_quality", "subscore": 0.94,
      "weight": 20, "contribution": 18.80,
      "reason": "Highs hug the log line (R2=0.94)." },
    { "id": "C5", "name": "retest_success", "subscore": 1.0,
      "weight": 15, "contribution": 15.00,
      "reason": "Retest held on bar 90; support confirmed." }
    /* … C2,C3,C4,C6,C7 … */
  ],
  "reasons": [
    "Strong line fit and a confirmed retest drive most of the score.",
    "Breakout volume only 1.6x average limited the volume contribution."
  ],
  "flags": ["LOW_VOLUME_NONE"],
  "disclaimers": [
    "Heuristic quality score, not a probability or trading advice.",
    "Excludes market sentiment (research-only under GOV-014)."
  ]
}
```

- `score_kind` is **always** `"heuristic"` in v1 (enforced).
- `disclaimers` are mandatory and non-empty.

> **Decision D-CF-03 — Schema surface** · Default: the above (score, components[],
> reasons[], version, disclaimers[]). · Alternative: add per-component
> percentile/rank once historical data exists. · Materiality: low · Human-approval:
> no.

---

## 5. Initial feature candidates for later ML (v2)

Captured now as **context** (no model built). Candidate features, all derivable
from the deterministic detector + price/volume:

- Line geometry: `slope m`, `R²_log`, `span (tB−tA)`, touch count/spacing.
- Breakout: close margin, `p_break` bars-to-confirm, volume ratio, gap-vs-no-gap.
- Pre-break structure: number of wick-breaks, time since ATH, drawdown from ATH.
- Post-break behaviour (label-time only): retest occurrence/depth, MAE/MFE.
- Cross-sectional context (future, sentiment-gated by GOV-014 — NOT in v1).

These are **candidates**, not commitments; feature selection is a v2 ticket.

---

## 6. Success labels for later ML (definition, human-approval flagged)

For a supervised v2, each confirmed breakout is later labeled **win/loss** by
**forward outcome**:

- **Candidate label (default):** a breakout is a **win** if, within horizon
  `H_label` bars after the confirmed bar, price achieves forward return `≥ +R_win`
  **before** hitting a stop of `−R_stop` from the breakout close; **loss**
  otherwise. Defaults proposed for discussion: `H_label = 60` bars, `R_win = +15%`,
  `R_stop = −7%` (a first-touch / triple-barrier style label).
- **Alternative:** simple sign of forward return at fixed horizon (no stop);
  simpler but ignores path/drawdown.

> **Decision D-CF-04 — Success label definition** · Default: triple-barrier
> (`+15% / −7% / 60 bars`, first touch). · Alternative: fixed-horizon return sign.
> · Materiality: **high** (defines what "confidence" is eventually calibrated
> against; wrong label → misleading future model). · **Human-approval: yes** for
> the exact thresholds/horizon.

Labels are computed **only for research/backtest**, never shown as a live
prediction under v1.

---

## 7. Calibration goals

- **v1 goal — rank-ordering:** higher scores should, on historical breakouts,
  correspond to a higher empirical win-rate (monotonic lift). v1 is validated by
  a **rank-ordering / lift** check on the golden + historical set, **not** by
  probability calibration.
- **v2 goal — reliability:** a future statistical model targets calibration
  (e.g. reliability diagram; target |predicted − observed| within a stated band,
  e.g. ≤ 10% per decile) and MUST be **backtested before shipping**.
- **No calibration claim for v1:** because v1 is heuristic, we make **no
  probability-calibration claim** and must not imply one.

> **Decision D-CF-05 — v1 validation metric** · Default: rank-ordering lift
> (e.g. Spearman of score vs realized win-rate deciles ≥ target, decided at
> backtest time). · Alternative: AUC once labels exist. · Materiality: med ·
> Human-approval: no.

---

## 8. Heuristic vs probability — the hard distinction

- A **heuristic score** ranks *structural quality*; it is an ordinal, engineered
  index. It does **not** estimate P(win).
- A **statistical probability** is a calibrated estimate of an outcome frequency,
  earned only via labeled data + backtesting + calibration (§6, §7).
- v1 is **heuristic**. UI, API, and copy MUST NOT render v1 as a probability,
  odds, or expected return. `score_kind:"heuristic"` and mandatory disclaimers
  enforce this at the data layer.

---

## 9. Future ML evolution (v2+)

1. **v2 = supervised model** trained on §5 features with §6 labels.
2. **Versioned:** every scorer carries `schema`+`version`; v1 and v2 coexist and
   are traceable.
3. **Backtested before shipping:** no model reaches users without an
   out-of-sample backtest meeting §7 calibration/lift targets — evidence
   attached to the promoting ticket.
4. **Sentiment (GOV-014):** F&G / regime may enter **only** at/after v2, **only**
   with human approval + a backtest showing it improves calibration/lift. Until
   then it is context, never a live confidence input.

---

## 10. Safeguards against misleading confidence claims

1. **No probability language for v1** anywhere user-facing (§8, D-CF-01).
2. **Mandatory disclaimers** in every output (§4): heuristic, not advice, excludes
   sentiment.
3. **No sentiment in v1** (GOV-014) — enforced by the component set (C1–C7 contain
   none) and asserted in tests (see evidence plan).
4. **No confidence from un-backtested inputs:** any new input (esp. sentiment)
   must pass backtest + human approval before it can move a score.
5. **Not financial advice:** outputs are signal-quality context, never orders or
   recommendations (matches vision out-of-scope list).
6. **Determinism guard:** identical inputs must yield identical scores — a
   regression fixture (below) locks this.

---

## 11. Evidence plan (what Verification will check post-freeze)

Deterministic fixtures a later, build-lifted ticket MUST produce (paralleling the
trendline golden examples GX-01…GX-12):

- **CF-EV-01:** the §2.2 worked example reproduced exactly → `score = 76`, with
  each component contribution matching to 2 decimals.
- **CF-EV-02:** a perfect-structure synthetic breakout → `score = 100`; a
  minimal-quality one → low score; asserts monotonic ordering between them.
- **CF-EV-03:** **no-sentiment assertion** — component ids are exactly
  `{C1..C7}`, none sentiment-derived; a test fails if any sentiment field appears
  (GOV-014 guard).
- **CF-EV-04:** schema-conformance — output validates against
  `4ur4.confidence.v1`, `score_kind == "heuristic"`, `disclaimers` non-empty.
- **CF-EV-05:** `Σ contributions` (clamped) `== score` (explainability integrity).
- **CF-EV-06:** determinism — same input scored twice → byte-identical output.
- **CF-EV-07:** retest present vs absent changes only C5 by its weighted delta
  (contribution isolation).

Each fixture pins numeric values to a stated precision so Verification is exact
and reproducible.

---

## Glossary additions proposed (for the Product Steward — do NOT self-edit)

- **Confidence v1 (heuristic score)** — deterministic 0–100 decomposable quality
  score for a confirmed breakout; explicitly **not** a probability.
- **Score component** — a named, bounded `[0,1]` sub-score with a points weight
  and a reason string.
- **Contribution** — `weight × sub-score`, the points a component adds to the
  total.
- **Success label (win/loss)** — the forward-outcome label used to train/validate
  future ML (triple-barrier default).
- **Calibration / rank-ordering lift** — the property that higher scores track
  higher realized win-rates.
- **score_kind** — output field fixed to `"heuristic"` in v1 to prevent
  probability mis-presentation.

---

## Open questions (for Orchestrator/Steward/human triage)

1. **OQ-CF-1 (D-CF-01, high):** Approve wording policy that v1 is presented as a
   heuristic quality score, never a probability.
2. **OQ-CF-2 (D-CF-04, high):** Approve the exact success-label thresholds
   (`+15% / −7% / 60 bars`) for future ML.
3. **OQ-CF-3:** Confirm C5 (retest) may be `0.5` for a "clean hold without formal
   retest," or should absence be strictly `0`?
4. **OQ-CF-4 (GOV-014):** Confirm sentiment stays entirely out of v1 and enters
   only post-backtest + approval (this spec assumes yes).
5. **OQ-CF-5:** Default weights (§2.1) — acceptable as tunable defaults, or does a
   human want to set initial weights?
