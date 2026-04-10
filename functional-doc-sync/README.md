# functional-doc-sync

A Claude Code plugin that maintains functional documentation in sync with code evolution.

## Why

AI-assisted development generates code through ephemeral conversations. Without a dedicated mechanism, documentation drifts from code within days. This plugin forces synchronization by integrating doc maintenance into the development flow.

## Installation

### From GitHub (recommended)

```bash
# In Claude Code:
/plugin marketplace add <your-github-user>/claude-skills
/plugin install functional-doc-sync@claude-skills
```

Always uses the latest version from the repo.

### Local development / testing

```bash
claude --plugin-dir /path/to/functional-doc-sync
```

### Manual

Copy the `functional-doc-sync/` folder to `~/.claude/skills/` (personal) or `.claude/skills/` in your project (project-scoped).

## The 5 Skills

All skills are namespaced under `functional-doc-sync`:

| Command | When to use | Duration |
|---------|------------|----------|
| `/functional-doc-sync:doc-init` | First run on an existing project | 5-20 min |
| `/functional-doc-sync:doc-update` | After each functional change | 1-3 min |
| `/functional-doc-sync:doc-interview` | To capture tacit knowledge | 5-30 min (interactive) |
| `/functional-doc-sync:doc-challenge` | Periodic review or post-refactoring | 3-10 min |
| `/functional-doc-sync:doc-coverage` | Measure completeness | 1-2 min |

## Quick Start

### Retrodocument an existing project

```
you    → /functional-doc-sync:doc-init
claude → [analyzes code, generates entire docs/ structure]
claude → "I have 14 [To confirm] items. Want to run doc-interview?"
you    → "yes"
claude → [asks questions one at a time about unclear areas]
```

### Daily workflow: after a change

```
you    → "Add a password reset endpoint"
claude → [codes the endpoint]
you    → /functional-doc-sync:doc-update
claude → [updates docs/features/auth.md + CHANGELOG-FUNCTIONAL.md]
you    → "commit"
claude → [commits code + doc together]
```

### Weekly review

```
you    → /functional-doc-sync:doc-challenge
claude → [report: 2 inconsistencies, 1 dead doc, 3 undocumented features]
you    → "fix what you can"
claude → [fixes obvious issues, flags the rest as [To confirm]]
you    → /functional-doc-sync:doc-coverage
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
[Inference]  → doc-interview → [Declared]   (human confirmation)
[Inference]  → doc-challenge  → [Code]       (verified against current code)
[To confirm] → doc-interview → [Declared]    (resolved by a human)
```

Goal: maximize `[Code]` and `[Declared]`, minimize `[To confirm]`.

## Generated Documentation Structure

```
docs/
├── OVERVIEW.md              # Vision, stack, macro architecture
├── ARCHITECTURE.md          # Components, dependencies, data flows
├── CHANGELOG-FUNCTIONAL.md  # Functional evolution journal
├── COVERAGE.md              # Coverage map (auto-generated)
├── features/                # One file per functional block
│   ├── auth.md
│   └── ...
└── decisions/               # Architecture Decision Records
    ├── 001-choice-of-db.md
    └── ...
```

## Best Practices

**Do:**
- Run `doc-update` after each functional change (not pure refactors)
- Run `doc-challenge` at least once a week on an active project
- Commit doc and code together (same commit)
- Use `doc-interview` when a business colleague is available

**Don't:**
- Try to document everything at once — iterate
- Remove `[To confirm]` tags without resolving them
- Document technical implementation in feature docs (that's code's job)
- Create one feature file per micro-feature — group by business domain

## Plugin Structure

```
functional-doc-sync/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── skills/
│   ├── doc-init/SKILL.md
│   ├── doc-update/SKILL.md
│   ├── doc-interview/SKILL.md
│   ├── doc-challenge/SKILL.md
│   └── doc-coverage/SKILL.md
├── templates/
│   ├── OVERVIEW.md
│   ├── ARCHITECTURE.md
│   ├── FEATURE.md
│   ├── DECISION.md
│   └── CHANGELOG-FUNCTIONAL.md
├── LICENSE                   # CC BY-SA 4.0
└── README.md                 # This file
```

## License

CC BY-SA 4.0 — See [LICENSE](LICENSE) for details.
