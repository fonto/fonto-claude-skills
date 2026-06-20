<!--
OKF reserved file. Two patterns below — keep only the relevant one when generating.

BUNDLE ROOT index.md: the ONLY index.md allowed to carry frontmatter, and ONLY
the okf_version key. Subdirectory index.md files have NO frontmatter.

Body = one or more sections grouping concepts under a heading, each concept a
bullet: [link](relative/path.md) — one-line description (no epistemic tags).
This is the progressive-disclosure entry point: load only what's relevant.
-->

--- ROOT (<bundle>/index.md) ---
---
okf_version: "0.1"
---

# {Project Name} — Knowledge Bundle

> Consult these concepts on demand — load only what's relevant to your task.

## Overview
- [OVERVIEW.md](OVERVIEW.md) — Project purpose, tech stack, entry points, functional blocks
- [ARCHITECTURE.md](ARCHITECTURE.md) — Component map, data flows, external dependencies

## Features
- [features/{block}.md](features/{block}.md) — {one-line description}

## Data
- [data/index.md](data/index.md) — Data catalog (one concept per table)

## Decisions
- [decisions/{NNN}-{title}.md](decisions/{NNN}-{title}.md) — {one-line description}

## History
- [log.md](log.md) — Functional change history

--- SUBDIRECTORY (<bundle>/<dir>/index.md, NO frontmatter) ---
# {Group Heading}

- [{concept}.md]({concept}.md) — {one-line description}
