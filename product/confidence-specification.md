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

> **Product Owner approved 2026-07-24 (HD-08) — Sentiment-Before-Evidence rule
> reaffirmed.** Sentiment stays **OUT** of the confidence score until BOTH (a) an
> **out-of-sample backtest demonstrates improvement** AND (b) an **explicit human
> approves** it. This is now the owner-approved governing rule (not merely a
> proposal). Wiring sentiment into the score before that evidence-and-approval gate
> is **rejected** as a governance violation; sentiment-as-context display remains a
> separate, human-gated matter (HD-09).

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

> **Decision D-CF-01 — Score meaning** · **Status: APPROVED (Product Owner,
> 2026-07-24, HD-04).** · Governing rule: Confidence v1 is a **0–100 heuristic
> quality score** (`score_kind:"heuristic"`, mandatory disclaimers), explicitly
> **NOT a probability**, never labeled "% chance," odds, or expected return. ·
> Allowed cosmetic alternatives: present as 0–1 or star tiers (still heuristic). ·
> Rejected: any "% chance"/probability rendering. · Materiality: **high**
> (mis-presentation is a user-trust/compliance risk). · Human-approval: yes —
> **granted 2026-07-24 (HD-04)** for the heuristic-not-probability policy.

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

> **Product Owner revised 2026-07-24 (HD-03) — propagation.** Per the revised
> breakout policy (trendline spec §13), **persistence above the line** and **volume
> confirmation** are **confidence/quality components — NOT breakout-validity
> gates**. They live here, in the scored, explainable layer, and never gate the
> breakout or delay its alert. Accordingly the component set now **explicitly
> includes a volume-confirmation component (C4)** and a **post-breakout
> persistence/quality component (C8)**, each independently explainable and
> inspectable. Weights were rebalanced to still sum to 100 (weights are tunable
> within the confidence workstream, per D-CF-02).

| # | Component | What it measures | Sub-score `s_i` formula (all clamp to [0,1]) | Default `w_i` (pts) |
|---|-----------|------------------|----------------------------------------------|--------------------:|
| C1 | **Line fit quality** | How cleanly highs hug the log line (R² of pivot highs vs `ŷ`). | `s = max(0, R²_log)` over the touching pivot highs. | 18 |
| C2 | **Touch count & spacing** | More, well-spaced touches = more-tested resistance. | `s = min(1, (n_touch−2)/(N_target−2)) · spacingFactor`, `N_target=5`; `spacingFactor = min(1, meanGap/minGapTarget)`. | 15 |
| C3 | **Breakout strength** | How decisively the close cleared the line. | `s = clamp( (ln C_bo − ŷ_bo) / margin_ref , 0, 1)`, `margin_ref = 0.05` (≈5%). | 15 |
| C4 | **Volume confirmation** (confidence-only, NOT a validity gate) | Volume expansion on breakout. Low volume lowers the score via this component and a `LOW_VOLUME` flag; it **never voids** the breakout (HD-03). | `s = clamp( (V_bo/SMA20_vol − 1) / (f_target − 1), 0, 1)`, `f_target = 2.0`. | 12 |
| C5 | **Retest success** | Did price retest and hold the line as support? | `s = 1` if `RETESTED`; `0.5` if clean no-retest hold; `0` if not yet / failed. | 15 |
| C6 | **Line maturity / age** | Longer-established resistance = more meaningful break. | `s = clamp( (tB − tA)/span_ref, 0, 1)`, `span_ref = 250` bars (~1yr daily). | 10 |
| C7 | **Cleanliness penalty** | Penalize many prior wick-breaks / near-pierces (false pressure). | `s = clamp(1 − n_wickbreak/wick_ref, 0, 1)`, `wick_ref = 5`. | 5 |
| C8 | **Post-breakout persistence** (confidence-only, NOT a validity gate) | How well the close **held above the line** in the bars after the alert. Rewards durable breakouts; does **not** gate validity or delay the alert (HD-03) — the breakout already fired on the first qualifying close. | `s = clamp( n_held / q_persist , 0, 1)`, where `n_held` = post-breakout bars closing above the line within a `q_persist`-bar window, default `q_persist = 5`. | 10 |
|   | **Total** | | | **100** |

> **Decision D-CF-02 — Component set & default weights** · **Revised 2026-07-24
> (HD-03 propagation):** component set is now **C1–C8**, weights summing to 100,
> explicitly including a **volume-confirmation** component (C4) and a
> **post-breakout persistence** component (C8) — both **confidence-only, not
> validity gates**. · Alternative: fold C7 into C2, or add an "ATR-normalized
> breakout strength." · Materiality: med (tunable; does not change score
> *meaning*). · Human-approval: no (tunable within the confidence workstream); the
> **move of persistence/volume from validity to confidence** is owner-approved via
> HD-03.

### 2.2 Worked example

A breakout with: `R²_log = 0.94`; `n_touch = 4`, good spacing (`spacingFactor =
1.0`); breakout close margin `ln C_bo − ŷ_bo = 0.03`; `V_bo/SMA20 = 1.6`;
`RETESTED`; `tB−tA = 180`; `n_wickbreak = 1`; and **4 of the first 5
post-breakout bars closed above the line** (`n_held = 4`, `q_persist = 5`).

| C | `s_i` | `w_i` | contribution |
|---|------:|------:|-------------:|
| C1 | 0.94 | 18 | 16.92 |
| C2 | `min(1,(4−2)/3)·1.0 = 0.667` | 15 | 10.00 |
| C3 | `0.03/0.05 = 0.60` | 15 | 9.00 |
| C4 | `(1.6−1)/(2.0−1) = 0.60` | 12 | 7.20 |
| C5 | 1.0 (RETESTED) | 15 | 15.00 |
| C6 | `180/250 = 0.72` | 10 | 7.20 |
| C7 | `1 − 1/5 = 0.80` | 5 | 4.00 |
| C8 | `4/5 = 0.80` | 10 | 8.00 |
| **Confidence** | | | **77.32 → 77** |

Reasons emitted, e.g. C5: *"Retest held on bar 90: low touched line (−0.4%) and
close reclaimed it — support confirmed."* C8: *"4 of the first 5 bars after the
breakout closed above the line — durable hold (persistence is a quality signal,
not a breakout gate)."*

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
  "confirmed_bar": 81,                   // HD-03: fires on first close; == breakout_bar
  "score": 77,
  "score_kind": "heuristic",            // never "probability"
  "components": [
    { "id": "C1", "name": "line_fit_quality", "subscore": 0.94,
      "weight": 18, "contribution": 16.92,
      "reason": "Highs hug the log line (R2=0.94)." },
    { "id": "C5", "name": "retest_success", "subscore": 1.0,
      "weight": 15, "contribution": 15.00,
      "reason": "Retest held on bar 90; support confirmed." },
    { "id": "C8", "name": "post_breakout_persistence", "subscore": 0.80,
      "weight": 10, "contribution": 8.00,
      "reason": "4 of first 5 post-breakout bars closed above the line (quality signal, not a gate)." }
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
- Breakout: close margin, volume ratio, gap-vs-no-gap. **(HD-03: there is no
  `p_break` bars-to-confirm feature — the breakout fires on the first qualifying
  close; "bars held above line" is captured instead as a post-break persistence
  feature, below.)**
- Pre-break structure: number of wick-breaks, time since ATH, drawdown from ATH.
- Post-break behaviour: **persistence** (bars/fraction closing above the line
  after the alert — the C8 quality signal), retest occurrence/depth, MAE/MFE
  (label-time for the outcome labels in §6).
- Cross-sectional context (future, sentiment-gated by GOV-014 — NOT in v1).

These are **candidates**, not commitments; feature selection is a v2 ticket.

---

## 6. Success labels for later ML (definition, human-approval flagged)

> **Product Owner revised 2026-07-24 (HD-05).** This section is **rewritten**. The
> single `+15% / −7% / 60 bars` triple-barrier label is **NOT** adopted as the only
> (or final) success definition. Instead, **multiple labels are stored per
> breakout**, and the `+15% / −7% / 60 bars` variant is retained only as an
> **INITIAL RESEARCH label — not product truth**. The **definitive** success
> definition is selected **later from backtest evidence (Phases 4/5/8) under human
> approval**, not fixed now.

For a supervised v2 — and for v1 rank-ordering validation — each confirmed
breakout has a **panel of labels computed and stored**, so the definitive success
definition can be chosen empirically rather than presumed:

- **Forward-horizon labels** at **5, 10, 20, and 60 bars** after the confirmed bar
  (e.g. sign and magnitude of forward return at each horizon).
- **Triple-barrier (first-touch) labels** at **+5% / −3%**, **+10% / −5%**, and
  **+15% / −7%** — each within its evaluation window (path/drawdown-aware).
- **MFE** — maximum favorable excursion (best unrealized gain reached).
- **MAE** — maximum adverse excursion (worst drawdown reached).
- **Failed-breakout** label — the breakout re-closed decisively below the line
  within the failure window (trendline spec §15).
- **Successful-retest** label — price retested the broken line and held as support
  (trendline spec §16).

All of the above are **stored together per breakout**. `+15% / −7% / 60 bars`
remains available among them as the **initial research label**, explicitly **not**
the final product truth.

> **Decision D-CF-04 — Success label definition** · **Status: REVISED (Product
> Owner, 2026-07-24, HD-05).** · Governing rule: **store MULTIPLE labels per
> breakout** — forward-horizon (5/10/20/60 bars), triple-barrier (+5%/−3%,
> +10%/−5%, +15%/−7%), plus **MFE, MAE, failed-breakout, and successful-retest**
> labels. `+15% / −7% / 60 bars` is kept as an **initial research label, not the
> final product truth**; the definitive success definition is chosen later from
> **backtest evidence (Phases 4/5/8), human-gated**. · Superseded formulation:
> triple-barrier `+15% / −7% / 60 bars` as the **sole** default label. · Rejected
> as sole label: fixed-horizon return sign alone (ignores path/drawdown). ·
> Materiality: **high** (defines what "confidence" is eventually calibrated
> against; a wrong/single label → misleading future model). · Human-approval: yes —
> **revised 2026-07-24 (HD-05)**; the final choice among stored labels remains
> human-gated at Phase 4/5/8.

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
3. **No sentiment in v1** (GOV-014) — enforced by the component set (C1–C8 contain
   none; volume C4 and persistence C8 are structural, not sentiment) and asserted
   in tests (see evidence plan). Reaffirmed owner-approved 2026-07-24 (HD-08).
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

- **CF-EV-01:** the §2.2 worked example reproduced exactly → `score = 77`
  (revised HD-03/HD-05 component set C1–C8), with each component contribution
  matching to 2 decimals, and `confirmed_bar == breakout_bar` (HD-03).
- **CF-EV-02:** a perfect-structure synthetic breakout → `score = 100`; a
  minimal-quality one → low score; asserts monotonic ordering between them.
- **CF-EV-03:** **no-sentiment assertion** — component ids are exactly
  `{C1..C8}`, none sentiment-derived; a test fails if any sentiment field appears
  (GOV-014 guard, HD-08 reaffirmed).
- **CF-EV-04:** schema-conformance — output validates against
  `4ur4.confidence.v1`, `score_kind == "heuristic"`, `disclaimers` non-empty.
- **CF-EV-05:** `Σ contributions` (clamped) `== score` (explainability integrity).
- **CF-EV-06:** determinism — same input scored twice → byte-identical output.
- **CF-EV-07:** retest present vs absent changes only C5 by its weighted delta
  (contribution isolation).
- **CF-EV-08 (HD-03 propagation):** volume (C4) and post-breakout persistence (C8)
  are **confidence-only** — asserts a **low-volume** and/or **non-persisting**
  breakout still yields a **valid, fired** breakout (`BROKEN_OUT` present,
  `confirmed_bar == breakout_bar`) with only the C4/C8 contributions reduced; the
  breakout is **never voided** by low volume or weak persistence.
- **CF-EV-09 (HD-05):** the stored **label panel** is present per breakout —
  forward-horizon (5/10/20/60), triple-barrier (+5/−3, +10/−5, +15/−7), MFE, MAE,
  failed-breakout, and successful-retest labels — with `+15/−7/60` flagged as the
  **initial research label**, not the definitive success definition.

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
- **Success label (panel)** — the set of forward-outcome labels stored per
  breakout (forward-horizon 5/10/20/60; triple-barrier +5/−3, +10/−5, +15/−7; MFE;
  MAE; failed-breakout; successful-retest) used to train/validate future ML. The
  definitive success definition is chosen later from backtest evidence (HD-05);
  `+15/−7/60` is the initial research label, not final product truth.
- **Post-breakout persistence (C8)** — a confidence/quality component measuring how
  well the close held above the line after the alert; **not** a breakout-validity
  gate (HD-03).
- **Calibration / rank-ordering lift** — the property that higher scores track
  higher realized win-rates.
- **score_kind** — output field fixed to `"heuristic"` in v1 to prevent
  probability mis-presentation.

---

## Open questions (for Orchestrator/Steward/human triage)

1. **OQ-CF-1 (D-CF-01, high) — RESOLVED 2026-07-24 (HD-04):** v1 is **approved** as
   a 0–100 heuristic quality score, never a probability.
2. **OQ-CF-2 (D-CF-04, high) — RESOLVED (REVISED) 2026-07-24 (HD-05):** do **not**
   adopt `+15% / −7% / 60 bars` as the sole/final label; **store the multi-label
   panel** (§6) and choose the definitive success definition later from backtest
   evidence, human-gated. `+15/−7/60` is the initial research label only.
3. **OQ-CF-3:** Confirm C5 (retest) may be `0.5` for a "clean hold without formal
   retest," or should absence be strictly `0`?
4. **OQ-CF-4 (GOV-014) — RESOLVED 2026-07-24 (HD-08):** sentiment stays **out** of
   v1 and enters only after an out-of-sample backtest shows improvement **AND** a
   human approves (Sentiment-Before-Evidence rule, owner-approved).
5. **OQ-CF-5:** Default weights (§2.1) — acceptable as tunable defaults, or does a
   human want to set initial weights?
