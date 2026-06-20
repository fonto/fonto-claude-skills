---
name: init
description: "Use when retrodocumenting an existing codebase for the first time. Analyzes the full project structure and generates a complete OKF (Open Knowledge Format) bundle with OVERVIEW, ARCHITECTURE, per-feature concepts, a per-table data catalog, and index/log files. Trigger with /doc-sync:init [path]"
---

# init — Retrodocument an Existing Codebase as an OKF Bundle

**Announce:** "I'm using the doc-sync plugin to retrodocument this project as an OKF bundle."

The output is a **Knowledge Bundle** conforming to Open Knowledge Format v0.1
(https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md):
a directory tree of markdown files where every non-reserved file carries YAML
frontmatter with a non-empty `type`, and reserved files (`index.md`, `log.md`)
follow a fixed structure.

## Bundle Location

- **Default:** `docs/okf/`.
- **Override:** the first argument to the skill, e.g. `/doc-sync:init docs/knowledge`
  or `/doc-sync:init .` — if absent, use `docs/okf/`.
- Throughout this skill, `<bundle>/` means that root.

## Frontmatter (every concept)

Only `type` is required by OKF. doc-sync also writes these producer keys:

```yaml
---
type: <Type>                  # REQUIRED — Overview | Architecture | Feature | Decision | "<DB> Table" | Coverage Report | Reference
title: <display name>
description: <one-line summary>
tags: [<tag>, ...]
timestamp: <ISO 8601 datetime>
confidence: <code | inference | to-confirm | declared | mixed>
---
```

`confidence` is the document-level summary of the inline epistemic tags below
(use the lowest/dominant level present; `mixed` when several coexist).

Reserved files have NO frontmatter, except the **bundle-root** `index.md`, which
carries ONLY `okf_version: "0.1"`.

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
<bundle>/                    # default docs/okf/
├── index.md                 # RESERVED — bundle root: frontmatter = ONLY okf_version: "0.1"
├── log.md                   # RESERVED — functional history, date-grouped, newest first
├── OVERVIEW.md              # concept · type: Overview
├── ARCHITECTURE.md          # concept · type: Architecture
├── COVERAGE.md              # concept · type: Coverage Report
├── features/
│   ├── index.md            # RESERVED — no frontmatter
│   └── <block>.md          # concept · type: Feature
├── decisions/
│   ├── index.md            # RESERVED — no frontmatter
│   └── <NNN>-<title>.md    # concept · type: Decision (if detectable)
└── data/
    ├── index.md            # RESERVED — no frontmatter
    └── <table>.md          # concept · type: "<DB> Table" (one per table/model)
```

Links between concepts are markdown links. Prefer relative paths within a
directory; use bundle-relative paths (leading `/`) for cross-directory links
(e.g. a FK in `data/orders.md` → `[users](/data/users.md)`).

## Process

### Step 1: Scan Project Structure

- List all directories, files, entry points
- Read config files: package.json, requirements.txt, Cargo.toml, go.mod, Gemfile, etc.
- Identify stack, frameworks, key dependencies
- Locate test files — they are a source of functional truth
- Locate existing documentation (README, comments, inline docs)
- **Read manifest/config files before describing the stack** (package.json,
  pyproject.toml/requirements.txt, go.mod, Cargo.toml, Gemfile, composer.json,
  etc.). Never state that a file, dependency, or config is *absent* without having
  listed the directory and confirmed it — tag `[Code]` only for what you read.

### Step 2: Build Component Map

- Identify modules, services, routes, models, key abstractions
- Map dependencies between components
- Identify external integrations (APIs, databases, queues, third-party services)
- Group into functional blocks (by business domain, not by file type)
- **Locate the data layer** — this becomes the `data/` catalog. Look for:
  - SQL migrations / DDL (`migrations/`, `*.sql`, schema dumps)
  - ORM models (Prisma `schema.prisma`, SQLAlchemy, Django models, TypeORM,
    Sequelize, ActiveRecord, Ent, GORM, etc.)
  - Detect the datastore flavor (Postgres, MySQL, SQLite, BigQuery, Mongo…) to
    pick the concept `type` and the `resource:` URI scheme.
  - For each table/collection, **read the DDL/model literally** and capture:
    - columns and types
    - **nullability** — `no` (not null) if the source declares `NOT NULL` or the
      column is a primary key; `yes` only when there is no NOT NULL and it is not a
      PK. Do not guess: if the source is ambiguous, tag that row `[To confirm]`
      rather than asserting `[Code]`.
    - **constraints** — primary key, foreign keys, `UNIQUE`, `DEFAULT`, `CHECK`
    - FKs become links to other table concepts.

### Step 3: Generate the Bundle

For each file, use the templates in the `templates/` directory of this plugin as
starting points. Adapt to the specific project. **Every concept gets frontmatter
(`type` required); reserved files do not** (except root `index.md` → `okf_version`).

**OVERVIEW.md** (`type: Overview`):
- Project purpose (from README, package description, or `[To confirm]`)
- Stack (from config files — tag `[Code]`)
- Architecture summary (tag `[Inference]`)
- Table of functional blocks with links to feature concepts

**ARCHITECTURE.md** (`type: Architecture`):
- Component table with responsibilities and file locations (`[Code]`)
- Data flow descriptions (`[Inference]`)
- External dependencies (`[Code]`)
- Data models: high-level summary only + link to `data/index.md` (details live
  in per-table concepts, not here)
- Configuration / env vars (`[Code]`)

**features/<block>.md** (`type: Feature`, one per functional block):
- Purpose (`[Inference]` or `[To confirm]`)
- Behavior — describe what the feature does, triggers, outcomes, error cases
- Business rules (`[To confirm]` unless obvious from code)
- Edge cases (`[Inference]`)
- Dependencies on other blocks
- `# Citations` only if claims come from external sources

**data/<table>.md** (`type: "<DB> Table"`, one per table/collection from Step 2):
- `resource:` canonical URI (e.g. `postgres://<db>/public/users`)
- `# Schema` table: column, type, null, key, **constraints**, description — fill
  nullability and constraints exactly as read in Step 2 (`[Code]`; ambiguous rows
  → `[To confirm]`)
- FKs as links to other table concepts (e.g. `FK → [users](/data/users.md)`)
- `# Examples` with a typical query (`[Inference]`)
- Use `templates/TABLE.md`

**log.md** (RESERVED, no frontmatter):
- Initialize with one dated entry, e.g.
  `## <YYYY-MM-DD>` / `* **Creation**: Initial documentation generated from codebase analysis.`

**index.md files** (RESERVED):
- Bundle root `<bundle>/index.md`: frontmatter `okf_version: "0.1"` only, then
  sections (Overview / Features / Data / Decisions / History) listing concepts as
  bullets `[link](path.md) — one-line description` (progressive disclosure).
- `features/index.md`, `decisions/index.md`, `data/index.md`: no frontmatter, one
  bullet per concept in that directory. Use `templates/index.md`.

### Step 4: Generate COVERAGE.md

`COVERAGE.md` is a concept too — give it frontmatter `type: Coverage Report`.
Cross-reference:
- Code modules/routes/components identified in Step 2
- Feature concepts and data-catalog (table) concepts generated in Step 3
- Tag distribution per concept

Output a coverage table and action items list.

### Step 5: Generate Documentation Map

Inject a compact index into the project's root `CLAUDE.md` or `AGENT.md` so coding
assistants know the bundle exists and where to enter it. This is separate from the
OKF `index.md` files (which live inside the bundle); the CLAUDE.md map points at
the bundle root and names its path so other doc-sync skills can discover it.

**Target file selection:**
1. If `CLAUDE.md` exists at project root → inject there
2. Else if `AGENT.md` exists → inject there
3. Else → create `AGENT.md` with just the map section

**Description per file type** (paths are relative to project root, using `<bundle>/`):

| File | Description to use |
|------|--------------------|
| `index.md` | "OKF bundle entry — start here (progressive disclosure)" |
| `OVERVIEW.md` | "Project purpose, tech stack, entry points, functional blocks" |
| `ARCHITECTURE.md` | "Component map, data flows, external dependencies" |
| `data/index.md` | "Data catalog — one concept per table" |
| `log.md` | "Functional change history" |
| `features/<block>.md` | Extract first sentence of the "Purpose" section, or the H1 title |
| `decisions/<n>-<name>.md` | Extract the H1 title, or humanize the filename if no H1 |

**Map format** (use exactly these delimiters for idempotent updates; `<bundle>` is
the actual path, e.g. `docs/okf`):

```markdown
<!-- doc-sync:map:start -->
## Documentation Index

> OKF knowledge bundle at `<bundle>/`. Consult on demand — load only what's relevant.

| File | Description |
|------|-------------|
| [<bundle>/index.md](<bundle>/index.md) | OKF bundle entry — start here (progressive disclosure) |
| [<bundle>/OVERVIEW.md](<bundle>/OVERVIEW.md) | Project purpose, tech stack, entry points, functional blocks |
| [<bundle>/ARCHITECTURE.md](<bundle>/ARCHITECTURE.md) | Component map, data flows, external dependencies |
| [<bundle>/data/index.md](<bundle>/data/index.md) | Data catalog — one concept per table |
| [<bundle>/features/auth.md](<bundle>/features/auth.md) | <extracted description> |
| [<bundle>/decisions/001-db.md](<bundle>/decisions/001-db.md) | <extracted description> |
| [<bundle>/log.md](<bundle>/log.md) | Functional change history |
<!-- doc-sync:map:end -->
```

**Injection rules:**
- If the target file already contains the delimiters → replace only the block between them (idempotent)
- If the target file exists without delimiters → append the map section at the end
- If the target file does not exist → create it with only the map section

### Step 6: Prompt for Interview

- Count `[To confirm]` and `[Inference]` items
- List the top priority items
- Ask: "I found N items that need human confirmation. Want to run `/doc-sync:interview` to clarify them?"

## Output

- Complete `<bundle>/` OKF bundle (default `docs/okf/`)
- All files committed to git with message: `docs: initial OKF retrodocumentation via doc-sync:init`

## Key Rules

- Group features by **business domain**, not by technical layer
- Don't document implementation details — document **behavior and intent**
- Prefer short, dense descriptions over verbose prose
- Every concept carries frontmatter with a non-empty `type`; reserved files
  (`index.md`, `log.md`) carry none (root `index.md` → `okf_version` only)
- Every section must have at least one epistemic tag; `confidence` in frontmatter
  summarizes them
- One table/collection = one concept in `data/`; FKs become links
- **Accuracy over completeness:** tag `[Code]` ONLY for facts read directly from
  source (a `NOT NULL`, a `UNIQUE`, a present file). If you did not verify it, use
  `[Inference]` or `[To confirm]` — never assert an unverified detail as `[Code]`
- If tests exist, extract functional assertions from them and tag as `[Code]`
