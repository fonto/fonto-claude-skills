---
type: Feature
title: {Feature/Block Name}
description: {One-line summary of this functional block}
tags: [{tag}]
generated: { by: doc-sync/2.3.1, at: {YYYY-MM-DDThh:mm:ssZ} }
# sources: write an entry only for a claim traceable to an addressable artifact
# (a repo path or a URL) — `resource` is required on every entry. Omit this key
# entirely when no claim below has an addressable source. A body claim
# attributes to an entry with a `[^<id>]` footnote, `<id>` matching sources[].id.
# Never invent a resource for session/ticket context alone.
sources:
  - id: {slug}
    resource: {repo path or URL}
    title: {source title}
    last_modified: {YYYY-MM-DD}
confidence: {code | inference | to-confirm | declared | mixed}
---

# {Feature/Block Name}

> Last updated: {date}

## Purpose

[To confirm] {What this functional block does and why it exists.}

## Behavior

### {Sub-feature or flow 1}

[Code] {Describe the expected behavior.}

**Trigger:** {What initiates this flow}
**Expected outcome:** {What should happen}
**Error cases:** {What happens when things go wrong}

### {Sub-feature or flow 2}

[Inference] {Describe the expected behavior.}

## Business Rules

[To confirm] {List the business rules that govern this feature.}

1. {Rule 1}
2. {Rule 2} [^{slug}]

## Edge Cases

[Inference] {Known edge cases and how they're handled.}

- {Edge case 1}: {handling}
- {Edge case 2}: {handling}

## Dependencies

[Code] {Other features or services this block depends on.}

- {Dependency and why}

## Open Questions

- [ ] {Anything marked [To confirm] that needs resolution}

[^{slug}]: {Source title} — {resource}
