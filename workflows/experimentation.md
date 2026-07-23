# Workflow — Experimentation

Experiments de-risk ideas **before** they cost roadmap space. They are bounded,
disposable, and evidence-producing — controlled creativity with a stop condition.

## When to run one

- An idea's value or feasibility is uncertain, and a small test would resolve it.
- Sentiment-context questions (Fear & Greed, market-regime) that inform the
  confidence thesis — **research only** ([GOV-014](../governance/market-sentiment-context.md)).

## Rules

- Every experiment states a **hypothesis**, a **method**, a **success/kill
  metric**, a **time/effort box**, and a **decision rule** up front.
  Use [`templates/experiment.md`](../templates/experiment.md).
- Experiments are **not** product features. Under the
  [build-freeze](../governance/build-freeze.md) they produce **context artifacts and
  throwaway analysis only** — never merged product code.
- An experiment has **one** of three outcomes: **adopt** (becomes an idea/roadmap
  candidate via triage), **iterate** (one bounded follow-up), or **drop** (archived
  with findings). No open-ended exploration.
- Findings are recorded as **context** (research brief / idea card), preserving
  **traceability** from question → method → result.
- Experiment volume is rationed by the idea budget ([GOV-008](../governance/ticket-hygiene.md)).

## Flow

```
Idea (uncertain) ─▶ Experiment (boxed, hypothesis + kill metric)
   ─▶ result ─▶ adopt / iterate / drop ─▶ Inbox triage (human + Steward)
```
