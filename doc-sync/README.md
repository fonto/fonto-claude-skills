# doc-sync

A Claude Code plugin that maintains functional documentation in sync with code
evolution, emitting an **OKF (Open Knowledge Format) knowledge bundle**.

## Why

AI-assisted development generates code through ephemeral conversations. Without a dedicated mechanism, documentation drifts from code within days. This plugin forces synchronization by integrating doc maintenance into the development flow.

## OKF conformance

The generated docs are an [Open Knowledge Format v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
*Knowledge Bundle*: a directory tree of markdown files where every non-reserved
file carries YAML frontmatter with a non-empty `type`, plus reserved `index.md`
(progressive-disclosure listings) and `log.md` (dated history) files. This makes the
docs portable, diffable, and readable by both humans and agents without tooling.

doc-sync keeps its signature **epistemic tags** inline in the body (legal OKF prose)
and additionally surfaces a document-level `confidence` key in the frontmatter.

## Installation

### From GitHub (recommended)

```bash
# In Claude Code:
/plugin marketplace add fonto/fonto-claude-skills
/plugin install doc-sync@claude-skills
```

Always uses the latest version from the repo.

### Local development / testing

```bash
claude --plugin-dir /path/to/doc-sync
```

### Manual

Copy the `doc-sync/` folder to `~/.claude/skills/` (personal) or `.claude/skills/` in your project (project-scoped).

## The skills

All skills are namespaced under `doc-sync`. You don't need them all on day one —
follow the flow: **create** a bundle, **keep it in sync**, then **keep it trustworthy**.

### 1. Start here — create your bundle

The right entry point depends on what you already have:

| You have… | Use | What it does |
|-----------|-----|--------------|
| code only, no docs | `/doc-sync:init [path]` | retrodocument the bundle from the code |
| a doc-sync **v1** `docs/` tree | `/doc-sync:migrate [src] [dst]` | one-time structural upgrade to an OKF bundle |
| **scattered existing docs** (README, design notes, old ADRs, wikis) | `/doc-sync:ingest-existing-docs [path…]` | fold the relevant, still-true parts in |

The bundle defaults to `docs/okf/` (override by passing a path to `/doc-sync:init`).
Every other skill auto-discovers it via the `okf_version` marker in its root `index.md`.

```
you    → /doc-sync:init
claude → [analyzes code, generates the whole docs/okf/ bundle]
claude → "I have 14 [To confirm] items. Want to run doc-sync:interview?"
you    → "yes"
```

Already have a bundle plus some old docs lying around? Point the new skill at them —
it verifies each claim against the current code and only asks you when something
conflicts:

```
you    → /doc-sync:ingest-existing-docs LEGACY-DESIGN.md docs/old-wiki/
claude → [reads them, checks each claim vs code, asks only on conflicts,
          merges the rest, archives the sources]
claude → "Ingested 2 docs: 9 elements merged, 1 conflict resolved, sources archived."
```

### 2. Keep it in sync — after each change

`/doc-sync:update` — run after any functional code change (skip pure refactors). It
reads the `git diff`, captures the session/plan/ticket intent behind the change,
updates the affected concepts, and appends to `log.md`.

```
you    → "Add a password reset endpoint"
claude → [codes the endpoint]
you    → /doc-sync:update
claude → "Is there a plan, spec, or ticket notes to fold in? (file path / paste / no)"
you    → no  (or paste ticket text, or give a file path)
claude → [updates docs/okf/features/auth.md + appends to docs/okf/log.md with Why: filled]
you    → "commit"
claude → [commits code + doc together]
```

### 3. Keep it trustworthy — mature & verify

The bundle is only as good as its tags. These three raise confidence over time:

| Command | When | What it does |
|---------|------|--------------|
| `/doc-sync:challenge` | weekly / post-refactor | cross-checks docs vs code; flags drift, dead docs, undocumented code |
| `/doc-sync:interview` | a colleague is available | asks about `[Inference]` / `[To confirm]` items → `[Declared]` |
| `/doc-sync:coverage` | anytime | measures completeness + tag distribution |

```
you    → /doc-sync:challenge
claude → [report: 2 inconsistencies, 1 dead doc, 3 undocumented features]
you    → "fix what you can"
claude → [fixes obvious issues, flags the rest as [To confirm]]
```

This is the maturation loop — `[Inference] → interview/challenge → [Declared]/[Code]`
(see [Epistemic Tags](#epistemic-tags)).

### 4. Plumbing

`/doc-sync:map` (< 1 min) — refresh the bundle `index.md` files and the CLAUDE.md /
AGENT.md pointer. The other skills run this for you when concepts are added or removed;
invoke it manually only if the indexes ever look stale.

## Epistemic Tags

Generated documentation uses tags to indicate the reliability of each assertion:

| Tag | Meaning | Reliability |
|-----|---------|-------------|
| `[Code]` | Directly verifiable in source code | High |
| `[Inference]` | Deduced from code by the AI | Medium — verify |
| `[To confirm]` | Unclear, needs human/business input | Low — priority for review |
| `[Declared]` | Confirmed or provided by a human | High |
| `[Decision]` | Documented architecture decision (ADR) | High |

### Why this matters

The AI reads code and deduces intentions. Sometimes it's right, sometimes not. Tags make the confidence level visible. Without them, documentation looks authoritative while containing hypotheses.

### Maturation workflow

```
[Inference]  → doc-sync:interview → [Declared]   (human confirmation)
[Inference]  → doc-sync:challenge  → [Code]       (verified against current code)
[To confirm] → doc-sync:interview → [Declared]    (resolved by a human)
```

Goal: maximize `[Code]` and `[Declared]`, minimize `[To confirm]`.

The inline tags are summarized at the document level by the frontmatter `confidence`
key (`code` | `inference` | `to-confirm` | `declared` | `mixed`).

## Generated Documentation Structure (OKF bundle)

Default location `docs/okf/` (override with `/doc-sync:init <path>`):

```
docs/okf/                    # the OKF Knowledge Bundle
├── index.md                 # RESERVED — bundle entry, frontmatter = okf_version only
├── log.md                   # RESERVED — functional history (dated, newest first)
├── OVERVIEW.md              # type: Overview      — vision, stack, macro architecture
├── ARCHITECTURE.md          # type: Architecture  — components, dependencies, data flows
├── COVERAGE.md              # type: Coverage Report (auto-generated)
├── features/                # type: Feature — one concept per functional block
│   ├── index.md             # RESERVED — listing (no frontmatter)
│   └── auth.md
├── decisions/               # type: Decision — Architecture Decision Records
│   ├── index.md
│   └── 001-choice-of-db.md
└── data/                    # type: "<DB> Table" — data catalog, one concept per table
    ├── index.md
    └── users.md
```

Every concept carries frontmatter (`type` required). FKs and cross-references are
markdown links between concepts; external sources go under a `# Citations` heading.

### Migrating from v1.x

v1 wrote a tag-only `docs/` tree with no frontmatter and a `CHANGELOG-FUNCTIONAL.md`.
Run **`/doc-sync:migrate`** once — it transforms the tree in place (it does *not*
regenerate from code, so human `[Declared]` content is preserved): moves `docs/` →
`docs/okf/`, adds `type`/`confidence` frontmatter, converts the changelog to
`log.md`, lifts decisions, extracts the new `data/` catalog, and generates the
`index.md` files. It finishes by running the OKF validator.

```
you    → /doc-sync:migrate
claude → [moves tree, adds frontmatter, builds data/ + index.md, validates]
claude → "Migrated 9 concepts, extracted 3 tables, 0 OKF errors."
```

## Best Practices

**Do:**
- Run `doc-sync:update` after each functional change (not pure refactors)
- Run `doc-sync:challenge` at least once a week on an active project
- Commit doc and code together (same commit)
- Use `doc-sync:interview` when a business colleague is available

**Don't:**
- Try to document everything at once — iterate
- Remove `[To confirm]` tags without resolving them
- Document technical implementation in feature docs (that's code's job)
- Create one feature file per micro-feature — group by business domain

## Plugin Structure

```
doc-sync/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── init/SKILL.md
│   ├── migrate/SKILL.md
│   ├── ingest-existing-docs/SKILL.md
│   ├── update/SKILL.md
│   ├── interview/SKILL.md
│   ├── challenge/SKILL.md
│   ├── coverage/SKILL.md
│   └── map/SKILL.md
├── templates/
│   ├── OVERVIEW.md
│   ├── ARCHITECTURE.md
│   ├── FEATURE.md
│   ├── DECISION.md
│   ├── TABLE.md
│   ├── index.md
│   └── log.md
├── scripts/
│   ├── make_fixture.sh         # scaffold a throwaway test repo (for init)
│   ├── make_v1_fixture.sh      # scaffold a v1 docs/ tree (for migrate)
│   ├── make_ingest_fixture.sh  # scaffold a repo + stray doc (for ingest-existing-docs)
│   └── validate_okf.py         # check a generated bundle for OKF conformance
├── LICENSE
└── README.md
```

## Development & testing

The skills are prompts, so the real test is running them and inspecting the output.

To test `/doc-sync:migrate`, use `scripts/make_v1_fixture.sh` instead — it scaffolds
a v1-style `docs/` tree (no frontmatter, `CHANGELOG-FUNCTIONAL.md`, inline tags). To
test `/doc-sync:ingest-existing-docs`, use `scripts/make_ingest_fixture.sh` — it adds
a stray `LEGACY-DESIGN.md` mixing a true fact, a stale one, and a rationale; run
`/doc-sync:init` first, then ingest it.

```bash
# 1. scaffold a throwaway repo (migrations + 2 features)
doc-sync/scripts/make_fixture.sh /tmp/okf-test

# 2. run the skills against it in a fresh session (loads the local plugin)
cd /tmp/okf-test && claude --plugin-dir /path/to/doc-sync
#    then: /doc-sync:init  →  /doc-sync:update  →  /doc-sync:challenge  →  /doc-sync:coverage

# 3. mechanically validate the generated bundle (no LLM)
python3 /path/to/doc-sync/scripts/validate_okf.py /tmp/okf-test/docs/okf
#    errors → non-conformant; warnings → broken links / non-ISO log dates
```

## License

CC BY-SA 4.0 — See [LICENSE](LICENSE) for details.
