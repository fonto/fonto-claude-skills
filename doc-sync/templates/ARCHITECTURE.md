---
type: Architecture
title: Architecture — {Project Name}
description: Component map, data flows, external dependencies, configuration
timestamp: {YYYY-MM-DDThh:mm:ssZ}
confidence: mixed
---

# Architecture — {Project Name}

> [Code] / [Inference] Auto-generated. Last updated: {date}

## Component Map

[Code] {List of identified modules/services/packages with their responsibility.}

| Component | Responsibility | Location |
|-----------|---------------|----------|
| {component} | {what it does} | `{path}` |

## Data Flow

[Inference] {Describe the main data flows through the system. Use text descriptions — diagrams can be added later.}

### Primary Flow: {name}

1. {step 1}
2. {step 2}
3. {step 3}

## External Dependencies

[Code] {APIs, databases, queues, third-party services.}

| Dependency | Type | Purpose |
|-----------|------|---------|
| {dep} | {API/DB/Queue/Service} | {why it's used} |

## Data Models

[Code] {High-level summary only — each table/model is documented as its own OKF concept.}

See [data/index.md](data/index.md) for the full data catalog (one concept per table).

## Configuration

[Code] {Environment variables, config files, feature flags.}

| Variable | Purpose | Default |
|----------|---------|---------|
| {var} | {what it controls} | {default} |
