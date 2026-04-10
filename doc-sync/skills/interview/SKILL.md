---
name: interview
description: "Use to capture tacit knowledge from developers or business stakeholders. Scans docs for [To confirm] and [Inference] items, asks targeted questions one at a time, and upgrades tags to [Declared] upon confirmation. Trigger with /doc-sync:interview"
---

# interview — Capture Tacit Knowledge

**Announce:** "I'm using the doc-sync plugin to interview you about documentation gaps."

## Epistemic Tags

| Tag | Meaning |
|-----|---------|
| `[Code]` | Directly verifiable in source code |
| `[Inference]` | Deduced from code patterns, naming, structure |
| `[To confirm]` | Requires human/business validation |
| `[Declared]` | Explicitly stated by a human |
| `[Decision]` | Architecture or business decision with rationale |

## Process

### Step 1: Collect Open Questions

- Scan all `docs/` files for `[To confirm]` and `[Inference]` tags
- Group by feature/topic
- Prioritize:
  1. Business rules tagged `[To confirm]` — highest risk of being wrong
  2. Architecture decisions tagged `[Inference]` — important for future work
  3. Edge cases tagged `[Inference]` — lower priority but useful

### Step 2: Present Summary

- Show the total count: "I found N items to clarify: X [To confirm], Y [Inference]"
- Show the priority grouping
- Ask: "Ready to go through them? I'll ask one at a time."

### Step 3: Ask ONE Question at a Time

For each item:
- Quote the current documented assertion with its tag
- State which file and section it's from
- Ask: "Is this correct? If not, what's the actual behavior/rationale?"
- Accept freeform answers

**Example:**
```
In docs/features/auth.md, section "Password Reset":

> [Inference] The reset token expires after 24 hours.

Is this correct? If not, what's the actual expiration time and why?
```

### Step 4: Update Documentation

For each answer:
- **Confirmed as-is:** Replace tag with `[Declared]`
- **Corrected:** Update content + tag as `[Declared]`
- **Still unclear:** Keep `[To confirm]`, add a note: `<!-- Discussed YYYY-MM-DD, still unresolved -->`
- **Reveals a decision:** Create an ADR in `docs/decisions/NNN-<topic>.md`

**ADR template:**
```markdown
# NNN — <Title>
**Date:** YYYY-MM-DD
**Status:** Accepted
**Context:** <why was a decision needed>
**Decision:** <what was decided>
**Consequences:** <trade-offs, implications>
**Source:** [Declared] — <who provided this>
```

### Step 5: Report Progress

After the session:
- Show how many items were resolved
- Show remaining `[To confirm]` count
- Commit updated docs with message: `docs: interview session — N items resolved`

## Key Rules

- **One question at a time** — never batch questions
- **Quote the existing assertion** — so the interviewee knows what they're confirming or correcting
- **Accept "I don't know"** — keep the tag as `[To confirm]`, don't pressure
- **Don't lead the witness** — present the assertion neutrally, don't suggest the answer
- **Record the source** — note who provided the information when creating `[Declared]` tags
- **Create ADRs proactively** — any answer that reveals a deliberate choice deserves a decision record
