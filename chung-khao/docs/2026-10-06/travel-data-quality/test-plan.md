---
author: /root
date: 2026-10-06
status: todo
agents: /root
summary: Unit and end-to-end checks for travel data freshness and deduplication.
---

# Test plan

## Unit tests

- Matching web samples with case, accent, or spacing changes replace the original ID and keep count stable.
- Distinct samples append; synthetic rows are not overwritten.
- Missing or invalid collection dates and dates beyond the configured freshness window are excluded from the planner catalog.
- Fresh web and synthetic samples remain eligible.

## End-to-end tests

- Run the same sourced search twice and confirm the second run refreshes the same web row.
- Advance the freshness window and confirm old web rows do not appear in a generated itinerary.

Real searches and generation incur gateway charges.
