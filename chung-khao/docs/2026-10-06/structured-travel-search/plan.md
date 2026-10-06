---
author: /root
date: 2026-10-06
status: in-progress
agents: /root
summary: Produce structured travel search data matching the sample dataset.
---

# Structured travel search

## Problem statement

The root search demo prints prose, which cannot be consumed as travel sample data.

## Requirements

- Keep round work under `chung-khao/`.
- Search the web through the configured gateway and append a sample to the existing dataset JSON.
- Preserve source URLs and distinguish unverified or missing prices from verified prices.
- Calculate totals from component prices; leave totals unknown when any component is unknown.
- Read query and models from configuration.
- Keep unique sample IDs and update dataset count and provenance metadata.

## Decisions made

- Add `chung-khao/travel_search.py` as the round-local search demo.
- Use the existing Nexus search and JSON helpers in two calls. Use the first sample as a shape guide, never as factual evidence.
- Use `null` for unavailable numeric values and include source URLs in `notes`.
- Preserve existing synthetic rows; label the resulting dataset as mixed synthetic and web-sourced data.

## Implementation approach

Load the sample file for its shape, search for the configured query, ask the model to extract one sample, validate required structure and numeric fields, calculate the total in Python, assign the next ID, append it to the dataset, update metadata and write the dataset back. Print the appended sample.

## To-do

- [x] Add the round-local structured search script and configuration examples.
- [x] Review the resulting schema, price calculation, and usage instructions.
- [x] Append each search result to the dataset with a unique ID and accurate metadata.
- [x] Update run instructions for the append behavior.
