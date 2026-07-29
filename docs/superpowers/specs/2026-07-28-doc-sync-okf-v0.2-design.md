# doc-sync: OKF v0.2 conformance and trust signals

Date: 2026-07-28
Status: Implemented in doc-sync 2.3.0
Affected: all 8 `doc-sync/skills/*/SKILL.md`, 6 of the 7 `doc-sync/templates/*.md`
(`log.md` unchanged),
`doc-sync/scripts/validate_okf.py`, README, plugin/marketplace manifests

## Problem

doc-sync emits an [OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
knowledge bundle targeting **v0.1**. OKF **v0.2** renames two things doc-sync
writes today and adds a vocabulary of trust signals:

| v0.2 change | doc-sync today |
|---|---|
| `timestamp` → `generated: { by, at }` | writes `timestamp` in 5 templates, 6 skills |
| body `# Citations` → `sources` frontmatter + `[^id]` footnotes | writes `# Citations` in 2 templates, 4 skills |
| `verified: [{ by, at }]` → unverified / machine-confirmed / human-reviewed | no equivalent |
| `status: draft \| stable \| deprecated` | `DECISION.md` uses ADR values in the same key |
| `stale_after: <YYYY-MM-DD>` | no equivalent |
| `type: Attested Computation` | n/a |
| `okf_version: "0.2"` | declares `"0.1"` |

Beyond conformance there is a substantive gain. doc-sync already runs a
maturation loop — `[Inference]` → `interview`/`challenge` → `[Declared]`/`[Code]`
— that is a verification loop in everything but name. v0.2's `verified` field
expresses exactly that loop in a portable, machine-readable way. Today the
outcome of an interview is only legible to a reader of the prose.

## Goal

Make the generated bundle conformant with OKF v0.2, and express doc-sync's
existing maturation loop through v0.2's native trust signals — without
discarding the epistemic tags, which carry information v0.2 does not.

## Decisions

1. **Scope** — the two renames plus `generated` / `verified` / `sources` /
   `status` / `stale_after` and `okf_version: "0.2"`. **Not** `Attested
   Computation`: it presupposes an execution runtime (`executor`, `receipt`,
   `attester`) that doc-sync does not have and that functional documentation
   does not need.
2. **`confidence` is kept** alongside `verified`. The two are orthogonal axes:
   `confidence` answers *where does this come from* (code / inference /
   declared), `verified` answers *who confirmed it*. A concept that is 100 %
   `[Code]` is highly reliable yet legitimately `unverified` in OKF terms.
   Custom keys are legal and preserved under the spec.
3. **v0.1 → v0.2 upgrade lands in `/doc-sync:migrate`**, which already detects
   `okf_version:`. No ninth skill for a one-shot operation.
4. **ADR statuses map onto the OKF vocabulary** — `Proposed→draft`,
   `Accepted→stable`, `Deprecated`/`Superseded→deprecated`. The ADR nuance,
   including "Superseded by 007", already lives in the body prose and stays
   there. One key, conformant. A v0.2 consumer reading `Accepted` would treat it
   as an unknown value and fall back to `stable` anyway.
5. **Actor identity is `doc-sync/<plugin version>`** (e.g. `doc-sync/2.3.0`),
   read from `plugin.json`. Always knowable, and the plugin version is what
   determines output quality. The model id is deliberately not encoded: it is
   not reliably known across harnesses.
6. **`stale_after` is written at human verification only** — `interview` sets it
   to +12 months when it records a `verified: human:` entry. One writer, one
   real use (human confirmations expire and must be re-asked). Writing it on
   every concept would expire the whole bundle on the same day and turn the
   signal into noise.

## Design

### Frontmatter contract

Every non-reserved concept:

```yaml
---
type: Feature
title: Authentification
description: Inscription, connexion, réinitialisation de mot de passe
tags: [auth]
generated: { by: doc-sync/2.3.0, at: 2026-07-28T14:00:00Z }
verified:
  - { by: human:olivier@fontenelle.org, at: 2026-07-28T15:12:00Z }
stale_after: 2027-07-28
sources:
  - id: rfc-6749
    resource: https://www.rfc-editor.org/rfc/rfc6749
    title: OAuth 2.0 Authorization Framework
    last_modified: 2012-10-01
confidence: mixed
---
```

- `generated` is always written. `verified`, `stale_after` and `sources` are
  omitted when empty — their absence carries meaning under v0.2.
- `status` is written only when it is not `stable` (absence means `stable` per
  spec), except on `Decision` concepts where it stays explicit.
- `sources[].usage_count` is never written: doc-sync has no usage data.
- Bundle-root `index.md` carries `okf_version: "0.2"` and nothing else.
- Removed: `timestamp` (→ `generated.at`), the `# Citations` heading
  (→ `sources` + `[^id]` footnotes), the `source:` key of `DECISION.md`
  (→ `sources` / `verified`).

### Trust model

| doc-sync event | frontmatter written | resulting tier |
|---|---|---|
| `init` / `update` writes a concept | `generated: { by: doc-sync/<v>, at: now }`, no `verified` | unverified |
| `challenge` re-checks a concept against code | append `verified: { by: process:doc-sync-challenge, at: now }` | machine-confirmed |
| `interview` — a human confirms | append `verified: { by: human:<id>, at: now }`, set `stale_after: now + 12 months` | human-reviewed |

Three rules, and no `verified` entry is ever deleted:

- `generated.at > max(verified[].at)` ⇒ the verification is **void** — the
  document was rewritten after it was confirmed. This falls out of `update`
  bumping `generated.at`; it needs no bookkeeping of its own.
- `today >= stale_after` ⇒ the human confirmation has **expired**.
- Corollary, added during implementation: `interview` must **not** bump
  `generated.at` for a plain confirmation or tag raise, or the verification it
  just recorded would be born void. It bumps `generated.at` only when it
  actually rewrites the assertion's text, and then writes the `verified` entry
  with an `at` at or after the new `generated.at`.
- Both are reported by `challenge` and `coverage`, and warned by the validator.
  Neither is an error: the spec forbids rejecting a bundle over them.

`human:<id>` comes from `git config user.email`; if unset, `interview` asks
once and reuses the answer for the session. The inline epistemic tags and
`confidence` are unchanged.

### `sources` and the `resource` constraint

A `sources` entry **requires** `resource`. Therefore doc-sync writes a `sources`
entry only for an addressable artifact — a file path in the repo or a URL.

- `ingest-existing-docs`: `resource` = the archived source's path,
  `last_modified` = its git date, `author` = its git author. Natural fit.
- `interview`: a source cited by the interviewee, when they give a path or URL.
- `update`: the plan/spec file when the user supplies a path.
- `update` with pasted ticket text, or session intent alone: **no addressable
  URI exists, so none is invented**. That intent stays in `log.md` prose, where
  it already goes today. This replaces the current behaviour of writing a
  `# Citations` line reading "session YYYY-MM-DD".

Per-claim attribution, when a body claim maps to one source, uses a markdown
footnote `[^<source id>]` keyed to `sources[].id`.

### Per-skill changes

- **`init`** — frontmatter contract section rewritten; writes `generated`, never
  `verified`; `sources` instead of `# Citations`; `okf_version: "0.2"`.
- **`update`** — bumps `generated.at` instead of `timestamp`; adds `sources`
  entries per the rule above; never writes `verified`.
- **`interview`** — appends the `verified: human:` entry and `stale_after`;
  records cited addressable sources; keeps raising inline tags to `[Declared]`.
- **`challenge`** — appends `verified: process:doc-sync-challenge` to concepts
  it re-checked and found accurate; reports void verifications, expired
  `stale_after`, and the trust-tier breakdown; sets `status: deprecated` on dead
  docs instead of only flagging them in prose.
- **`coverage`** — adds the three-tier distribution and a freshness count
  (void / expired) to `COVERAGE.md`, alongside the existing tag distribution
  and `confidence`.
- **`migrate`** — new v0.1 → v0.2 branch (below); its existing v1 → OKF branch
  now targets 0.2 directly.
- **`map`** — writes `okf_version: "0.2"`.
- **`ingest-existing-docs`** — `sources` entries for ingested documents;
  `generated.at` bump instead of `timestamp`.

### Templates

`OVERVIEW`, `ARCHITECTURE`, `FEATURE`, `TABLE`: `timestamp` → `generated`,
`# Citations` → `sources`. `DECISION`: OKF `status` vocabulary, `source:` key
dropped. `index.md`: `okf_version: "0.2"`. `log.md`: unchanged.

### `scripts/validate_okf.py`

The three hard conformance rules stay the **only** errors — the spec requires
consumers to tolerate everything else. New warnings:

- legacy `timestamp` key present (v0.1 residue)
- residual `# Citations` heading
- `status` outside `draft | stable | deprecated`
- `generated` / `verified` malformed (missing `by` or `at`, `verified` neither a
  mapping nor a list of mappings)
- `stale_after` not `YYYY-MM-DD`, or in the past
- `max(verified[].at) < generated.at` (void verification)
- `okf_version` present but not `"0.2"`
- a `[^id]` footnote with no matching `sources[].id`, and vice versa

Plus one summary line: counts of unverified / machine-confirmed /
human-reviewed. Still stdlib-only, no YAML dependency — the existing regex
frontmatter reader is extended to the handful of keys above rather than made
into a general YAML parser.

### `/doc-sync:migrate`, v0.1 → v0.2 branch

Detection: root `index.md` declares `okf_version: "0.1"` → upgrade branch (the
existing v1 branch triggers on the absence of any bundle marker). Per
non-reserved file:

1. `timestamp: X` → `generated: { by: doc-sync, at: X }`. The original date is
   preserved; `by` is the bare producer with no version, because the version
   that actually generated the document is unknown and writing the current one
   would be false.
2. `# Citations` list → `sources` entries with slugified ids; inline references
   to a citation become `[^id]` footnotes where they exist.
3. `DECISION` `status:` → OKF vocabulary; `source:` key dropped (its content is
   already in the body).
4. `confidence` carried over unchanged.
5. **No `verified` entry is added** — verification cannot be attributed
   retroactively. Every migrated concept is legitimately `unverified` until
   `challenge` or `interview` runs.
6. Bump `okf_version` to `"0.2"`, then run `validate_okf.py`.

### Housekeeping

- `plugin.json` and `marketplace.json`: `2.2.0 → 2.3.0`.
- README: OKF v0.2 section, trust-signal table, the epistemic-tags ↔ trust-tiers
  mapping, migration note.
- New `scripts/make_okf01_fixture.sh`: scaffolds a small OKF v0.1 bundle
  (`timestamp`, `# Citations`, ADR `status`, `okf_version: "0.1"`) so the
  migration branch is testable.

## Verification

- `validate_okf.py` on a bundle freshly generated by `init` — 0 errors,
  0 warnings.
- `validate_okf.py` on a bundle deliberately holding each new warning condition
  — each warning fires, exit code stays 0.
- `make_okf01_fixture.sh` → `/doc-sync:migrate` → validator clean, and the
  original `timestamp` dates preserved in `generated.at`.
- Manual run of `init` → `update` → `interview` → `challenge` → `coverage` on
  `make_fixture.sh` output: verify the tier of a concept moves unverified →
  machine-confirmed → human-reviewed, and that a subsequent `update` voids the
  human verification.

## Out of scope (YAGNI)

- `type: Attested Computation` and its `runtime` / `parameters` / `executor` /
  `receipt` / `attester` fields.
- `sources[].usage_count` — no usage data available.
- Retroactive `verified` attribution during migration.
- Reading v0.1 bundles as a permanent fallback mode: `migrate` upgrades them
  once. The validator warns on v0.1 residue rather than supporting it forever.
