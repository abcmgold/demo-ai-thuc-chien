---
author: linhbk3@techcombank.com.vn
date: 2026-10-06
status: in-progress
agents: /root
summary: Create a readable backend code scaffold aligned with the current architecture.
---

# Backend code structure

## Problem statement

The architecture describes a direct AI itinerary backend, but the round folder has no source layout. Developers need clear places for each responsibility before implementation begins.

## Requirements

- Keep all files under `chung-khao/` and preserve the organizer's layout.
- Mirror the current architecture: HTTP boundary, request and response contracts, itinerary workflow, AI provider, consistency checks, configuration, and optional storage.
- Make module ownership and the direct generation flow easy to inspect.
- Add no runtime behavior or unapproved external integration in this structure-only change.

## Decisions made

- Use `chung-khao/backend/app/` as the Python package root.
- Group code by responsibility, with one README explaining where future code belongs.
- Keep optional persistence separate from the generation path.
- Use package markers and module docstrings as placeholders; no executable API is introduced.

## Implementation approach

Create the package skeleton and a backend README showing the tree, call direction, and file ownership. Document future unit and end-to-end checks in `test-plan.md`.

## To-do

- [x] Create the backend package skeleton matching the architecture.
- [x] Document module responsibilities and request flow for developers.
- [x] Review the scaffold against the architecture and ensure no unrelated files are included.
