---
name: functional-doc-sync
description: Maintain functional documentation in sync with code evolution. Use when creating, updating, reviewing, or retroactively documenting a codebase. Modes - init (retrodocument), update (sync after changes), interview (capture tacit knowledge), challenge (verify accuracy), coverage (measure completeness).
---

# Functional Documentation Sync

## Overview

Keep functional documentation accurate and in sync with code across any project and stack.

**Core principle:** Documentation lives in `docs/` at project root, in Markdown, versioned with the code. Every documented assertion carries an epistemic tag indicating its source and confidence level.

**Announce at start:** "I'm using the functional-doc-sync skill to [init/update/interview/challenge/check coverage of] the project documentation."

## Epistemic Tags

Every substantive statement in generated documentation MUST be prefixed with one of:

| Tag | Meaning | Source |
|-----|---------|--------|
| `[Code]` | Directly verifiable in source code | Code analysis |
| `[Inference]` | Deduced from code patterns, naming, structure | AI interpretation |
| `[To confirm]` | Requires human/business validation | Uncertain or ambiguous |
| `[Declared]` | Explicitly stated by a human (dev, PO, business) | Interview or input |
| `[Decision]` | Architecture or business decision with rationale | ADR or declared |

**Rule:** When in doubt, use `[To confirm]`. Never present an inference as fact.

## Documentation Structure

```
docs/
├── OVERVIEW.md              # Vision, stack, macro architecture
├── ARCHITECTURE.md          # Components, dependencies, data flows
├── CHANGELOG-FUNCTIONAL.md  # Functional evolution journal
├── COVERAGE.md              # Auto-generated coverage map
├── features/                # One file per functional block
│   ├── auth.md
│   ├── payments.md
│   └── ...
└── decisions/               # Architecture Decision Records
    ├── 001-choice-of-db.md
    └── ...
```

## Modes

### Mode 1: `/doc:init` — Retrodocumentation

**Trigger:** First-time documentation of an existing codebase.

**Process:**

1. **Scan project structure**
   - List all directories, files, entry points
   - Identify stack, frameworks, dependencies from config files (package.json, requirements.txt, Cargo.toml, etc.)
   - Identify test files (source of functional truth)

2. **Build component map**
   - Identify modules, services, routes, models, key abstractions
   - Map dependencies between components
   - Identify external integrations (APIs, databases, queues)

3. **Generate documentation skeleton**
   - Create `docs/` directory structure
   - Generate `OVERVIEW.md` from project config + top-level analysis
   - Generate `ARCHITECTURE.md` with component map and data flows
   - For each identified functional block, create `docs/features/<block>.md`
   - Tag everything appropriately: `[Code]` for verifiable facts, `[Inference]` for deductions

4. **Generate initial COVERAGE.md**
   - Cross-reference code modules vs documented features
   - Flag undocumented areas
   - Flag all `[To confirm]` and `[Inference]` items

5. **Prompt for interview**
   - List top `[To confirm]` items
   - Ask: "Want to run `/doc:interview` to clarify these?"

**Output:** Complete `docs/` directory committed to git.

---

### Mode 2: `/doc:update` — Post-Change Sync

**Trigger:** After any code change with functional impact.

**Process:**

1. **Identify what changed**
   - Analyze recent uncommitted changes or specified commit range
   - Use `git diff` to identify modified files
   - Classify changes: functional (behavior change) vs technical (refactor, perf, style)

2. **If functional change detected:**
   - Identify which `docs/features/*.md` file(s) are impacted
   - Update the relevant sections, preserving existing epistemic tags
   - New content tagged `[Code]` if verifiable, `[Inference]` if deduced
   - Add entry to `CHANGELOG-FUNCTIONAL.md`:
     ```
     ## YYYY-MM-DD — <short description>
     - **What changed:** <functional description>
     - **Why:** <rationale if known, otherwise [To confirm]>
     - **Files impacted:** <list>
     - **Doc updated:** <list of docs/*.md files modified>
     ```

3. **If no functional change:** Skip doc update, optionally note in commit.

4. **Update COVERAGE.md** if new modules/routes appeared.

**Output:** Updated doc files, staged for commit alongside code.

---

### Mode 3: `/doc:interview` — Capture Tacit Knowledge

**Trigger:** Explicitly requested, or suggested after `init` / `challenge`.

**Process:**

1. **Collect open questions**
   - Scan all `docs/` files for `[To confirm]` and `[Inference]` tags
   - Group by feature/topic
   - Prioritize: business rules > architecture decisions > edge cases

2. **Ask ONE question at a time**
   - Present the current documented assertion
   - Ask: "Is this correct? If not, what's the actual behavior/rationale?"
   - Accept freeform answers

3. **Update documentation**
   - Replace `[To confirm]`/`[Inference]` with `[Declared]` once confirmed
   - If corrected, update content + tag as `[Declared]`
   - If still unclear, keep `[To confirm]` and note the discussion

4. **Record decisions**
   - If an answer reveals an architecture/business decision, create a `docs/decisions/NNN-<topic>.md` ADR:
     ```
     # NNN — <Title>
     **Date:** YYYY-MM-DD
     **Status:** Accepted
     **Context:** <why was a decision needed>
     **Decision:** <what was decided>
     **Consequences:** <trade-offs, implications>
     **Source:** [Declared] — <who provided this>
     ```

**Output:** Updated docs with reduced `[To confirm]` count.

---

### Mode 4: `/doc:challenge` — Verify Accuracy

**Trigger:** Periodic review, or after major refactoring.

**Process:**

1. **Cross-reference doc vs code**
   - For each `docs/features/*.md`, verify assertions tagged `[Code]` still hold
   - Check if documented flows match current code paths
   - Identify documented features that no longer exist in code (dead doc)
   - Identify code paths not covered by any doc (undocumented features)

2. **Check inference validity**
   - Re-evaluate `[Inference]` tags against current code
   - Flag any that seem incorrect or outdated

3. **Produce challenge report**
   - List: confirmed OK, inconsistent, dead doc, undocumented code, suspect inferences
   - For each issue, suggest resolution (update doc, update code, confirm with human)

4. **Apply fixes**
   - Auto-fix clear inconsistencies (rename, moved files)
   - Flag ambiguous issues as `[To confirm]`
   - Prompt for `/doc:interview` on remaining items

**Output:** Challenge report + updated docs.

---

### Mode 5: `/doc:coverage` — Measure Completeness

**Trigger:** On demand or as part of `init`/`challenge`.

**Process:**

1. **Inventory code surface**
   - List all: modules, routes/endpoints, models/schemas, services, key functions
   - Group by functional domain

2. **Inventory documented surface**
   - Parse `docs/features/*.md` for documented blocks
   - Extract epistemic tag distribution

3. **Generate COVERAGE.md**
   ```
   # Documentation Coverage

   Last updated: YYYY-MM-DD

   ## Summary
   - Modules documented: X/Y (Z%)
   - Assertions [Code]: N
   - Assertions [Inference]: N
   - Assertions [To confirm]: N
   - Assertions [Declared]: N

   ## Coverage by Module
   | Module | Documented | Status | Confidence |
   |--------|-----------|--------|------------|
   | auth   | ✅ Yes    | Current | 80% [Code], 20% [Inference] |
   | payments | ⚠️ Partial | Outdated | 50% [To confirm] |
   | reports | ❌ No     | —       | — |

   ## Action Items
   - [ ] Document: reports module
   - [ ] Confirm: 12 [To confirm] items in payments
   - [ ] Review: 5 [Inference] items in auth (last challenged: never)
   ```

**Output:** `docs/COVERAGE.md` written/updated.

## Template Files

Use templates from `templates/` subdirectory of this skill when generating initial docs. Adapt to the specific project — templates are starting points, not rigid formats.

## Key Principles

| Principle | Application |
|-----------|-------------|
| **Epistemic honesty** | Every assertion tagged by source and confidence |
| **Zero friction** | Doc update is part of the coding flow, not a separate task |
| **Code is truth** | When doc contradicts code, code wins — update the doc |
| **Incremental** | Don't try to document everything at once — iterate |
| **Generic** | Same structure regardless of stack or language |
| **Machine-readable** | Tags and structure parseable by agents for downstream tasks |

## Integration with Workflow

### Recommended Commit Pattern

```
# After code change:
1. Make code changes
2. Run /doc:update
3. Stage code + doc changes together
4. Commit with message: "feat: <what> — docs updated"
```

### Recommended Periodic Review

```
# Weekly or before major releases:
1. Run /doc:challenge
2. Fix inconsistencies
3. Run /doc:coverage to check completeness
4. Run /doc:interview on remaining [To confirm] items
```
