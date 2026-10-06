---
author: linhbk3@techcombank.com.vn
date: 2026-10-06
status: in-progress
agents: /root
summary: Current Streamlit architecture for web-sourced travel search and catalog-based itinerary planning.
---

# Dak Lak AI Travel Assistant — Current Architecture

## 1. Objectives

Turn a travel party's size, trip length, VND budget, and preferences into a reviewable Dak Lak itinerary with places, meals, lodging, and estimated costs. Each planning request searches the web for a relevant travel sample, records it in the local catalog, and uses eligible catalog entries to build the itinerary. Travelers can adjust the plan and download it as an Excel file.

The catalog begins with synthetic examples and may contain web-sourced records. Source URLs and collection times support traceability and freshness filtering, but do not independently verify prices, opening hours, routes, or availability. The budget covers the party's in-destination spending unless the traveler selects a per-person basis. Booking and live availability remain outside the product.

## 2. Techstacks

| Name | Description | Config / Ability |
|---|---|---|
| Python and Streamlit | Web interface and backend workflow in one app | Capture preferences, run search and planning, display adjustments, and offer Excel export. |
| Organizer AI gateway | External web search, structured extraction, and itinerary selection | Return search answers with source URLs, extract one catalog sample, and choose catalog entries for a trip. |
| JSON travel catalog | Local synthetic and web-sourced travel samples | Keep source URLs and collection times; supply eligible entries to the planner. |
| Python validation and calculation | Catalog quality and itinerary rules | Refresh matching web records, exclude incomplete or stale records, validate choices, and calculate VND costs. |
| OpenPyXL | Itinerary export | Build the downloadable Excel workbook from the reviewed plan. |

## 3. Architecture

ASCII is sufficient because one Streamlit app coordinates the search, catalog, planning, and review flow.

```text
Traveler --> Streamlit app --> Search & extraction <--> Organizer AI gateway
                                  |
                                  v
                           JSON travel catalog
                                  |
                                  v
                       Catalog-based AI selection <--> Organizer AI gateway
                                  |
                                  v
                       Python validation & costs
                                  |
                                  v
                       Streamlit review & Excel export
```

The app runs the backend workflow in its own process. Python checks determine which catalog records and AI selections can influence the final plan.

## 4. Dataflow

1. **Search:** Normalize submitted trip preferences and ask the gateway's web-search capability for a relevant Dak Lak attraction, meal, hotel, transport option, prices, and source URLs. A result without source URLs stops the request.
2. **Structure and record:** Use a second AI call to extract one catalog sample. Check its shape and known prices, leave unsupported facts unknown, then store source URLs and a UTC collection time. Refresh a matching web record or append a new one while preserving synthetic examples.
3. **Filter:** Check catalog IDs and price arithmetic. Keep incomplete web records for traceability but exclude them from planning. Exclude web records older than the configured freshness window; collection time does not establish when a source last updated its price.
4. **Plan:** Give eligible catalog choices and a low-cost budget baseline to the itinerary model. Validate selected IDs, lodging, and day count, then calculate daily, lodging, party, and per-person totals in Python. Retry an invalid selection once; show an error if it remains invalid.
5. **Review:** Show the plan with unverified-price and budget notices. Traveler adjustments reuse eligible catalog choices and recalculate totals. Export the reviewed plan to Excel.

## 5. Deployment

Run the Streamlit app in a Python environment with a writable, persistent local catalog and network access to the organizer AI gateway. Configure gateway credentials, search and extraction models, and the web-record freshness window outside the application. The current round code does not include a separate API service or database deployment.

## Backlog

- **2026-10-06:** Refocus the architecture on backend processing, remove frontend stack choices, and make ingestion, retrieval, constraint planning, AI boundaries, and validation explicit before frontend design.
- **2026-10-06:** Align the current backend with direct LLM-generated travel data: remove the proposed catalog, web search, retrieval, ranking, and RAG paths; limit validation claims to what can be checked without external facts.
- **2026-10-06:** Add the active web search and catalog workflow: searches use trip preferences, sourced records are validated and refreshed in the catalog, and only complete, recent records can reach the itinerary planner. Retain the direct API as a separate path while the web client uses catalog planning.
- **2026-10-06:** Record a current integration gap: catalog validation rejects some supplied synthetic lodging areas, and the search-to-plan handoff can fail after a catalog write. The workflow above describes the intended boundary; these defects still need correction.
- **2026-10-06:** Recheck the current round code and show web search as a backend step before catalog planning. Remove the unimplemented FastAPI, Supabase, and direct-generation path from the current architecture; include the Streamlit review, adjustment, and Excel export path.
