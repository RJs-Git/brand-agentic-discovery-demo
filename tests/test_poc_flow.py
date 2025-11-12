from travel_poc.booking_service import BookingService
from travel_poc.data import build_knowledge_graph, build_price_catalog, seed_intent_catalog
from travel_poc.events import EventBus
from travel_poc.intent_catalog import IntentCatalog, IntentCatalogUpdater
from travel_poc.inventory_manager import InventoryManager
from travel_poc.search_service import AgentSearchService


def build_services():
    graph = build_knowledge_graph()
    prices = build_price_catalog()
    event_bus = EventBus()
    catalog = IntentCatalog(seed_intent_catalog())
    updater = IntentCatalogUpdater(catalog, graph)
    event_bus.subscribe(updater)
    inventory = InventoryManager(graph, event_bus)
    search = AgentSearchService(graph, catalog, prices)
    booking = BookingService(prices)
    return graph, catalog, inventory, search, booking, updater


def test_inventory_event_updates_intent_catalog():
    graph, catalog, inventory, _, _, updater = build_services()

    inventory.add_hotel_amenity("hotel123", "Kids' Club")
    inventory.add_flight_service("route789", "Ride App Pickup")

    assert "hotel123" in catalog.list_products("FamilyVacation")
    assert "route789" in catalog.list_products("SeamlessJourney")
    assert any("Kids' Club" in entry for entry in updater.activity_log)


def test_search_returns_new_inventory():
    graph, catalog, inventory, search, _, _ = build_services()
    inventory.add_hotel_amenity("hotel123", "Kids' Club")

    payload = search.search(intent="FamilyVacation", location="Hawaii")
    assert payload["results"], "Expected to find at least one hotel"
    hotel = payload["results"][0]
    assert hotel["name"] == "Sunshine Resort"
    assert "Kids' Club" in hotel["features"]


def test_booking_confirmation_format():
    _, _, _, _, booking, _ = build_services()
    confirmation = booking.book("hotel123", user_reference="demo")
    assert confirmation.status == "CONFIRMED"
    assert confirmation.confirmation_code.startswith("HTL-")
