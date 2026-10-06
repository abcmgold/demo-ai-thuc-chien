---
author: /root
date: 2026-10-06
status: todo
agents: /root
summary: Checks for structured travel search output.
---

# Test plan

## Unit tests

- Reject missing dataset fields, invalid price types, and invalid group size.
- Calculate totals from per-person, per-room-night, and group round-trip amounts.
- Return a null total if any required price is missing.
- Consecutive appends assign unique IDs, increment `sample_count`, and retain prior rows.

## End-to-end tests

- With a gateway key, search a real Dak Lak query and inspect source URLs, JSON shape, and price evidence.
- Compare output keys with `data/synthetic_travel_samples.json`; verify unknown prices are null.

The end-to-end call incurs gateway search and model charges.
