---
name: update
description: "Use after any code change with functional impact to sync documentation. Analyzes git diff, updates affected OKF concepts, refreshes their frontmatter, and adds a functional entry to log.md. Trigger with /doc-sync:update"
---

# update — Post-Change Documentation Sync

**Announce:** "I'm using the doc-sync plugin to update the OKF bundle after this change."

## Locate the Bundle

- If a path argument is given, use it.
- Otherwise find the bundle root: the `index.md` whose frontmatter contains
  `okf_version:`. Fallback if none found: `docs/okf/`, then `docs/`.
- `<bundle>/` refers to that root below. If no bundle exists, suggest `/doc-sync:init`.

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

**Identify impacted concepts:**
- Map changed files to their functional block
- Find the corresponding `<bundle>/features/*.md` concept(s)
- If no feature concept exists for the impacted block, create one (with frontmatter)

**Update feature concepts:**
- Modify the relevant sections
- Preserve existing epistemic tags on unchanged content
- New content: tag `[Code]` if directly verifiable, `[Inference]` if deduced
- Remove or update any content that is now incorrect
- **Refresh frontmatter** of each touched concept: bump `timestamp` (ISO 8601) and
  recompute `confidence` from the inline tags now present

**If the schema/data layer changed** (migration added, model field changed):
- Update the affected `<bundle>/data/<table>.md` concept's `# Schema` (columns,
  nullability, constraints — read the DDL/model literally, `NOT NULL`/`UNIQUE`
  exactly as written) and FK links
- Add a new table concept if a new table/collection appeared (use `templates/TABLE.md`)
- Refresh that concept's `timestamp`/`confidence`

**Add an entry to `<bundle>/log.md`** (RESERVED OKF file — no frontmatter, newest
first; create the date heading if today's is absent). Functional changes only:
```
## YYYY-MM-DD

* **Update**: <functional description — what the user/system sees differently>.
  Why: <rationale if known, otherwise [To confirm]>. Impact: <features/blocks>.
  Docs: <concepts updated>.
```
(Use `**Creation**` for a new feature, `**Deprecation**` for a removal.)

**Update ARCHITECTURE.md if needed:**
- New module/service/route/model added
- Dependency added or removed
- Data flow changed

### Step 3: If No Functional Change

- Skip doc update
- Optionally inform: "This change is technical only — no doc update needed."

### Step 4: Update COVERAGE.md

- If new modules/routes/components/tables appeared, add them to the coverage table
- Update tag distribution if changed
- Keep its frontmatter (`type: Coverage Report`)

### Step 4.5: Refresh Indexes & Documentation Map

- If a concept under `features/`, `decisions/`, or `data/` was **created or deleted**:
  - update the matching `<dir>/index.md` (OKF progressive disclosure), and
  - update the bundle-root `<bundle>/index.md` listing, and
  - regenerate the CLAUDE.md map section (same logic as `doc-sync:init` Step 5)
- If only existing concepts were modified (no new/deleted files) → indexes are still
  accurate, skip

### Step 5: Stage Together

- Stage doc changes alongside code changes
- Suggest commit message: `feat: <what> — docs updated`

## Key Rules

- **Atomic updates:** doc changes go in the same commit as code changes
- **Don't over-document:** only document functional impact, not implementation details
- **Preserve human input:** never overwrite `[Declared]` content without explicit instruction
- **Flag uncertainty:** when the rationale for a change is unclear, use `[To confirm]` and note it
- **Detect drift:** if you notice existing doc that contradicts the current code (even outside the current diff), flag it but don't silently fix it — ask first
