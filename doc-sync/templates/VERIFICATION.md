---
type: Verification Harness
title: {Project} verification harness
description: How agents launch, drive and prove {Project} features.
generated: { by: doc-sync/2.4.0, at: {YYYY-MM-DDThh:mm:ssZ} }
# OKF §10 attested-computation vocabulary: the executor runs, it returns a
# receipt, an optional attester checks the receipt without an LLM. The CLI is
# project-owned; doc-sync only reads this declaration and never runs `drive`.
runtime: {playwright | panther | …}
executor:
  resource: {repo path of the project CLI}   # may not exist yet: say so in the body
  launch: "{cli} up"                          # ready = usable, not just "port answers"
  doctor: "{cli} doctor"                      # read-only health check, before every drive
  drive: "{cli} drive {feature} --sub {sub} --role {role} --evidence {dir}"
  cleanup: "{cli} down"                       # stops what the run started, keeps {dir}
  receipt: [feature, sub_passed, sub_failed, unreachable, sha, evidence_dir, exit_code]
attester: { resource: {repo path} }           # optional, deterministic
# apps: one entry per app; `routes` picks the routes_inventory.py adapter:
#   next-app (root = the app/ dir) | tanstack (root = routeTree.gen.ts)
#   | nestjs (root = the source dir) | cmd (routes_cmd prints one route per line)
# base_url_env / base_path are for the executor; surfaces stay app-relative.
apps:
  - { name: {app}, base_url_env: {ENV_VAR}, routes: {next-app}, root: {apps/x/src/app} }
roles: [{role}, …]                            # the vocabulary features' `roles` use
# accounts: names only. A password or token NEVER goes in the bundle — only the
# NAME of the env var that holds it, in secret_env.
accounts:
  - { role: {role}, email: {test account}, secret_env: {ENV_VAR} }
safety: { allowed_targets: [local, worktree], forbid_env: [staging, production] }
proof: { actor: process:{cli}, freshness_days: 30 }
confidence: {code | inference | to-confirm | declared | mixed}
---

# {Project} verification harness

## Baseline preconditions

[To confirm] {What a fresh run starts from: seeded DB, per-worktree ports, flags, mail capture.}

## Driving conventions

- Stable handles only: ARIA role + accessible name, `name=` attributes, `data-testid`, routes.
- Exercise the real user path — never an internal setter or a test-only endpoint.
- Capture the action and the resulting state, plus side effects (rows, emails, messages),
  and re-read a mutated state from a second, read-only view.
- Never weaken a journey to make it pass: a missing precondition is a failure, noted in
  the feature's Gotchas.
- Inconclusive, or proven on the wrong surface, is not a pass.

## Proof rules

- A live replay appends `{ by: <proof.actor>, at, sha }` to a feature's `verified` list,
  **only on `main`** and only when every sub-feature passed. Worktree agents never write
  `verified`: they attach evidence to their PR.
- `init`, `update`, `interview`, `ingest-existing-docs` and `migrate` never write a proof.
- A proof is stale at the first of: `freshness_days` elapsed, `generated.at` moved past
  it, or a commit since its `sha` touched a file behind one of the feature's surfaces.

## Failure triage

| Finding | Meaning | Action |
|---------|---------|--------|
| doc error | the map describes the feature wrongly | fix the feature concept |
| harness gap | the feature works but the harness can't drive it | fix the CLI, not the doc |
| product regression | the app no longer does what the map says | report it; never hide it in the doc |
| `verified-unreachable` | a precondition the harness lacks (account, inbox, flag) | name the precondition and the route tried |
