---
name: doc-challenge
description: "Use for periodic review or after major refactoring. Cross-references documentation against current code, identifies inconsistencies, dead docs, undocumented features, and suspect inferences. Trigger with /functional-doc-sync:doc-challenge"
---

# doc-challenge — Verify Documentation Accuracy

**Announce:** "I'm using the functional-doc-sync plugin to challenge the documentation against the current code."

## Epistemic Tags

| Tag | Meaning |
|-----|---------|
| `[Code]` | Directly verifiable in source code |
| `[Inference]` | Deduced from code patterns, naming, structure |
| `[To confirm]` | Requires human/business validation |
| `[Declared]` | Explicitly stated by a human |
| `[Decision]` | Architecture or business decision with rationale |

## Process

### Step 1: Cross-Reference Doc vs Code

For each `docs/features/*.md`:
- Verify assertions tagged `[Code]` against current source — do they still hold?
- Check documented flows against actual code paths
- Identify **dead doc:** features documented but no longer present in code
- Identify **undocumented code:** code paths not covered by any feature doc

For `docs/ARCHITECTURE.md`:
- Verify component list matches actual project structure
- Check dependency map against current imports/configs
- Verify external integrations still exist

### Step 2: Check Inference Validity

- Re-evaluate all `[Inference]` tags against current code
- Flag any that:
  - Contradict current code behavior
  - Describe removed functionality
  - Make assumptions no longer supported by code structure

### Step 3: Produce Challenge Report

Output a structured report:

```markdown
# Challenge Report — YYYY-MM-DD

## Summary
- Items checked: N
- Confirmed OK: N
- Inconsistencies found: N
- Dead documentation: N
- Undocumented code: N
- Suspect inferences: N

## Inconsistencies
| File | Section | Issue | Suggested Fix |
|------|---------|-------|--------------|
| features/auth.md | Password Reset | Token expiry documented as 24h, code shows 1h | Update doc |

## Dead Documentation
| File | Section | Reason |
|------|---------|--------|
| features/legacy-export.md | All | Module removed in commit abc123 |

## Undocumented Code
| Module/Path | Apparent Function | Priority |
|-------------|------------------|----------|
| src/services/webhooks.js | Webhook dispatch system | High |

## Suspect Inferences
| File | Assertion | Concern |
|------|-----------|---------|
| features/billing.md | "[Inference] Invoices are generated monthly" | No scheduling logic found in code |
```

### Step 4: Apply Fixes

- **Auto-fix clear inconsistencies:** renamed files, moved modules, updated values — apply directly, tag `[Code]`
- **Flag ambiguous issues:** change tag to `[To confirm]`, add comment with challenge date
- **Remove dead doc:** move to a `docs/_archive/` directory (don't delete — preserve history)
- **Create stubs for undocumented code:** generate minimal feature doc tagged `[Inference]`

### Step 5: Suggest Next Steps

- If many `[To confirm]` items: suggest `/functional-doc-sync:doc-interview`
- If many undocumented modules: suggest targeted `/functional-doc-sync:doc-init` on specific directories
- Update COVERAGE.md

**Commit:** `docs: challenge review — N issues found, M auto-fixed`

## Key Rules

- **Don't silently fix ambiguous issues** — flag and ask
- **Preserve [Declared] content** — if declared content contradicts code, flag the contradiction but don't auto-correct (the code might be wrong)
- **Archive, don't delete** — dead doc may contain historical context worth keeping
- **Be specific** — every issue in the report must reference exact file, section, and line/assertion
- **Prioritize** — undocumented high-traffic code paths are more urgent than suspect inferences in edge cases
