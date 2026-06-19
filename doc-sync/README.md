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

## The 6 Skills

All skills are namespaced under `doc-sync`:

| Command | When to use | Duration |
|---------|------------|----------|
| `/doc-sync:init [path]` | First run on an existing project (bundle defaults to `docs/okf/`) | 5-20 min |
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
To upgrade: move the tree to `docs/okf/` (or re-run `/doc-sync:init`), then run
`/doc-sync:challenge` — it adds missing `type` frontmatter, and `/doc-sync:update`
switches the changelog to `log.md`.

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
├── LICENSE
└── README.md
```

## License

CC BY-SA 4.0 — See [LICENSE](LICENSE) for details.
