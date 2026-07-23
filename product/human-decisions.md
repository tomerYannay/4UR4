# 4UR4 — Human Decision Register

Status: planning artifact under [GOV-015](../governance/build-freeze.md); these are
**proposals for the product owner, not decisions taken**.

> These are the material decisions that genuinely require the product owner
> ([GOV-013](../governance/approval-gate.md)). Each lists a recommended option, the
> reason, alternatives, the cost of delaying, and a safe default to hold until the
> owner decides. Agents must not self-approve these. Trivial/tunable choices
> (e.g. pivot `k`, tolerances, default weights) are intentionally **excluded** —
> they are per-ticket, versioned, and revisable within their workstream.

| ID | Materiality | Decision (short) |
|----|-------------|------------------|
| HD-01 | high | Price-adjustment basis |
| HD-02 | high | Envelope selection rule (upper log-hull) |
| HD-03 | high | Breakout confirmation policy |
| HD-04 | high | Confidence presented as heuristic, not probability |
| HD-05 | high | ML success-label thresholds (triple-barrier) |
| HD-06 | high | Data-provider selection + recurring cost |
| HD-07 | high | Survivorship-bias-free constituents + delisted history |
| HD-08 | high | Promoting sentiment into the confidence score |
| HD-09 | med  | External Fear & Greed source + redistribution/display rights |
| HD-10 | high | SaaS billing/PII security review |

---

## HD-01 — Price-adjustment basis · materiality: **high**
- **Decision:** Which price series feeds ATH selection, pivots, line fitting, and
  breakout tests?
- **Recommended option:** **Split-adjusted, dividend-UNadjusted ("as-traded")**,
  used consistently across all stages (trendline spec §2, D-TL-01).
- **Reason:** Matches the chart a trader actually sees, keeps the ATH stable, and
  avoids negative adjusted prices on long histories that would break `ln`.
- **Alternatives:** Fully adjusted (total-return) close; raw unadjusted (rejected —
  splits inject false ATHs/breakouts).
- **Cost of delaying:** Blocks Phase 1 (data) and Phase 2 (engine) — the adjustment
  basis changes *which bar is the ATH* and therefore every downstream signal.
- **Safe default:** Hold on split-adjusted/dividend-unadjusted; build fixtures
  against it. Reversible before Phase 1 implementation.

## HD-02 — Envelope selection rule · materiality: **high**
- **Decision:** The canonical rule that selects the single second anchor `B*` and
  thus THE line.
- **Recommended option:** **Upper convex hull in log space from the ATH** — the
  shallowest descending log line that dominates all intervening highs within
  tolerance `ε` (trendline spec §8, D-TL-04).
- **Reason:** This is the load-bearing geometric *definition of the product*;
  resistance must sit above the highs it caps. The hull is deterministic and
  noise-tolerant.
- **Alternatives:** Naive "steepest line through two most significant pivots"
  (rejected — cuts through intervening highs).
- **Cost of delaying:** Blocks Phase 2 entirely; the engine cannot be built or
  fixture-tested without the confirmed definition.
- **Safe default:** Hold on upper-log-hull; encode discrimination fixture GX-02
  (must pick `B*=(45,92)`, not `(20,96)`).

## HD-03 — Breakout confirmation policy · materiality: **high**
- **Decision:** What counts as a *confirmed* breakout.
- **Recommended option:** **Close-based cross** (`ε_break=0.01`) **+ persistence**
  (`p_break=2` bars) **+ soft volume** (`f_vol=1.0×` 20-bar avg; low volume flags
  `LOW_VOLUME`, does not void) (trendline spec §13, D-TL-07).
- **Reason:** Defines *when the product fires*; balances signal count against false
  positives while keeping correctness/explainability separate (volume softens
  score, not validity).
- **Alternatives:** Single-close breakout (more signals, more false positives);
  hard volume gate (fewer signals, discards borderline valid breaks).
- **Cost of delaying:** Blocks Phase 3 (breakout/retest engine).
- **Safe default:** Hold on the close+persistence+soft-volume policy; fixtures
  GX-03/GX-11 encode it.

## HD-04 — Confidence is a heuristic, not a probability · materiality: **high**
- **Decision:** How the confidence score is *presented* in UI/API/copy.
- **Recommended option:** Present Confidence v1 as a **0–100 heuristic quality
  score**, `score_kind:"heuristic"`, with mandatory disclaimers; **never** labeled
  a probability, odds, or expected return (confidence spec §1, §8, D-CF-01).
- **Reason:** Mis-presenting a heuristic as a probability is a user-trust and
  compliance risk. Explainability integrity depends on honest framing.
- **Alternatives:** 0–1 scale or star tiers (cosmetic, allowed); presenting as
  "% chance" (rejected — prohibited).
- **Cost of delaying:** Blocks Phase 5 UI wording and Phase 6 dashboard copy;
  low cost to hold since the data-layer default is already `"heuristic"`.
- **Safe default:** Enforce `score_kind:"heuristic"` + disclaimers at the data
  layer regardless; owner confirms user-facing wording.

## HD-05 — ML success-label thresholds · materiality: **high**
- **Decision:** How each historical breakout is labeled win/loss for future ML (v2)
  and for Confidence v1 rank-ordering validation.
- **Recommended option:** **Triple-barrier, first-touch**: win if forward return
  reaches **+15%** before a **−7%** stop within **60 bars**, else loss (confidence
  spec §6, D-CF-04).
- **Reason:** Defines what "confidence" is eventually calibrated against; a wrong
  label yields a misleading future model. Path/drawdown-aware.
- **Alternatives:** Fixed-horizon return sign (simpler; ignores path/drawdown).
- **Cost of delaying:** Blocks Confidence-v1 lift validation (Phase 5) and Phase 8
  ML labels; delaying leaves the calibration target undefined.
- **Safe default:** Hold on triple-barrier defaults for research/backtest only
  (never shown live); thresholds tunable before Phase 8 modeling.

## HD-06 — Data-provider selection + recurring cost · materiality: **high**
- **Decision:** Which market-data provider(s) to license, and approval of the
  recurring spend.
- **Recommended option:** **No recommendation — human-gated.** Agents produce the
  R1–R8 research and comparison matrix; the human selects and approves spend
  (data-provider research; architecture §9, [GOV-013](../governance/approval-gate.md)).
- **Reason:** Recurring cost and licensing are commercial commitments only a human
  may make; provider names are deliberately omitted to avoid steering.
- **Alternatives:** Bundle vs. best-of-breed across vendors (a decision the matrix
  informs).
- **Cost of delaying:** Blocks Phase 1 (data foundation) and everything downstream.
- **Safe default:** Continue research-only; **default MVP cadence is EOD/daily**.
  Commit nothing until the owner decides.

## HD-07 — Survivorship-bias-free constituents + delisted history · materiality: **high**
- **Decision:** Whether to license point-in-time S&P 500 membership and delisted
  price history (frequently a paid dataset).
- **Recommended option:** **Acquire it (human-gated)** — treated as
  **correctness-critical**; without it, backtests are survivorship-biased (data
  research R4/R5).
- **Reason:** Backtests and regime/breadth stats are misleading without the actual
  historical members and delisted names.
- **Alternatives:** Use today's members projected backward (rejected — biased);
  defer accurate backtesting (limits trust in Confidence v1 lift).
- **Cost of delaying:** Blocks trustworthy Phase 4 backtesting and Phase 5/8
  calibration.
- **Safe default:** Research availability/cost now; hold the purchase for the owner;
  flag any Phase 4 backtest run without it as **biased/provisional**.

## HD-08 — Promoting sentiment into the confidence score · materiality: **high**
- **Decision:** Whether/when Fear & Greed or the regime score may enter the
  **scored** confidence model.
- **Recommended option:** **Blocked** until BOTH (a) a backtest shows the feature
  improves calibration on out-of-sample data, AND (b) explicit human approval — the
  Sentiment-Before-Evidence rule (sentiment spec §7, [GOV-014](../governance/market-sentiment-context.md)).
- **Reason:** Protects correctness (no unproven input inflating trust) and
  explainability (every scored contribution must have evidence).
- **Alternatives:** Display sentiment as *context only* next to a signal (allowed
  after a human approves a display ticket + HD-09); wiring it into the score early
  (rejected — governance violation).
- **Cost of delaying:** None to the MVP — Confidence v1 is defined to exclude
  sentiment; this decision only gates Phase 8+.
- **Safe default:** Keep sentiment out of the score (enforced by the C1–C7 set and
  CF-EV-03 test); research only.

## HD-09 — External Fear & Greed source + redistribution/display rights · materiality: **med**
- **Decision:** Which sentiment source (if any) to use, and confirmation it permits
  commercial **display/redistribution** to end users.
- **Recommended option:** **Human-gated selection**; safest interim default is the
  **4UR4-reconstructed approximation** built only from inputs 4UR4 already has
  redistribution-safe rights to (sentiment spec §2.2/§3, data research R6/R7).
- **Reason:** Showing a third party's proprietary index to paying subscribers may
  need a display/redistribution license distinct from data access; "free to fetch"
  ≠ "free to resell/show." Highest legal-risk area.
- **Alternatives:** A licensed published composite (paid, redistribution-checked);
  a vendor API (licensing must be verified).
- **Cost of delaying:** None to MVP core; gates any user-facing sentiment display in
  Phase 7.
- **Safe default:** Research licensing (R6/R7) only; hold selection for the owner;
  do not display any third-party index until rights are confirmed.

## HD-10 — SaaS billing/PII security review · materiality: **high**
- **Decision:** Approve the privacy/security posture before any customer or billing
  data is collected.
- **Recommended option:** **Require a formal privacy/security review** before Phase
  7 SaaS work: PII minimization, isolated billing behind a **third-party
  processor** (no card data held), least-privilege module access (architecture
  §6.2, §9).
- **Reason:** Collecting customer/billing data creates a compliance surface that
  must be reviewed by a human before exposure.
- **Alternatives:** Hold card data directly (rejected — unnecessary risk); defer
  review until after launch (rejected — exposure precedes review).
- **Cost of delaying:** None to Phases 0–6 (internal only); a hard gate on Phase 7.
- **Safe default:** Keep the MVP internal-only (no customer PII) until the review
  is done.

---

*This register is a proposal pending human approval ([GOV-013](../governance/approval-gate.md));
the build-freeze ([GOV-015](../governance/build-freeze.md)) remains ON.*
