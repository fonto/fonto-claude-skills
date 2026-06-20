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

## The 7 Skills

All skills are namespaced under `doc-sync`:

| Command | When to use | Duration |
|---------|------------|----------|
| `/doc-sync:init [path]` | First run on an existing project (bundle defaults to `docs/okf/`) | 5-20 min |
| `/doc-sync:migrate [src] [dst]` | One-time upgrade of a v1 `docs/` tree to a v2 OKF bundle | 3-10 min |
| `/doc-sync:update` | After each functional change | 1-3 min |
| `/doc-sync:interview` | To capture tacit knowledge | 5-30 min (interactive) |
| `/doc-sync:challenge` | Periodic review or post-refactoring | 3-10 min |
| `/doc-sync:coverage` | Measure completeness | 1-2 min |
| `/doc-sync:map` | Refresh bundle indexes + CLAUDE.md pointer | < 1 min |

The bundle location defaults to `docs/okf/` and is overridable by passing a path to
`/doc-sync:init`. Other skills auto-discover the bundle via the `okf_version` marker
in its root `index.md`.

## Quick Start

### Retrodocument an existing project

```
you    → /doc-sync:init
claude → [analyzes code, generates entire docs/ structure]
claude → "I have 14 [To confirm] items. Want to run doc-sync:interview?"
you    → "yes"
claude → [asks questions one at a time about unclear areas]
```

### Daily workflow: after a change

```
you    → "Add a password reset endpoint"
claude → [codes the endpoint]
you    → /doc-sync:update
claude → [updates docs/okf/features/auth.md + appends to docs/okf/log.md]
you    → "commit"
claude → [commits code + doc together]
```

### Weekly review

```
you    → /doc-sync:challenge
claude → [report: 2 inconsistencies, 1 dead doc, 3 undocumented features]
you    → "fix what you can"
claude → [fixes obvious issues, flags the rest as [To confirm]]
you    → /doc-sync:coverage
claude → [generates coverage map]
```

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
│   ├── make_fixture.sh      # scaffold a throwaway test repo (for init)
│   ├── make_v1_fixture.sh   # scaffold a v1 docs/ tree (for migrate)
│   └── validate_okf.py      # check a generated bundle for OKF conformance
├── LICENSE
└── README.md
```

## Development & testing

The skills are prompts, so the real test is running them and inspecting the output.

To test `/doc-sync:migrate`, use `scripts/make_v1_fixture.sh` instead — it scaffolds
a v1-style `docs/` tree (no frontmatter, `CHANGELOG-FUNCTIONAL.md`, inline tags).

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
