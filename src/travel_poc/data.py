"""Mock data fixtures used across the travel agent PoC demo."""
from __future__ import annotations

from typing import Dict, List

from .knowledge_graph import KnowledgeGraph
from .models import Flight, Hotel, PriceQuote, Service


def build_knowledge_graph() -> KnowledgeGraph:
    """Create the base knowledge graph with a handful of hotels and flights."""

    hotels: List[Hotel] = [
        Hotel(
            id="hotel123",
            name="Sunshine Resort",
            location="Hawaii",
            amenities=[],
            tags=["Resort", "Beachfront"],
        ),
        Hotel(
            id="hotel456",
            name="OceanView Retreat",
            location="Hawaii",
            amenities=[],
            tags=["Resort"],
        ),
    ]

    flights: List[Flight] = [
        Flight(
            id="route789",
            route="JFK-LAX",
            travel_class="PremiumEconomy",
            services=[
                Service(
                    id="service-0",
                    name="Lounge Access",
                    description="Pre-flight lounge access at JFK",
                )
            ],
            tags=["Premium"],
        ),
        Flight(
            id="route321",
            route="SFO-SEA",
            travel_class="Business",
            services=[],
            tags=["Business"],
        ),
    ]

    return KnowledgeGraph(hotels=hotels, flights=flights)


def build_price_catalog() -> Dict[str, PriceQuote]:
    """Create a synthetic pricing store used by the search and booking flows."""

    return {
        "hotel123": PriceQuote(
            product_id="hotel123",
            price=250.0,
            currency="USD",
            availability="Dec 1-7: Available",
            extra={"room_type": "Ocean View Suite"},
        ),
        "hotel456": PriceQuote(
            product_id="hotel456",
            price=210.0,
            currency="USD",
            availability="Dec 1-7: Limited",
            extra={"room_type": "King Room"},
        ),
        "route789": PriceQuote(
            product_id="route789",
            price=450.0,
            currency="USD",
            availability="Next flight: 2025-12-15 08:00",
            extra={"seats_left": "5"},
        ),
        "route321": PriceQuote(
            product_id="route321",
            price=320.0,
            currency="USD",
            availability="Next flight: 2025-11-20 13:30",
            extra={"seats_left": "3"},
        ),
    }


def seed_intent_catalog() -> Dict[str, List[str]]:
    """Starting state for the intent catalog used in Stage 3."""

    return {
        "FamilyVacation": ["hotel456"],
        "BusinessTrip": ["route789"],
        "EcoTravel": [],
    }
