---
name: doc-coverage
description: "Use to measure documentation completeness. Inventories code surface vs documented surface, computes coverage percentage and epistemic tag distribution, generates COVERAGE.md. Trigger with /functional-doc-sync:doc-coverage"
---

# doc-coverage — Measure Documentation Completeness

**Announce:** "I'm using the functional-doc-sync plugin to measure documentation coverage."

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
- Models / schemas / data structures
- Services / key business logic files
- External integrations

Group by functional domain (not by file type).

### Step 2: Inventory Documented Surface

Parse `docs/features/*.md` and extract:
- Which functional blocks are documented
- How many substantive assertions each contains
- Epistemic tag distribution per file

Parse `docs/ARCHITECTURE.md` and extract:
- Which components are listed
- Which data flows are described
- Which external dependencies are documented

Parse `docs/decisions/*.md` and count ADRs.

### Step 3: Generate COVERAGE.md

Write or overwrite `docs/COVERAGE.md`:

```markdown
# Documentation Coverage

Last updated: YYYY-MM-DD

## Summary
- Functional blocks in code: N
- Functional blocks documented: N (Z%)
- Total assertions: N
  - [Code]: N (X%)
  - [Inference]: N (X%)
  - [To confirm]: N (X%)
  - [Declared]: N (X%)
  - [Decision]: N (X%)
- Architecture Decision Records: N

## Coverage by Functional Block

| Block | Documented | Doc File | Status | Tag Distribution |
|-------|-----------|----------|--------|-----------------|
| auth | ✅ Yes | features/auth.md | Current | 70% [Code], 20% [Inference], 10% [Declared] |
| payments | ⚠️ Partial | features/payments.md | Outdated | 30% [Code], 20% [Inference], 50% [To confirm] |
| reports | ❌ No | — | Missing | — |
| webhooks | ❌ No | — | Missing | — |

## Confidence Score

Overall documentation confidence: X%
(Weighted: [Code]=100%, [Declared]=90%, [Decision]=90%, [Inference]=50%, [To confirm]=10%)

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

- **Group by business domain** — not by technical layer (don't report "models: 80%, routes: 60%")
- **Compute a confidence score** — weighted by tag reliability, gives a single number to track over time
- **Prioritize action items** — undocumented high-traffic blocks first, suspect inferences in edge cases last
- **Track trends** — if previous COVERAGE.md exists, note improvements or regressions
- **Be honest** — a project with 100% coverage but 80% `[Inference]` is not well-documented
