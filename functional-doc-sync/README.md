# functional-doc-sync — User Guide

## What

A Claude Code skill that maintains functional Markdown documentation in sync with code, inside Git.

## Why

AI-assisted development generates code through ephemeral conversations. Without a dedicated mechanism, documentation drifts from code within days. This skill forces synchronization by integrating doc maintenance into the development flow.

## Prerequisites

- Claude Code with custom skill support
- An initialized Git project
- This skill installed in your Claude Code skills directory

## Installation

Copy the `functional-doc-sync/` folder into your Claude Code skills directory (e.g., `~/.claude/skills/` or your configured path).

## The 5 Commands

| Command | When to use | Typical duration |
|---------|------------|-----------------|
| `/doc:init` | First run on an existing project | 5-20 min depending on size |
| `/doc:update` | After each functional change | 1-3 min |
| `/doc:interview` | To capture tacit knowledge | 5-30 min (interactive) |
| `/doc:challenge` | Periodic review or post-refactoring | 3-10 min |
| `/doc:coverage` | Measure completeness | 1-2 min |

## Daily Workflow

### Typical scenario: iterative development

```
you    → "Add a password reset endpoint"
claude → [codes the endpoint]
you    → "/doc:update"
claude → [updates docs/features/auth.md + CHANGELOG-FUNCTIONAL.md]
you    → "commit"
claude → [commits code + doc together]
```

### First run on an existing project

```
you    → "/doc:init"
claude → [analyzes code, generates entire docs/ structure]
claude → "I have 14 [To confirm] items. Want to run /doc:interview?"
you    → "yes"
claude → [asks questions one at a time about unclear areas]
```

### Weekly review

```
you    → "/doc:challenge"
claude → [report: 2 inconsistencies, 1 dead doc, 3 undocumented features]
you    → "fix what you can"
claude → [fixes obvious issues, flags the rest as [To confirm]]
you    → "/doc:coverage"
claude → [generates coverage map]
```

## Epistemic Tags

Generated documentation uses tags to indicate the reliability of each assertion:

- **`[Code]`** — Directly verifiable in source code. Reliable.
- **`[Inference]`** — Deduced from code by the AI. Likely correct but should be verified.
- **`[To confirm]`** — Unclear area requiring human/business input. Priority for review.
- **`[Declared]`** — Confirmed or provided by a human. Reliable.
- **`[Decision]`** — Documented architecture decision (ADR). Reliable.

### Why this matters

The AI reads code and deduces intentions. Sometimes it's right, sometimes not. Tags make the confidence level visible. Without them, documentation looks authoritative while containing hypotheses.

### Maturation workflow

```
[Inference]  → /doc:interview → [Declared]  (human confirmation)
[Inference]  → /doc:challenge  → [Code]      (verified against current code)
[To confirm] → /doc:interview → [Declared]   (resolved by a human)
```

The goal is to drive documentation toward maximum `[Code]` and `[Declared]`, minimum `[To confirm]`.

## Generated Documentation Structure

```
docs/
├── OVERVIEW.md              # Vision, stack, macro architecture
├── ARCHITECTURE.md          # Components, dependencies, data flows
├── CHANGELOG-FUNCTIONAL.md  # Functional evolution journal
├── COVERAGE.md              # Coverage map (auto-generated)
├── features/                # One file per functional block
│   ├── auth.md
│   ├── payments.md
│   └── ...
└── decisions/               # Architecture Decision Records
    ├── 001-choice-of-db.md
    └── ...
```

### What each file contains

- **OVERVIEW.md** — What the project does, for whom, with what stack. Read first by any new dev or AI agent.
- **ARCHITECTURE.md** — How components fit together. Flow diagrams, inter-module dependencies.
- **features/*.md** — Detail of each functional block: expected behavior, business rules, edge cases.
- **decisions/*.md** — The "why": each significant technical or business choice documented with its context and consequences.
- **CHANGELOG-FUNCTIONAL.md** — Chronological journal of *functional* changes (not a technical git log).
- **COVERAGE.md** — Dashboard: what is documented, at what confidence level, and what is missing.

## Best Practices

### Do

- Run `/doc:update` after each functional change (not pure refactors)
- Run `/doc:challenge` at least once a week on an active project
- Commit doc and code together (same commit)
- Use `/doc:interview` when a business colleague is available — best time to capture tacit knowledge

### Don't

- Don't try to document everything at once — iterate
- Don't remove `[To confirm]` tags without resolving them
- Don't document technical implementation details in features (that's the job of code and comments)
- Don't create one feature file per micro-feature — group by business domain

## FAQ

**Q: What if I make several changes before running `/doc:update`?**
The update mode analyzes the full diff. Multiple changes will be processed together. But the larger the diff, the higher the risk of omissions. Prefer frequent updates.

**Q: Does the skill work with any language?**
Yes. Analysis is based on project structure, config files, and source code. The skill adapts to the detected stack.

**Q: How to handle multi-repo projects?**
Each repo has its own `docs/`. For cross-cutting documentation, create a dedicated `docs-system` repo with links to each repo's docs.

**Q: Is the generated documentation perfect?**
No. That's the central point: epistemic tags make explicit what is reliable and what is not. The documentation is a starting point that improves through iteration.
