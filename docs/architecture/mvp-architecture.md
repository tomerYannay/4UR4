# 4UR4 — MVP Architecture (design / context)

> **Status: DESIGN / CONTEXT ONLY under [GOV-015](../../governance/build-freeze.md).**
> The build-freeze is **ON**. Nothing in this document is built, scaffolded, or
> merged as product code. This is a *recommendation* of structure, described in
> prose and diagrams. No source directories, packages, services, or schemas
> described here exist yet or may be created under freeze. Implementation is the
> Engineer's authority *after* a human lifts the freeze per-scope
> ([GOV-013](../../governance/approval-gate.md)).

## 1. Architectural stance

**Recommendation: a modular monorepo (a "modular monolith"), not microservices.**

Rationale, tied to the product values:
- **Correctness first.** The hard part of 4UR4 is a *correct, deterministic*
  trendline + backtesting core. That belongs in one well-tested library, not
  scattered across network boundaries.
- **Reproducibility.** A single repo with pinned dependencies and shared model
  versioning makes "same inputs → same signals" enforceable.
- **Anti-gold-plating (GOV-007).** Microservices buy independent scaling and
  deployment we do not need at MVP; they cost distributed-systems complexity we
  cannot justify. We defer that cost.
- **Clean seams for later split.** Modules communicate through **explicit
  internal interfaces** (not by reaching into each other's internals), so any
  module can later become a service without a rewrite.

> **Recorded alternative:** microservices / event-driven from day one — deferred
> as premature. **Safest default adopted:** modular monorepo with strict module
> boundaries.

## 2. Monorepo layout (described, NOT created)

Top-level modules/packages (illustrative names; **prose only** under freeze):

```
4ur4/                         (repo root — conceptual)
├── engine/        Python trendline + backtesting engine  (pure, deterministic core)
├── data/          Market-data abstraction layer          (provider-agnostic interface)
├── worker/        Scanner / batch daily S&P 500 job       (orchestrates engine over data)
├── api/           Thin read-model API service             (serves stored results)
├── alerts/        Alert pipeline                          (queue → notification channels)
├── web/           Web frontend                            (internal dashboard → SaaS)
├── db/            Schema + migrations (design docs now)   (PostgreSQL)
└── shared/        Cross-cutting types, model-version registry, provenance utils
```

Dependency direction (arrows point to what a module depends on):

```
web ─▶ api ─▶ db ◀─ worker ─▶ engine ─▶ (pure, no I/O)
                     │            ▲
                     ▼            │
                   data ──────────┘   (worker feeds data into engine)
alerts ◀─ worker            api ─▶ shared ◀─ everyone
```

Key rule: **`engine/` depends on nothing with I/O.** It receives plain data
(price bars) and returns plain results (trendlines, breakouts, scores). This is
what keeps the core testable and reproducible.

## 3. Component responsibilities

### 3.1 Python trendline & backtesting engine (`engine/`)
- The **pure, deterministic, testable core**. No network, no DB, no clock reads
  baked into logic (time is passed in).
- Responsibilities: fit ATH-anchored **log descending trendlines** (anchor at
  ATH wick, connect to a later high wick via the envelope rule, respect the
  above-intervening-highs tolerance), detect **confirmed breakouts**, detect
  **retests**, expire lines **~100 bars after breakout**, and (later) compute the
  **explainable, decomposable confidence score**.
- Backtesting harness: replay historical bars and emit signals + a calibration
  report. This is where the §Sentiment-Before-Evidence rule (see
  [`market-sentiment-specification.md`](../../product/market-sentiment-specification.md)
  §7) is proven or disproven.
- **Determinism requirement:** given the same bars + same algo version, identical
  output. Every run stamps the **trendline-algo version** and **confidence
  version** it used.

### 3.2 Market-data abstraction layer (`data/`)
- A **provider-agnostic interface** so 4UR4 is never locked to one vendor. The
  engine and worker speak to an internal contract (e.g. "give me adjusted daily
  OHLCV for symbol X over range R", "give me point-in-time S&P 500
  constituents"), and concrete adapters implement it per provider.
- This is the seam that ties directly to the data-provider research
  ([`../../product/data-provider-research.md`](../../product/data-provider-research.md)):
  **no provider is chosen here**; the interface exists so the choice stays
  human-gated and swappable.
- Owns **normalization** (split/dividend adjustment policy, symbol mapping) and
  **provenance tagging** (which provider, which snapshot).

### 3.3 Worker / scanner (`worker/`)
- Runs the **batch daily scan** of the S&P 500: pull bars via `data/`, run
  `engine/` over each name, persist trendlines/breakouts/retests/scores to
  PostgreSQL, and enqueue alerts for new confirmed events.
- Batch, idempotent, and **auditable**: each run writes a scan/run record (what
  ran, over what universe, with what versions, how long, what data snapshot).
- **Default cadence:** once daily, end-of-day aligned (matches the sentiment
  ingestion cadence). Intraday scanning is a recorded, deferred alternative.

### 3.4 API service (`api/`)
- **Thin**, serving **read models** only at MVP: it reads pre-computed results
  from PostgreSQL and returns them. It does **not** run the detector inline (keeps
  latency and correctness concerns separated; the worker is the source of truth).
- Later: authentication/authorization for SaaS, subscription-scoped queries.

### 3.5 Web frontend (`web/`)
- **Internal dashboard first** (inspect scans, trendlines, breakouts, scores,
  and — as context only — sentiment), **then SaaS**. Sequencing this way lets us
  validate correctness/explainability before selling anything.
- Renders the **decomposed** confidence score (named contributions), central to
  the explainability value.

### 3.6 Alert pipeline (`alerts/`)
- **Queue → notification channels.** The worker enqueues events; the pipeline
  fans out to channels (email first; others later). Decoupled via a queue so
  notification failures never corrupt scan/scoring correctness.
- SaaS **subscription alerts** are a later evolution of this pipeline, gated by
  auth/billing (deferred, §7).

## 4. Data model — PostgreSQL (high-level, design only)

Chosen store: **PostgreSQL** (relational integrity, time-series-friendly with
indexing, strong tooling; safest default for a correctness-first system).
Core tables (columns are indicative, **not** a migration):

| Table | Purpose | Notable fields (high level) |
|-------|---------|-----------------------------|
| `securities` | S&P 500 (and delisted) universe | symbol, name, sector, first/last seen, is_active |
| `bars` | Daily OHLCV (adjusted + policy noted) | security_id, date, o/h/l/c/v, adjustment_policy, data_source, snapshot_id |
| `trendlines` | Detected ATH-anchored log descending lines | security_id, ath_ref, anchor points, params, algo_version, valid_from/expiry |
| `breakouts` | Confirmed breakouts | trendline_id, confirm_date, confirmation_rule_ref, expiry (~100 bars) |
| `retests` | Post-breakout retests | breakout_id, retest_date, held (bool) |
| `scores` | Explainable confidence scores | breakout_id, value, **decomposition (named contributions)**, confidence_version |
| `alerts` | Emitted notifications | event_ref, channel, status, sent_at |
| `model_versions` | Registry of algo/score/data versions | version_id, kind, params_hash, created_at, notes |
| `scan_runs` (observability) | Audit of each batch scan | run_id, universe, versions, snapshot_id, started/finished, counts, data-quality flags |
| *(context-only)* `sentiment_snapshots` | F&G / regime **context** values | value(s), source, license_ref, snapshot_ts — **display/context only until GOV-014 §7 satisfied** |

Design notes:
- **Point-in-time correctness:** `securities` must support **historical
  constituents** (survivorship-bias-free) — see data research. Bars carry their
  `data_source` and `snapshot_id` for **provenance/reproducibility**.
- **Scores store their decomposition**, not just a number — explainability is
  schema-level, not an afterthought.
- The `sentiment_*` table exists in this *design* only to reserve the shape; it
  may not feed `scores` until the Sentiment-Before-Evidence rule is met.

## 5. Model / version tracking & provenance

Reproducibility is a first-class value, so versioning is architectural:
- **Trendline-algo version** and **confidence version** are stamped on every
  `trendlines`/`scores` row via `model_versions`.
- **Data snapshot / provenance**: each `bars` row (and each scan run) records
  which provider and snapshot produced it, so any historical signal can be
  **replayed and defended**.
- A signal is fully reproducible from: (algo_version, confidence_version,
  data snapshot_id, input bars). This is the concrete mechanism behind the
  "same inputs → same signals" value.

## 6. Cross-cutting concerns

### 6.1 Observability
- **Structured logging** across worker/api/alerts.
- **Metrics**: scan duration, names scanned, breakouts/retests found, alert
  delivery success.
- **Scan/run audit** (`scan_runs`) — every batch is accountable.
- **Data-quality checks**: gap/holiday detection, split-adjustment sanity,
  duplicate-bar detection, constituent drift; failures flag a run rather than
  silently producing wrong signals (correctness > availability).

### 6.2 Security boundaries
- **Secrets handling**: provider API keys and DB creds via a secrets manager /
  env injection, never in code or repo. (Design principle now; enforced later.)
- **No brokerage / no order-routing / no financial advice** — hard boundary
  inherited from the vision; the architecture has *no* module that could place
  trades.
- **PII minimization** for eventual SaaS: collect the minimum for auth/billing;
  isolate billing behind a dedicated boundary; prefer a third-party billing
  processor to avoid holding card data.
- **Least privilege between modules**: `engine/` has no credentials at all
  (pure). `api/` gets read-mostly DB access; `worker/` gets write access to
  result tables; `alerts/` only reads the event queue and writes delivery status.

## 7. What we deliberately defer (anti-gold-plating, GOV-007)

| Deferred | Why |
|----------|-----|
| Microservices / independent deploys | No scale need at MVP; adds distributed complexity. |
| Intraday / real-time scanning & streaming | Daily batch is sufficient to prove correctness first. |
| Sentiment **in the score** | Blocked until backtest + human approval (GOV-014 §7). |
| SaaS auth, billing, subscription alerts | Internal dashboard proves value before we monetize. |
| Learned/ML confidence or regime models | Start transparent + rules-based; earn complexity with evidence. |
| Multi-provider live failover | One human-gated provider first; the `data/` seam makes this cheap later. |
| Horizontal scaling / caching layers | Premature; revisit when a measured bottleneck exists. |

## 8. ASCII component diagram

```
                 ┌──────────────────────────────────────────────────────┐
                 │                     4UR4 monorepo                      │
                 │                                                        │
  external       │   ┌────────────┐        ┌───────────────────────┐     │
  market data ──▶│──▶│  data/     │◀──────▶│  worker/ (daily scan) │     │
  providers      │   │ (provider- │        │   pulls bars,         │     │
  (HUMAN-GATED)  │   │  agnostic) │        │   runs engine,        │     │
                 │   └────────────┘        │   persists results    │     │
                 │                         └─────────┬─────────────┘     │
                 │        ┌────────────┐             │  uses            │
                 │        │  engine/   │◀────────────┘                  │
                 │        │  PURE core │  (trendlines, breakouts,       │
                 │        │  no I/O    │   retests, expiry, score)      │
                 │        └────────────┘                               │
                 │                         writes │                     │
                 │                                ▼                     │
                 │                        ┌───────────────┐            │
                 │                        │  PostgreSQL   │            │
                 │                        │  (db/ schema) │            │
                 │                        └──┬────────┬───┘            │
                 │                    reads  │        │  events        │
                 │              ┌────────────▼──┐  ┌──▼──────────┐     │
                 │              │  api/ (thin,  │  │  alerts/    │     │
                 │              │  read models) │  │  queue→chan │     │
                 │              └───────┬───────┘  └──────┬──────┘     │
                 │                      │                 │            │
                 └──────────────────────┼─────────────────┼───────────┘
                                        ▼                 ▼
                                   ┌─────────┐     email / (later) SaaS
                                   │  web/   │        channels
                                   │dashboard│
                                   │ → SaaS  │
                                   └─────────┘
```

## 9. Human-approval flags raised here

- **Data provider selection** (feeds `data/` adapters) — HUMAN-GATED (GOV-013);
  see [`../../product/data-provider-research.md`](../../product/data-provider-research.md).
- **Lifting the build-freeze per-scope** before any of this is implemented
  (GOV-015 / GOV-013).
- **SaaS billing/PII architecture** — revisit for a formal privacy/security
  review before any customer data is collected.
- **Promoting sentiment into the score** — blocked (GOV-014 §7).

> Reminder: under **GOV-015 none of this is built yet.** This document is the
> map, not the territory.
