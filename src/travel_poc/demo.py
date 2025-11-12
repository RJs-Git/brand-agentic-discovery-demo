"""Command line script that walks through the five demo stages."""
from __future__ import annotations

from pprint import pprint

from .booking_service import BookingService
from .data import build_knowledge_graph, build_price_catalog, seed_intent_catalog
from .events import EventBus
from .intent_catalog import IntentCatalog, IntentCatalogUpdater
from .inventory_manager import InventoryManager
from .search_service import AgentSearchService


def run_demo() -> None:
    """Execute the complete New Inventory to Agentic Booking scenario."""

    print("=== Initialising systems ===")
    graph = build_knowledge_graph()
    prices = build_price_catalog()
    event_bus = EventBus()
    intent_catalog = IntentCatalog(seed_intent_catalog())
    catalog_updater = IntentCatalogUpdater(intent_catalog, graph)
    event_bus.subscribe(catalog_updater)

    inventory = InventoryManager(graph, event_bus)
    search_api = AgentSearchService(graph, intent_catalog, prices)
    booking_api = BookingService(prices)

    print("\n=== Stage 1: New Inventory Addition ===")
    kids_event = inventory.add_hotel_amenity(
        hotel_id="hotel123",
        name="Kids' Club",
        description="Supervised activities for children ages 4-12.",
    )
    print("Added amenity event:")
    pprint(kids_event)

    ride_event = inventory.add_flight_service(
        flight_id="route789",
        name="Ride App Pickup",
        description="Door-to-door ground transfer partner included.",
    )
    print("Added service event:")
    pprint(ride_event)

    print("\n=== Stage 2: Knowledge Graph Verification ===")
    sunshine = graph.get_hotel("hotel123")
    print("Sunshine Resort amenities now include:", [a.name for a in sunshine.amenities])
    premium_flight = graph.get_flight("route789")
    print("Premium Economy services now include:", [s.name for s in premium_flight.services])

    print("\n=== Stage 3: Intent Catalog Update ===")
    for line in catalog_updater.activity_log:
        print("-", line)
    print("Current intent catalog snapshot:")
    pprint(intent_catalog.snapshot())

    print("\n=== Stage 4: Agent Search ===")
    family_results = search_api.search(intent="FamilyVacation", location="Hawaii")
    pprint(family_results)
    print(search_api.summarize_for_agent(family_results))

    business_results = search_api.search(intent="SeamlessJourney", route="JFK-LAX")
    pprint(business_results)
    print(search_api.summarize_for_agent(business_results))

    print("\n=== Stage 5: Booking via ACP ===")
    confirmation = booking_api.book(
        product_id="hotel123",
        user_reference="demo-user-001",
        stay_or_travel_details="1-7 Dec, Sunshine Resort",
    )
    pprint(confirmation)
    print(
        "Agent message:",
        f"Great news! Your stay is confirmed with code {confirmation.confirmation_code}.",
    )


if __name__ == "__main__":
    run_demo()
