---
name: coverage
description: "Use to measure documentation completeness. Inventories code surface vs documented OKF concepts, computes coverage percentage, epistemic tag distribution, and OKF conformance, generates COVERAGE.md. Trigger with /doc-sync:coverage"
---

# coverage — Measure Documentation Completeness

**Announce:** "I'm using the doc-sync plugin to measure OKF bundle coverage."

## Locate the Bundle

- If a path argument is given, use it.
- Otherwise find the bundle root: the `index.md` whose frontmatter contains
  `okf_version:`. Fallback: `docs/okf/`, then `docs/`. `<bundle>/` refers to it below.

## Epistemic Tags

| Tag | Meaning |
|-----|---------|
| `[Code]` | Directly verifiable in source code |
| `[Inference]` | Deduced from code patterns, naming, structure |
| `[To confirm]` | Requires human/business validation |
| `[Declared]` | Explicitly stated by a human |
| `[Decision]` | Architecture or business decision with rationale |

## Process

### Step 1: Inventory Code Surface

Scan the project and list all:
- Modules / packages / top-level directories
- Routes / endpoints (REST, GraphQL, CLI commands)
- Tables / collections / models (the data layer — migrations, ORM)
- Services / key business logic files
- External integrations

Group by functional domain (not by file type).

### Step 2: Inventory Documented Surface

Inventory concepts by reading the `type` field in each concept's frontmatter.

Parse `<bundle>/features/*.md` (`type: Feature`) and extract:
- Which functional blocks are documented
- How many substantive assertions each contains
- Epistemic tag distribution per concept (cross-check against `confidence`)

Parse `<bundle>/data/*.md` (`type: "<DB> Table"`) and extract:
- Which tables/collections are documented vs present in code

Parse `<bundle>/ARCHITECTURE.md` and extract:
- Which components, data flows, and external dependencies are documented

Parse `<bundle>/decisions/*.md` (`type: Decision`) and count ADRs.

Also compute **OKF conformance**: % of non-reserved `.md` files with a parseable
frontmatter carrying a non-empty `type`.

For every concept, read `generated.at`, `verified` and `stale_after` from its
frontmatter and classify its trust tier:
- no `verified` key → **unverified**
- `verified` present, every actor is non-human (`process:...`) → **machine-confirmed**
- `verified` present with at least one `human:<id>` actor → **human-reviewed**

Then flag freshness issues, without treating either as an error:
- `generated.at` later than `max(verified[].at)` → **void** (the concept was
  rewritten after it was last confirmed)
- `stale_after` present and `today >= stale_after` → **expired**

### Step 3: Generate COVERAGE.md

Write or overwrite `<bundle>/COVERAGE.md` (it is itself a concept — keep its
frontmatter `type: Coverage Report`):

```markdown
---
type: Coverage Report
title: Documentation Coverage
generated: { by: doc-sync/<plugin version>, at: <ISO 8601 UTC> }
confidence: code
---

# Documentation Coverage

Last updated: YYYY-MM-DD

## Summary
- Functional blocks in code: N
- Functional blocks documented: N (Z%)
- Tables in code: N
- Tables documented: N (Z%)
- OKF conformance: N% of concepts have valid `type` frontmatter
- Total assertions: N
  - [Code]: N (X%)
  - [Inference]: N (X%)
  - [To confirm]: N (X%)
  - [Declared]: N (X%)
  - [Decision]: N (X%)
- Architecture Decision Records: N
- Trust tiers: N unverified (X%), N machine-confirmed (X%), N human-reviewed (X%)
- Freshness: N void (rewritten after verification), N expired (past `stale_after`)

## Coverage by Functional Block

| Block | Documented | Concept | Status | Tag Distribution |
|-------|-----------|---------|--------|-----------------|
| auth | ✅ Yes | features/auth.md | Current | 70% [Code], 20% [Inference], 10% [Declared] |
| payments | ⚠️ Partial | features/payments.md | Outdated | 30% [Code], 20% [Inference], 50% [To confirm] |
| reports | ❌ No | — | Missing | — |
| webhooks | ❌ No | — | Missing | — |

## Data Catalog Coverage

| Table | Documented | Concept |
|-------|-----------|---------|
| users | ✅ Yes | data/users.md |
| orders | ❌ No | — |

## Confidence Score

Overall documentation confidence: X%
(Weighted: [Code]=100%, [Declared]=90%, [Decision]=90%, [Inference]=50%, [To confirm]=10%)

## Trust & Freshness

| Tier | Count | % |
|------|------:|--:|
| Unverified — no `verified` entry | N | X% |
| Machine-confirmed — `verified` has only non-human actors | N | X% |
| Human-reviewed — `verified` has at least one `human:` actor | N | X% |

- Void (`generated.at` later than the last `verified[].at`): N concepts — list them, or "none"
- Expired (`today >= stale_after`): N concepts — list them, or "none"

Void and expired are signals to act on, not errors: re-run `challenge` to
re-confirm a void concept, or `interview` to refresh an expired one.

## Action Items

### High Priority
- [ ] Document: reports module (undocumented, high usage)
- [ ] Confirm: 12 [To confirm] items in payments

### Medium Priority
- [ ] Review: 5 [Inference] items in auth (never challenged)
- [ ] Document: webhooks module

### Low Priority
- [ ] Add ADRs for database and framework choices
```

### Step 4: Commit

Stage and commit: `docs: coverage report updated`

## Key Rules

- **Group by business domain** — not by technical layer
- **Compute a confidence score** — weighted by tag reliability, gives a single number to track over time
- **Report the trust-tier distribution and freshness** — unverified / machine-confirmed / human-reviewed counts, plus void and expired concepts; `confidence` is not replaced by this, the two axes are orthogonal
- **Prioritize action items** — undocumented high-traffic blocks first, suspect inferences in edge cases last
- **Track trends** — if previous COVERAGE.md exists, note improvements or regressions
- **Be honest** — a project with 100% coverage but 80% `[Inference]` is not well-documented
- **Review before commit:** show the diff and confirm with the user before running `git commit`.
