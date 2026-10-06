---
author: linhbk3@techcombank.com.vn
date: 2026-10-06
status: todo
agents: /root
summary: Unit and end-to-end checks for the direct AI itinerary backend.
---

# Test plan

## Unit tests

- Input rejects nonpositive party size, days, budget, and empty interests; defaults appear in normalized input.
- Output rejects wrong day count, overlapping or unordered activities, nonpositive duration, unsupported cost unit, and inconsistent lodging nights.
- Cost calculator multiplies per-person prices by party size, per-room-night prices by rooms and nights, and per-group prices once.
- Unknown prices produce unknown budget fit and list missing components.
- Workflow retries invalid model output only up to the configured limit and returns a clear failure after exhaustion.
- Revision includes original preferences and current itinerary; save is never called by generation or revision.
- API maps invalid client input, AI failure, and unavailable persistence to clear responses.

## End-to-end tests

- Call generation and revision against the real organizer AI API, inspect schedule, estimates, assumptions, and confirmation notice.
- With a real Supabase table, explicitly save a reviewed plan and inspect the stored JSON.
- Deploy to Cloud Run with environment variables and check health, generation, failure reporting, latency, and AI usage cost.

The end-to-end checks require external services and may incur cost.
