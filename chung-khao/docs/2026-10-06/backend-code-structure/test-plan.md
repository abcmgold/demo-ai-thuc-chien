---
author: linhbk3@techcombank.com.vn
date: 2026-10-06
status: todo
agents: /root
summary: Verification plan for the backend scaffold and later behavior.
---

# Test plan

## This structure change

- Review the tree against `chung-khao/docs/architecture.md`.
- Confirm every package has one documented responsibility and optional storage is isolated.
- Confirm no runtime behavior, credentials, or organizer files were changed.

## Unit tests for later implementation

- Request validation: required fields, optional defaults, invalid values.
- Response validation: schema, day count, activity order, duration, and price units.
- Cost calculation: party totals, nights, room occupancy, unknown components, and budget comparison.
- Workflow: bounded repair and explicit failure after invalid AI output; revision revalidation.
- Save flow: persist only after the traveler explicitly chooses to save.

## End-to-end tests for later implementation

- Against the configured organizer AI API, generate and revise an itinerary and inspect estimates and confirmation notices.
- With a real Supabase project, save an approved itinerary and retrieve it.
- In Cloud Run, verify configured credentials, timeouts, failure reporting, and API reachability.

The later end-to-end checks require real services and may incur cost. This scaffold has no executable behavior to exercise yet.
