---
author: /root
date: 2026-10-06
status: in-progress
agents: /root
summary: Prevent duplicate and stale web travel samples from affecting plans.
---

# Travel data quality

## Problem statement

Repeated searches append equivalent rows, while older web prices stay eligible for planning without a collection date.

## Requirements

- Record a UTC collection timestamp and source URLs on every new web row.
- Replace an equivalent web row while preserving its ID; never overwrite synthetic rows.
- Keep web rows in the JSON for traceability, but exclude them from planning after a configurable freshness period.
- Apply the same write policy to CLI and app searches; preserve the dataset count and existing rows.

## Decisions made

- A duplicate has the same normalized profile, group size, stay length, attraction, hotel, meal, transport mode, origin, and destination. Case, accents, and spacing do not affect matching.
- A web row without a valid collection timestamp is stale. The default freshness period is configured in `.env.example`.
- Refreshing a row replaces its extracted fields and sources with the new result. Each successful search is treated as a new observation; prices remain unverified.

## Implementation approach

Add shared persistence, duplicate-key, and freshness functions to `travel_search.py`. Both search entry points use the shared persistence. Filter stale web rows when the planner loads the catalog, without deleting the original JSON records.

## To-do

- [x] Add dated upsert behavior shared by CLI and app searches.
- [x] Exclude stale web rows from planning and document the freshness setting.
