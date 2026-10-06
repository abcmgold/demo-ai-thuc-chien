---
author: /root
date: 2026-10-06
status: in-progress
agents: /root
summary: Use relevant trip preferences in web search without changing planner cost boundaries.
---

# Flexible travel search

## Problem statement

The app's web search prompt omits the selected starting point, lodging nights, and meal count. The search can therefore return a sample that fits the destination but not the user's requested trip shape.

## Requirements

- Include all trip preferences that affect search relevance: party size, days, interests, transport, comfort, pace, group budget, starting point, lodging nights, and meals per day.
- Explain that an unspecified external origin does not provide an intercity fare; keep the existing in-destination round-trip cost scope.
- Do not request lodging for a zero-night trip, while preserving the catalog sample schema and planner behavior.
- Verify prompt content and search-to-catalog-to-planner compatibility without a paid API call.
- When a newly sourced row names an existing catalog hotel, prefer the newer row for lodging selection.

## Decisions made

- Keep the established Buôn Ma Thuột in-destination transport origin and the current JSON sample structure.
- Use conditional prompt text for zero versus positive lodging nights.
- Keep budget basis as the already calculated group budget; the UI toggle is not a travel fact.
- Keep hotel-name deduplication, with later catalog rows taking precedence.

## Implementation approach

Update the request-driven search and extraction prompts. Prefer later catalog rows when consolidating the same hotel. Add local unit coverage for prompt variations and a mocked search/extraction flow that writes to a temporary dataset, then loads it through the planner.

## To-do

- [x] Include starting point, nights, and meal count in the search prompt with correct zero-night wording.
- [x] Add and run local compatibility checks for prompt and catalog planning.
