---
type: Feature
title: {Feature/Block Name}
description: {One-line summary of this functional block}
tags: [{tag}]
generated: { by: doc-sync/2.4.0, at: {YYYY-MM-DDThh:mm:ssZ} }
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
# --- verification (optional, doc-sync 2.4) — never use an `id:` key below:
# the source parser would read it as a sources[].id. Omit all three keys when
# the bundle has no VERIFICATION.md or the feature has no user-facing route.
# surfaces: where a user reaches this feature; `app` is an app name declared in
# VERIFICATION.md, `route` is app-relative as routes_inventory.py prints it
# (`[param]` syntax, no basePath), `/x/*` covers every route under /x.
surfaces:
  - { app: {app}, route: {/path/[param]} }
roles: [{role}]                 # vocabulary declared in VERIFICATION.md
tests: [{repo path of an e2e spec}]
# Live proofs are `verified` entries written ONLY by a replay on `main`:
#   - { by: process:{harness-cli}, at: {ISO 8601 UTC}, sha: {commit} }
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

## Verification

> How an agent drives this feature as a user and proves it works. Harness and
> baseline: [VERIFICATION.md](/VERIFICATION.md). Steps name stable handles only
> (ARIA role + name, `name=` attributes, data-testid, routes); never secrets.
> Keep this section last and under ~40 lines; cite test-case ids, don't copy plans.

### Sub-features
- `{feature-sub}` {one line} — TCs: {TC-…}

### How to get to it (user POV)
- {app} `{route}` → {visible control}   <!-- every entry point, not one convenient path -->

### Driving it
Preconditions: {seed state, role/account, flags}
- **{Action}.** `{selector / command}` → {observable result} [Code|Inference]

### Proof (observable end state)
- {state seen from a second, read-only view} + {side effect: row/email/message}

### Gotchas
- {trap that wastes or invalidates a run; a missing precondition goes here, never a weakened journey}

[^{slug}]: {Source title} — {resource}
