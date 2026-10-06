---
author: /root
date: 2026-10-06
status: todo
agents: /root
summary: Verification coverage for request driven travel search.
---

# Test plan

## Unit tests

- Mock web search and extraction to check that the query includes user preferences.
- Check that missing sources or malformed records leave the catalog unchanged; incomplete priced records retain null values and are excluded from schedules.
- Check a complete row gets a unique ID, correct total, provenance and updated count.
- Check the planner loads a mixed catalog and rejects invalid cost fields.
- Check the catalog cache is refreshed after append and search validation errors reach the form.

## End-to-end tests

- In the real app with gateway credentials, submit preferences and confirm one new sample is appended before the schedule is generated.
- Confirm search failure gives a visible error and the catalog remains valid.
