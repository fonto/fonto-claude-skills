#!/usr/bin/env bash
# Create a throwaway OKF *v0.1* knowledge bundle (legacy `timestamp`, body
# `# Citations`, ADR `status`/`source` keys, `okf_version: "0.1"`) to test the
# v0.1 -> v0.2 upgrade branch of /doc-sync:migrate.
# Usage: make_okf01_fixture.sh [TARGET_DIR]   (default: /tmp/okf01)
set -euo pipefail
DIR="${1:-/tmp/okf01}"
PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [ -e "$DIR" ] || [ -L "$DIR" ]; then
  echo "refusing: $DIR already exists (rm it first or pass another path)" >&2
  exit 1
fi

mkdir -p "$DIR"/{features,decisions}
cd "$DIR"

# --- bundle-root index.md: the only file allowed frontmatter beyond okf_version ---
cat > index.md <<'MD'
---
okf_version: "0.1"
---

# okf01-fixture — Knowledge Bundle

> Consult these concepts on demand — load only what's relevant to your task.

## Features
- [features/auth.md](features/auth.md) — Login, session management, password reset
- [features/billing.md](features/billing.md) — Checkout and invoicing
- [features/notifications.md](features/notifications.md) — Transactional email notifications

## Decisions
- [decisions/001-use-postgres.md](decisions/001-use-postgres.md) — Use PostgreSQL

## History
- [log.md](log.md) — Functional change history
MD

# --- subdirectory index.md: RESERVED, no frontmatter ---
cat > features/index.md <<'MD'
# Features

- [auth.md](auth.md) — Login, session management, password reset
- [billing.md](billing.md) — Checkout and invoicing
- [notifications.md](notifications.md) — Transactional email notifications
MD

# --- concept 1: legacy timestamp + # Citations (URL + bundle-relative path) + inline refs ---
cat > features/auth.md <<'MD'
---
type: Feature
title: Authentication
description: Login, session management, and password reset
tags: [auth]
timestamp: 2025-11-03T09:15:00Z
confidence: declared
---

# Authentication

> Last updated: 2025-11-03

## Purpose

[Declared] Lets a user log in and manage their session.

## Behavior

### Login

[Code] Validates credentials against the users table and issues a session token.

**Trigger:** POST /login
**Expected outcome:** A session token is returned
**Error cases:** Invalid credentials return 401

## Business Rules

[Declared] Sessions expire after 24 hours, per the OAuth 2.0 recommendation [1].
The original design rationale is captured in the internal spec [2].

1. Sessions expire after 24 hours.
2. Password reset links expire after 1 hour.

## Edge Cases

[Inference] Concurrent logins from multiple devices are allowed.

- Expired token: user is redirected to login.

## Dependencies

[Code] Depends on the users table in data/.

## Open Questions

- [ ] None currently.

# Citations

1. OAuth 2.0 Authorization Framework — https://www.rfc-editor.org/rfc/rfc6749
2. Internal Auth Design Spec — specs/auth-design.md
MD

# --- concept 2: legacy timestamp only, distinct past date ---
cat > features/billing.md <<'MD'
---
type: Feature
title: Billing
description: Checkout and invoicing
tags: [billing]
timestamp: 2026-01-20T16:42:00Z
confidence: inference
---

# Billing

> Last updated: 2026-01-20

## Purpose

[Inference] Handles checkout and payment processing.

## Behavior

### Checkout

[Code] Creates an order and charges the payment method.

**Trigger:** POST /checkout
**Expected outcome:** Order created, payment charged
**Error cases:** Payment failure rolls back the order

## Business Rules

[Inference] Orders cannot be modified after checkout completes.

1. Orders are immutable after checkout.

## Edge Cases

[Inference] Partial refunds are not yet supported.

- Payment timeout: order rolled back.

## Dependencies

[Code] Depends on the orders table in data/.

## Open Questions

- [ ] Confirm refund policy with product.
MD

# --- concept 3: legacy timestamp only, third distinct past date ---
cat > features/notifications.md <<'MD'
---
type: Feature
title: Notifications
description: Email notifications for account and billing events
tags: [notifications]
timestamp: 2026-04-05T11:00:00Z
confidence: code
---

# Notifications

> Last updated: 2026-04-05

## Purpose

[Code] Sends transactional emails for account and billing events.

## Behavior

### Email dispatch

[Code] Sends an email via the notification queue when a triggering event occurs.

**Trigger:** order.created, password.reset events
**Expected outcome:** Email queued and sent
**Error cases:** Queue failure retries up to 3 times

## Business Rules

[Code] Notifications are sent asynchronously via a queue.

1. Emails retry up to 3 times on failure.

## Edge Cases

[Inference] Duplicate events are deduplicated by event id.

- Queue unavailable: event is retried later.

## Dependencies

[Code] Depends on billing and auth events.

## Open Questions

- [ ] None currently.
MD

# --- decisions/ concept: ADR status vocabulary + old source key, own timestamp ---
cat > decisions/001-use-postgres.md <<'MD'
---
type: Decision
title: 001 — Use PostgreSQL
description: Chose PostgreSQL as the primary relational store
timestamp: 2025-09-12T10:00:00Z
status: Accepted
source: [Declared] — lead engineer
confidence: declared
---

# 001 — Use PostgreSQL

> Status: Accepted · Source: lead engineer

## Context

[Declared] The team needed a relational store with strong transactional
guarantees for orders and payments.

## Options Considered

### Option A: PostgreSQL
- **Pros:** Mature, strong consistency, JSONB support.
- **Cons:** Requires operational overhead for scaling.

### Option B: MongoDB
- **Pros:** Flexible schema.
- **Cons:** Weaker transactional guarantees for financial data.

## Decision

[Declared] PostgreSQL, chosen for ACID guarantees on the billing tables.

## Consequences

- [Declared] Billing and auth tables live in a single relational schema.
- [Inference] Future read-heavy reporting may need a read replica.
- Onboarding requires basic SQL familiarity.
MD

# --- log.md: RESERVED, no frontmatter ---
cat > log.md <<'MD'
# Log

## 2026-01-20

* **Update**: Added billing checkout flow. Why: [Declared] Requested by product
  for the Q1 launch. Impact: billing. Docs: features/billing.md.

## 2025-11-03

* **Creation**: Initial documentation generated. Why: [Declared] Onboarding
  docs requested by the team. Impact: auth. Docs: features/auth.md.
MD

git init -q && git add -A && git commit -qm "init OKF v0.1 fixture"
echo "OKF v0.1 fixture ready: $DIR"
echo "next: cd $DIR && claude --plugin-dir $PLUGIN_DIR"
echo "then: /doc-sync:migrate $DIR $DIR    (expect okf_version -> 0.2, timestamp -> generated.at, Citations -> sources)"
echo "check: python3 $PLUGIN_DIR/scripts/validate_okf.py $DIR"
