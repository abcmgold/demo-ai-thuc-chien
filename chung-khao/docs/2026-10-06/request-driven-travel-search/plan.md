---
author: /root
date: 2026-10-06
status: in-progress
agents: /root
summary: Search for trip relevant samples before generating an itinerary.
---

# Request driven travel search

## Problem statement

The planner only reads a static catalog. The existing web search script uses a fixed query and writes rows that the planner cannot load.

## Requirements

- After the user submits trip preferences, search for a relevant Đắk Lắk sample and append it before itinerary generation.
- Build the search prompt from normalized user preferences; keep model choices configurable.
- Keep the catalog valid for the planner, retain provenance, and mark unknown web prices as null.
- Show a useful error when search or extraction fails, without damaging the catalog.

## Decisions made

- Reuse the current web search and extraction helpers in `travel_search.py`.
- Save sourced but incomplete web records with null fields and totals. The planner skips incomplete records when selecting itinerary samples.
- Search once per form submission, then generate the schedule from the catalog file; catalog loading now reads the file on each call.
- Show search validation failures directly in the form so the user can identify missing source data; keep gateway failures generic except for status codes.
- Validate top-level party and lodging constraints only at the root sample; nested sample objects have different fields.

## Implementation approach

Add a callable search-and-append function, construct its query from the normalized request, validate the extracted row and sources, and write atomically. Connect it in the Streamlit submit path before `generate_plan`. Update the planner catalog validation for mixed metadata and document configuration.

## To-do

- [x] Implement request based search and safe catalog append.
- [x] Connect search to planner submission and mixed catalog loading.
- [x] Document configuration and human verification steps.
- [x] Report the specific search validation failure and use the newly written catalog on the next planner call.
- [x] Fix nested sample validation and save sourced partial records without making them selectable for schedules.
