---
name: map
description: "Generate or refresh a Documentation Index section in the project's root CLAUDE.md or AGENT.md, pointing to all docs/ files with one-line descriptions so coding assistants can find them on demand. Trigger with /doc-sync:map"
---

# map — Generate Documentation Index in CLAUDE.md / AGENT.md

**Announce:** "I'm using the doc-sync plugin to generate the documentation index."

## Purpose

Inject a compact, scannable index into the project's root `CLAUDE.md` (or `AGENT.md`) so coding assistants know where to find documentation without loading it all into context upfront. This is safe to run repeatedly — the section is delimited and replaced, never duplicated.

## Process

### Step 1: Verify docs/ exists

- If `docs/` does not exist at the project root → stop and suggest running `/doc-sync:init` first
- List all files in `docs/`: OVERVIEW.md, ARCHITECTURE.md, CHANGELOG-FUNCTIONAL.md, features/*.md, decisions/*.md

### Step 2: Extract descriptions

For each file found, extract a one-line description:

| File | Source |
|------|--------|
| `docs/OVERVIEW.md` | Fixed: "Project purpose, tech stack, entry points, functional blocks" |
| `docs/ARCHITECTURE.md` | Fixed: "Component map, data flows, external dependencies, data models" |
| `docs/CHANGELOG-FUNCTIONAL.md` | Fixed: "Functional evolution history" |
| `docs/features/<block>.md` | Read the file: extract first sentence of the "Purpose" section, or the H1 title |
| `docs/decisions/<n>-<name>.md` | Read the file: extract the H1 title, or humanize the filename (e.g. `001-postgresql` → "PostgreSQL selection") |

Keep descriptions under 80 characters. Remove epistemic tags from extracted text.

### Step 3: Select target file

1. If `CLAUDE.md` exists at project root → use it
2. Else if `AGENT.md` exists → use it
3. Else → create `AGENT.md`

### Step 4: Inject or replace the map section

**Map format:**

```markdown
<!-- doc-sync:map:start -->
## Documentation Index

> Consult these files on demand — load only what's relevant to your task.

| File | Description |
|------|-------------|
| [docs/OVERVIEW.md](docs/OVERVIEW.md) | Project purpose, tech stack, entry points, functional blocks |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Component map, data flows, external dependencies, data models |
| [docs/features/auth.md](docs/features/auth.md) | <extracted description> |
| [docs/decisions/001-db.md](docs/decisions/001-db.md) | <extracted description> |
| [docs/CHANGELOG-FUNCTIONAL.md](docs/CHANGELOG-FUNCTIONAL.md) | Functional evolution history |
<!-- doc-sync:map:end -->
```

**Injection rules:**
- Delimiters present → replace only the block between `<!-- doc-sync:map:start -->` and `<!-- doc-sync:map:end -->` (idempotent)
- File exists, no delimiters → append the map section at the end with a blank line separator
- File does not exist → create it with only the map section

### Step 5: Confirm

Report: "Documentation map updated in `<filename>` — N files indexed."

## Key Rules

- Never touch content outside the `<!-- doc-sync:map:start/end -->` delimiters
- Descriptions must be one line, under 80 characters, no epistemic tags
- Rows are ordered: OVERVIEW → ARCHITECTURE → features (alphabetical) → decisions (numbered) → CHANGELOG-FUNCTIONAL
- If a `docs/COVERAGE.md` exists, omit it from the map (it's a meta-file, not reference material)
