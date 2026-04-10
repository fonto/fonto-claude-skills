---
name: update
description: "Use after any code change with functional impact to sync documentation. Analyzes git diff, updates affected feature docs, and adds a functional changelog entry. Trigger with /doc-sync:update"
---

# update — Post-Change Documentation Sync

**Announce:** "I'm using the doc-sync plugin to update documentation after this change."

## Epistemic Tags

| Tag | Meaning |
|-----|---------|
| `[Code]` | Directly verifiable in source code |
| `[Inference]` | Deduced from code patterns, naming, structure |
| `[To confirm]` | Requires human/business validation |
| `[Declared]` | Explicitly stated by a human |
| `[Decision]` | Architecture or business decision with rationale |

## Process

### Step 1: Identify What Changed

- Run `git diff` (or `git diff HEAD~N` if a commit range is specified)
- List modified, added, deleted files
- Classify each change:
  - **Functional** — behavior change, new feature, modified business rule, new route/endpoint
  - **Technical** — refactor, performance, style, dependency update, config change with no functional impact

### Step 2: If Functional Change Detected

**Identify impacted docs:**
- Map changed files to their functional block
- Find the corresponding `docs/features/*.md` file(s)
- If no feature doc exists for the impacted block, create one

**Update feature docs:**
- Modify the relevant sections
- Preserve existing epistemic tags on unchanged content
- New content: tag `[Code]` if directly verifiable, `[Inference]` if deduced
- Remove or update any content that is now incorrect

**Add changelog entry to `docs/CHANGELOG-FUNCTIONAL.md`:**
```
## YYYY-MM-DD — <short description>
- **What changed:** <functional description — what the user/system sees differently>
- **Why:** <rationale if known, otherwise [To confirm]>
- **Files impacted:** <list of code files>
- **Doc updated:** <list of docs/*.md files modified>
```

**Update ARCHITECTURE.md if needed:**
- New module/service/route/model added
- Dependency added or removed
- Data flow changed

### Step 3: If No Functional Change

- Skip doc update
- Optionally inform: "This change is technical only — no doc update needed."

### Step 4: Update COVERAGE.md

- If new modules/routes/components appeared, add them to the coverage table
- Update tag distribution if changed

### Step 5: Stage Together

- Stage doc changes alongside code changes
- Suggest commit message: `feat: <what> — docs updated`

## Key Rules

- **Atomic updates:** doc changes go in the same commit as code changes
- **Don't over-document:** only document functional impact, not implementation details
- **Preserve human input:** never overwrite `[Declared]` content without explicit instruction
- **Flag uncertainty:** when the rationale for a change is unclear, use `[To confirm]` and note it
- **Detect drift:** if you notice existing doc that contradicts the current code (even outside the current diff), flag it but don't silently fix it — ask first
