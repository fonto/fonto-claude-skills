---
name: challenge
description: "Use for periodic review or after major refactoring. Cross-references documentation against current code, identifies inconsistencies, dead docs, undocumented features, suspect inferences, and OKF conformance issues. Trigger with /doc-sync:challenge"
---

# challenge — Verify Documentation Accuracy

**Announce:** "I'm using the doc-sync plugin to challenge the OKF bundle against the current code."

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

### Step 1: Cross-Reference Doc vs Code

For each `<bundle>/features/*.md`:
- Verify assertions tagged `[Code]` against current source — do they still hold?
- Check documented flows against actual code paths
- Identify **dead doc:** features documented but no longer present in code
- Identify **undocumented code:** code paths not covered by any feature concept

For `<bundle>/ARCHITECTURE.md`:
- Verify component list matches actual project structure
- Check dependency map against current imports/configs
- Verify external integrations still exist

For each `<bundle>/data/*.md` (table concepts):
- Verify the `# Schema` matches the real schema (migrations / ORM models)
- Flag columns/tables removed from code, and tables present in code but undocumented
- Check FK links resolve to existing table concepts

### Step 2: Check Inference Validity

- Re-evaluate all `[Inference]` tags against current code
- Flag any that:
  - Contradict current code behavior
  - Describe removed functionality
  - Make assumptions no longer supported by code structure

### Step 2.5: Check OKF Conformance

- Every non-reserved `.md` has a parseable YAML frontmatter with a non-empty `type`
- Reserved files: bundle-root `index.md` has `okf_version`; other `index.md` and all
  `log.md` carry no frontmatter; `log.md` is date-grouped, newest first
- Cross-links (markdown links between concepts) resolve to existing files
- Flag any violation (these are conformance issues, not behavior issues)

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
- OKF conformance issues: N

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

## OKF Conformance
| File | Issue | Suggested Fix |
|------|-------|--------------|
| features/legacy.md | Missing `type` in frontmatter | Add `type: Feature` |
| data/orders.md | FK link to `/data/users.md` is broken | Create concept or fix link |
```

### Step 4: Apply Fixes

- **Auto-fix clear inconsistencies:** renamed files, moved modules, updated values,
  missing/invalid `type` frontmatter — apply directly, tag `[Code]`
- **Flag ambiguous issues:** change tag to `[To confirm]`, add comment with challenge date
- **Remove dead doc:** move to a `<bundle>/_archive/` directory (don't delete — preserve
  history). Archived concepts keep valid frontmatter so the bundle stays conformant.
- **Create stubs for undocumented code:** generate minimal feature concept (with
  frontmatter) tagged `[Inference]`; add a table concept for any undocumented table

### Step 5: Suggest Next Steps

- If many `[To confirm]` items: suggest `/doc-sync:interview`
- If many undocumented modules: suggest targeted `/doc-sync:init` on specific directories
- Update COVERAGE.md

**Commit:** `docs: challenge review — N issues found, M auto-fixed`

## Key Rules

- **Don't silently fix ambiguous issues** — flag and ask
- **Preserve [Declared] content** — if declared content contradicts code, flag the contradiction but don't auto-correct (the code might be wrong)
- **Archive, don't delete** — dead doc may contain historical context worth keeping
- **Be specific** — every issue in the report must reference exact file, section, and line/assertion
- **Prioritize** — undocumented high-traffic code paths are more urgent than suspect inferences in edge cases
