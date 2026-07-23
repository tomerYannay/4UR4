# 4UR4 Glossary (shared vocabulary)

A single, authoritative vocabulary keeps tickets, plans, and evidence
consistent (supports **traceability** and **reproducibility**). Terms are
descriptive context; thresholds and formulas are **defined per ticket**, never
here.

| Term | Meaning in 4UR4 |
|------|-----------------|
| **ATH** | All-time high; the anchor point for a descending trendline. |
| **Log descending trendline** | A downward trendline fitted in logarithmic price space from the ATH along subsequent lower highs. |
| **Breakout** | Price action that crosses above the descending trendline under defined confirmation criteria. |
| **Confirmed breakout** | A breakout that satisfies the confirmation rules for a ticket (e.g. close-based, volume, persistence) — rules TBD per ticket. |
| **Retest** | Price returning toward the broken trendline and holding it as support. |
| **Confidence score** | A transparent, decomposed 0–1 (or 0–100) rating of signal quality. |
| **Explainability** | The property that a score can be broken into named, inspectable contributions. |
| **Fear & Greed (F&G)** | A market-sentiment indicator used as *context* to modulate confidence. |
| **Market-regime score** | A proprietary measure of overall market state (e.g. risk-on/risk-off) used as context. |
| **Sentiment context** | Collective term for F&G + regime inputs. Research-only for now ([GOV-014](../governance/market-sentiment-context.md)). |
| **Ticket** | A GitHub Issue representing one unit of governed work. |
| **Evidence** | Repository-verifiable proof a ticket is Done (commits, tests, CI, links). |
| **Ready** | A ticket that meets the [Definition of Ready](../governance/definition-of-ready.md). |
| **Done** | A ticket that meets the [Definition of Done](../governance/definition-of-done.md) with evidence. |

> If a term is missing or ambiguous, the **Product Steward** adds it here as part
> of making a ticket Ready — not the agent that happens to trip over it.
