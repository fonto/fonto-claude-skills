#!/usr/bin/env bash
# Create a throwaway repo to test doc-sync skills against.
# Usage: make_fixture.sh [TARGET_DIR]   (default: /tmp/okf-test)
set -euo pipefail
DIR="${1:-/tmp/okf-test}"
PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [ -e "$DIR" ] || [ -L "$DIR" ]; then
  echo "refusing: $DIR already exists (rm it first or pass another path)" >&2
  exit 1
fi

mkdir -p "$DIR"/{migrations,src}
cd "$DIR"

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

cat > src/auth.js <<'JS'
// authentication: login + password reset
export function login(email, password) {}
export function requestPasswordReset(email) {}
JS

cat > src/billing.js <<'JS'
// billing: checkout + invoice
export function checkout(userId, items) {}
JS

cat > package.json <<'JSON'
{ "name": "okf-test", "version": "0.0.0", "description": "doc-sync test fixture" }
JSON

git init -q && git add -A && git commit -qm "init fixture"
echo "fixture ready: $DIR"
echo "next: cd $DIR && claude --plugin-dir $PLUGIN_DIR"
