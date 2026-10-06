---
author: linhbk3@techcombank.com.vn
date: 2026-10-06
status: in-progress
agents: /root
summary: Implement the direct AI itinerary backend described by the architecture.
---

# Backend implementation

## Problem statement

The backend currently contains only package markers. It cannot accept preferences, generate or revise an itinerary, check costs and schedule consistency, or save a reviewed plan.

## Requirements

- Accept and validate trip preferences and optional context through FastAPI.
- Generate and revise structured itineraries through the configured AI API, with bounded repair for invalid output.
- Validate day count, activity order and duration, cost units, and completeness; calculate totals in backend code.
- Explain unknown costs and externally unverified facts in every result.
- Save only on an explicit request, through optional Supabase storage.
- Configure credentials, URLs, model, retries, timeout, and budget assumptions outside code.
- Keep the implementation within the current package boundaries and document local deployment.

## Decisions made

- Use an OpenAI-compatible chat completions API adapter until the organizer's protocol is confirmed. The endpoint URL and model are configurable.
- Use Pydantic contracts for strict JSON output and HTTP input. Use `Decimal` for price arithmetic.
- AI output contains daily activities and line-item costs with explicit per-person, per-group, or per-room-night units. The backend computes all totals.
- A missing cost makes budget fit unknown. The AI must include assumptions and estimated price fields for all known components.
- Use Supabase REST only when its settings are present; the save endpoint returns unavailable otherwise.
- No authentication is included because the architecture does not specify accounts; the save API returns an ID but provides no public read endpoint.

## Implementation approach

Implement contracts, pure validation and arithmetic, the AI and storage adapters, the orchestration service, FastAPI routes, environment settings, and deployment instructions. The API exposes `POST /itineraries/generate`, `POST /itineraries/revise`, `POST /itineraries/save`, and `GET /health`. The caller supplies original preferences and current itinerary for revision. Save takes the reviewed itinerary and preferences explicitly.

## To-do

- [x] Add strict request and itinerary contracts plus environment configuration.
- [x] Implement schedule validation and deterministic cost calculation.
- [x] Implement the configured AI adapter and bounded generation/revision workflow.
- [x] Implement optional Supabase save and FastAPI routes.
- [x] Document configuration, API use, deployment, and verification steps.
