---
type: {Postgres Table | MySQL Table | BigQuery Table | SQLite Table | Mongo Collection}
title: {table_name}
description: {What this table holds, in one line}
resource: {canonical URI, e.g. postgres://<db>/public/<table_name>}
tags: [{domain}]
timestamp: {YYYY-MM-DDThh:mm:ssZ}
confidence: code
---

# {table_name}

[Code] {What this table stores and its role in the system.}

# Schema

[Code]

<!--
Read the DDL / ORM model LITERALLY — do not guess:
- Null: "no" if the source declares NOT NULL or the column is a primary key;
  "yes" ONLY when there is no NOT NULL and it is not a PK. If the source is
  ambiguous, tag that row [To confirm] instead of asserting [Code].
- Key: PK | FK → [other](/data/other.md) | — (combine with a comma if both).
- Constraints: UNIQUE, DEFAULT <x>, CHECK(<…>), generated, etc. "—" if none.
-->

| Column | Type | Null | Key | Constraints | Description |
|--------|------|------|-----|-------------|-------------|
| {id} | {uuid} | no | PK | — | {purpose} |
| {fk_id} | {uuid} | no | FK → [{other_table}](/data/{other_table}.md) | — | {purpose} |
| {email} | {text} | no | — | UNIQUE | {purpose} |
| {field} | {type} | {yes/no} | — | {DEFAULT/CHECK/—} | {purpose} |

## Relationships

[Code] {FKs link to other table concepts above. Describe the relationship in prose.}

- {This table} {has many / belongs to} [{other_table}](/data/{other_table}.md)

# Examples

[Inference]

```sql
{a typical query against this table}
```

# Citations

{Only when claims come from external sources.}
