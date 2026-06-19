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

| Column | Type | Null | Key | Description |
|--------|------|------|-----|-------------|
| {id} | {uuid} | {no} | PK | {purpose} |
| {fk_id} | {uuid} | {no} | FK → [{other_table}](/data/{other_table}.md) | {purpose} |
| {field} | {type} | {yes/no} | — | {purpose} |

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
