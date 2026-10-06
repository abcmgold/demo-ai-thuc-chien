---
author: /root
date: 2026-10-06
status: in-progress
agents: /root
summary: Run the structured travel web search demo.
---

# Usage

Set `THUCCHIEN_API_KEY` and the `TRAVEL_*` values from `chung-khao/.env.example` in `chung-khao/.env`, then run from the repository root:

```bash
python3 chung-khao/travel_search.py
```

Each run appends one sample to `chung-khao/data/synthetic_travel_samples.json`, updates its count and provenance notes, and prints the new sample. Unavailable prices appear as `null`; if any required price is unknown, `sample_total_vnd` is `null` too. Source URLs appear in the dataset's `notes`.
