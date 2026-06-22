#!/usr/bin/env bash
# Create a throwaway repo with a doc-sync *v1* docs/ tree (no frontmatter,
# CHANGELOG-FUNCTIONAL.md, inline tags) to test /doc-sync:migrate.
# Usage: make_v1_fixture.sh [TARGET_DIR]   (default: /tmp/okf-v1)
set -euo pipefail
DIR="${1:-/tmp/okf-v1}"
PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [ -e "$DIR" ] || [ -L "$DIR" ]; then
  echo "refusing: $DIR already exists (rm it first or pass another path)" >&2
  exit 1
fi

mkdir -p "$DIR"/{migrations,src,docs/features,docs/decisions}
cd "$DIR"

# --- code (with NOT NULL / UNIQUE / FK so migrate must extract a data/ catalog) ---
cat > migrations/001_init.sql <<'SQL'
CREATE TABLE users (
  id    uuid PRIMARY KEY,
  email text NOT NULL UNIQUE
);
CREATE TABLE orders (
  id      uuid PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES users(id),
  total   int  NOT NULL
);
SQL
echo "export function login(){}" > src/auth.js
echo "export function checkout(){}" > src/billing.js
echo '{ "name": "okf-v1", "version": "0.0.0" }' > package.json

# --- v1 docs/ tree: NO frontmatter, inline epistemic tags ---
cat > docs/OVERVIEW.md <<'MD'
# okf-v1

> [Code] Auto-generated. Last updated: 2026-05-01

## Purpose
[Declared] A demo app for auth and billing. Confirmed by the team.

## Stack
[Code] JavaScript, PostgreSQL.
MD

cat > docs/ARCHITECTURE.md <<'MD'
# Architecture — okf-v1

> [Code] Last updated: 2026-05-01

## Component Map
[Code]
| Component | Responsibility | Location |
|-----------|---------------|----------|
| auth | login | `src/auth.js` |

## Data Models
[Code]
### users
- id: uuid — PK
- email: text — unique

### orders
- id: uuid — PK
- user_id: uuid — FK to users
MD

cat > docs/features/auth.md <<'MD'
# Authentication

## Purpose
[Declared] Lets a user log in. The team confirmed sessions last 24h.

## Business Rules
[Declared] Sessions expire after 24 hours.
MD

cat > docs/features/billing.md <<'MD'
# Billing

## Purpose
[Inference] Handles checkout.
MD

cat > docs/decisions/001-postgres.md <<'MD'
# 001 — Use PostgreSQL

**Date:** 2026-05-01
**Status:** Accepted
**Source:** [Declared] — lead engineer

## Context
Needed a relational store.

## Decision
PostgreSQL.
MD

cat > docs/CHANGELOG-FUNCTIONAL.md <<'MD'
# Functional Changelog

## 2026-05-01 — Initial documentation
- **What changed:** First documentation generated.
- **Why:** [Declared] Onboarding.
- **Impact:** auth, billing
- **Doc updated:** OVERVIEW.md, features/auth.md
MD

cat > docs/COVERAGE.md <<'MD'
# Documentation Coverage
Last updated: 2026-05-01
## Summary
- Functional blocks documented: 2
MD

# --- a CLAUDE.md carrying an old v1 map block (migrate should refresh it) ---
cat > CLAUDE.md <<'MD'
# Project

<!-- doc-sync:map:start -->
## Documentation Index

| File | Description |
|------|-------------|
| [docs/OVERVIEW.md](docs/OVERVIEW.md) | Project purpose |
<!-- doc-sync:map:end -->
MD

git init -q && git add -A && git commit -qm "init v1 fixture"
echo "v1 fixture ready: $DIR"
echo "next: cd $DIR && claude --plugin-dir $PLUGIN_DIR"
echo "then: /doc-sync:migrate    (expect docs/ -> docs/okf/, data/ catalog created)"
echo "check: python3 $PLUGIN_DIR/scripts/validate_okf.py $DIR/docs/okf"
