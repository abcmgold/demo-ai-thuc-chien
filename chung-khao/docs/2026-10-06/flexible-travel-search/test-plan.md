---
author: /root
date: 2026-10-06
status: todo
agents: /root
summary: Offline verification for preference-aware travel search and planner compatibility.
---

# Test plan

## Unit tests

- Prompt includes all relevant normalized preferences and uses group budget for a per-person budget.
- Zero-night search does not request a hotel; positive-night search requests lodging for the selected stay.
- A mocked search with source URLs and complete extracted values writes a web row that the planner can load and use in a schedule.
- A mocked partial row remains in the catalog but is excluded from itinerary choices.
- A newly sourced row with the same hotel name as an existing row remains eligible for lodging selection.
- Repeating the same mocked search refreshes one web record without raising the sample count again.

## End-to-end tests

- With organizer gateway credentials, submit different trip preferences in the app and inspect the search relevance, source URLs, saved row, and generated itinerary.

The end-to-end check incurs gateway charges and requires the real service.
