---
author: /root
date: 2026-10-06
status: in-progress
agents: /root
summary: Connect the planner UI to a validated AI itinerary workflow.
---

# Itinerary agent workflow

## Problem statement

The planner currently shows a fixed preview. The architecture describes direct AI generation, deterministic checks, bounded repair, revision, and optional save, but that workflow is absent.

## Requirements

- Accept trip preferences and optional context through FastAPI.
- Generate a structured Dak Lak itinerary through the configured AI gateway without retrieval or web search.
- Check day count, ordered non-overlapping activities, positive durations, explicit cost units, room occupancy and night counts, and group budget fit.
- Retry invalid model output a bounded number of times and surface clear errors.
- Support revision with original preferences and the current plan; save only on explicit request when Supabase is configured.
- Replace the static planner preview with live generation, review, revision, and save controls.
- Keep external facts labeled as unverified suggestions and prices as estimates.

## Decisions made

- Keep the removed `backend/` path absent. Add a small `agent/` package and `api.py` inside `chung-khao/`.
- Use the existing `nexus.chat` gateway wrapper in JSON mode. Use Pydantic contracts and Decimal arithmetic.
- Use `gpt-6-luna` as the configurable itinerary inference model through the existing gateway.
- The UI calls the FastAPI service over a configurable local URL. No AI key is sent to the browser.
- Optional persistence uses Supabase REST and requires explicit save. No read endpoint or authentication is added.

## Implementation approach

Define strict request and response contracts, a deterministic schedule and cost validator, and an orchestration service that calls the AI gateway and repairs invalid responses. Expose generate, revise, save, and health endpoints. Wire the existing Streamlit planner to the API and document local startup. Keep runtime settings in `.env.example`.

## To-do

- [x] Add contracts, configuration, validation, and cost calculations.
- [x] Add generation, repair, revision, optional save, and FastAPI routes.
- [x] Wire planner form, itinerary review, revision, and save to the API.
- [ ] Document setup and handoff for human end-to-end verification.
