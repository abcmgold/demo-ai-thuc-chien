---
author: /root
date: 2026-10-06
status: in-progress
agents: /root
summary: Verification cases for the itinerary agent workflow.
---

# Test plan

## Unit tests

- Validate rejected party size, day count, empty interests, malformed activity times, overlap, and wrong day count.
- Check per-person, per-group, and per-room-night arithmetic with room occupancy and missing prices.
- Check budget states: within, over, and unknown when a component is missing.
- Mock the gateway to check generation, bounded repair, revision context, and explicit failure.
- Mock Supabase to check save only occurs on explicit request.

## End-to-end tests

- Start FastAPI and Streamlit with a real organizer API key; generate a trip from the form and inspect every day and total.
- Request a revision and confirm the new plan is validated and displayed.
- Try generation with the key missing and confirm a clear error.
- Configure Supabase, click Save, and confirm one row is created. Without Supabase, confirm Save reports unavailable.

Real AI and Supabase calls can incur cost and need human verification in the configured environment.
