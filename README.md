# Agentic Travel PoC Demo

This repository contains a self-contained simulation of the **“New Inventory to Agentic Booking”** flow described in the product requirements documents. It models how a travel brand can add new offerings to its catalog and have an AI agent discover and book them end-to-end using mock data.

## Repository Structure

```
requirements/          Product requirements used to design the demo
src/travel_poc/        Python modules implementing the five demo stages
  ├── booking_service.py   Stage 5 – ACP booking handler
  ├── data.py              Synthetic knowledge graph, pricing, and intent seeds
  ├── demo.py              Command-line walkthrough of the scenario
  ├── events.py            Event definitions and a lightweight event bus
  ├── intent_catalog.py    Stage 3 – intent classification and catalog updates
  ├── inventory_manager.py Stage 1 – inventory ingestion façade
  ├── knowledge_graph.py   Stage 2 – in-memory Neptune substitute
  └── search_service.py    Stage 4 – agent-facing search API
```

## Running the PoC Walkthrough

The project has no third-party dependencies beyond the Python standard library. Execute the demo script to see the five stages in action:

```bash
python demo.py
```

Alternatively, if you prefer to invoke the package module directly, set `PYTHONPATH=src` and run `python -m travel_poc.demo`.

The script performs the following steps:

1. **Stage 1 – Inventory Addition:** Adds the *Kids’ Club* amenity to Sunshine Resort and the *Ride App Pickup* service to the JFK–LAX Premium Economy flight. Each addition emits an `InventoryAdded` event.
2. **Stage 2 – Knowledge Graph Update:** Reads back the updated hotel and flight nodes, showing that the new amenity/service are attached to their parents.
3. **Stage 3 – Intent Catalog Update:** Uses a rules-based classifier to map the new inventory to traveler intents (e.g., *FamilyVacation*, *SeamlessJourney*) and logs bundle updates.
4. **Stage 4 – Agent Search:** Queries the agent-facing search service for both hotel and flight intents, returning structured JSON and a conversational summary that highlights the new offerings.
5. **Stage 5 – Booking via ACP:** Simulates the booking call and returns a confirmation object, mirroring the Agentic Commerce Protocol’s confirmation step.

Running the script prints structured payloads and explanatory text so you can trace how the new features become discoverable and bookable.

## Testing

Basic automated tests cover the critical flows. Run them with:

```bash
pytest
```

These tests ensure that the intent catalog is updated by the event-driven flow, the search service surfaces the new inventory, and the booking service produces confirmation codes.
