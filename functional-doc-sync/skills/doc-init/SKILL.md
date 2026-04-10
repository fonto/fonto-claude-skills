---
name: doc-init
description: "Use when retrodocumenting an existing codebase for the first time. Analyzes the full project structure, generates a complete docs/ directory with OVERVIEW, ARCHITECTURE, per-feature docs, and a coverage map. Trigger with /functional-doc-sync:doc-init"
---

# doc-init — Retrodocument an Existing Codebase

**Announce:** "I'm using the functional-doc-sync plugin to retrodocument this project."

## Epistemic Tags

Every substantive statement MUST be prefixed with one of:

| Tag | Meaning |
|-----|---------|
| `[Code]` | Directly verifiable in source code |
| `[Inference]` | Deduced from code patterns, naming, structure |
| `[To confirm]` | Requires human/business validation |
| `[Declared]` | Explicitly stated by a human |
| `[Decision]` | Architecture or business decision with rationale |

**Rule:** When in doubt, use `[To confirm]`. Never present an inference as fact.

## Target Structure

```
docs/
├── OVERVIEW.md
├── ARCHITECTURE.md
├── CHANGELOG-FUNCTIONAL.md
├── COVERAGE.md
├── features/
│   └── <one file per functional block>.md
└── decisions/
    └── <ADRs if detectable>.md
```

## Process

### Step 1: Scan Project Structure

- List all directories, files, entry points
- Read config files: package.json, requirements.txt, Cargo.toml, go.mod, Gemfile, etc.
- Identify stack, frameworks, key dependencies
- Locate test files — they are a source of functional truth
- Locate existing documentation (README, comments, inline docs)

### Step 2: Build Component Map

- Identify modules, services, routes, models, key abstractions
- Map dependencies between components
- Identify external integrations (APIs, databases, queues, third-party services)
- Group into functional blocks (by business domain, not by file type)

### Step 3: Generate Documentation

For each file, use the templates in the `templates/` directory of this plugin as starting points. Adapt to the specific project.

**OVERVIEW.md:**
- Project purpose (from README, package description, or `[To confirm]`)
- Stack (from config files — tag `[Code]`)
- Architecture summary (tag `[Inference]`)
- Table of functional blocks with links to feature docs

**ARCHITECTURE.md:**
- Component table with responsibilities and file locations (`[Code]`)
- Data flow descriptions (`[Inference]`)
- External dependencies (`[Code]`)
- Data models / schemas (`[Code]`)
- Configuration / env vars (`[Code]`)

**features/<block>.md** (one per functional block):
- Purpose (`[Inference]` or `[To confirm]`)
- Behavior — describe what the feature does, triggers, outcomes, error cases
- Business rules (`[To confirm]` unless obvious from code)
- Edge cases (`[Inference]`)
- Dependencies on other blocks

**CHANGELOG-FUNCTIONAL.md:**
- Initialize with a single entry: "Initial documentation generated from codebase analysis"

### Step 4: Generate COVERAGE.md

Cross-reference:
- Code modules/routes/components identified in Step 2
- Feature docs generated in Step 3
- Tag distribution per feature

Output a coverage table and action items list.

### Step 5: Prompt for Interview

- Count `[To confirm]` and `[Inference]` items
- List the top priority items
- Ask: "I found N items that need human confirmation. Want to run `/functional-doc-sync:doc-interview` to clarify them?"

## Output

- Complete `docs/` directory
- All files committed to git with message: `docs: initial retrodocumentation via doc-init`

## Key Rules

- Group features by **business domain**, not by technical layer
- Don't document implementation details — document **behavior and intent**
- Prefer short, dense descriptions over verbose prose
- Every section must have at least one epistemic tag
- If tests exist, extract functional assertions from them and tag as `[Code]`
