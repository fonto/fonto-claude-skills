#!/usr/bin/env bash
# Create a throwaway repo to test /doc-sync:ingest-existing-docs.
# Same code as make_fixture.sh, plus a stray LEGACY-DESIGN.md that mixes:
#   (a) a fact that still matches the code   -> should be ingested as [Code]
#   (b) a fact that contradicts the code     -> should surface a conflict question
#   (c) a design rationale                   -> should become a decisions/ concept
# Flow: run this -> /doc-sync:init -> /doc-sync:ingest-existing-docs LEGACY-DESIGN.md
# Usage: make_ingest_fixture.sh [TARGET_DIR]   (default: /tmp/okf-ingest)
set -euo pipefail
DIR="${1:-/tmp/okf-ingest}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(cd "$HERE/.." && pwd)"

# Reuse the base fixture (it creates $DIR, the code, and the initial commit).
"$HERE/make_fixture.sh" "$DIR"
cd "$DIR"

cat > LEGACY-DESIGN.md <<'MD'
# Legacy design notes

These notes predate the OKF bundle and are only *more or less* up to date.

## Authentication
The app supports user login and password reset by email.

## Orders
An order may have a NULL user_id to support anonymous guest checkout.

## Why Postgres
We chose Postgres over MongoDB because orders and users have strict relational
integrity requirements (every order references a real user).
MD

git add -A && git commit -qm "add legacy design notes"
echo "ingest fixture ready: $DIR"
echo "next: cd $DIR && claude --plugin-dir $PLUGIN_DIR"
echo "then: /doc-sync:init  ->  /doc-sync:ingest-existing-docs LEGACY-DESIGN.md"
