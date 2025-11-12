"""Agent-facing search API simulation for Stage 4."""
from __future__ import annotations

from typing import Dict, List, Optional

from .intent_catalog import IntentCatalog
from .knowledge_graph import KnowledgeGraph
from .models import PriceQuote


class AgentSearchService:
    """Provides structured search responses similar to an Answers API."""

    def __init__(
        self,
        graph: KnowledgeGraph,
        catalog: IntentCatalog,
        price_catalog: Dict[str, PriceQuote],
    ) -> None:
        self._graph = graph
        self._catalog = catalog
        self._price_catalog = price_catalog

    def search(
        self,
        intent: str,
        location: Optional[str] = None,
        route: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, object]]]:
        product_ids = self._catalog.list_products(intent)
        hotels = self._graph.find_hotels_by_ids(product_ids, location=location)
        flights = self._graph.find_flights_by_ids(product_ids, route_filter=route)

        results: List[Dict[str, object]] = []
        for hotel in hotels:
            price = self._price_catalog.get(hotel.id)
            results.append(
                {
                    "type": "hotel",
                    "id": hotel.id,
                    "name": hotel.name,
                    "location": hotel.location,
                    "features": [amenity.name for amenity in hotel.amenities],
                    "price_per_night": self._format_price(price),
                    "availability": price.availability if price else "Unknown",
                }
            )

        for flight in flights:
            price = self._price_catalog.get(flight.id)
            result = {
                "type": "flight",
                "id": flight.id,
                "route": flight.route,
                "class": flight.travel_class,
                "features": [service.name for service in flight.services],
                "price": self._format_price(price),
                "availability": price.availability if price else "Unknown",
            }
            result.update(price.extra if price else {})
            results.append(result)

        return {"intent": intent, "results": results}

    # ------------------------------------------------------------------
    def summarize_for_agent(
        self, payload: Dict[str, List[Dict[str, object]]]
    ) -> str:
        """Render a conversational summary similar to what Claude would say."""

        results = payload.get("results", [])
        if not results:
            return "I could not find any options that match that intent right now."

        messages: List[str] = []
        for result in results:
            if result["type"] == "hotel":
                messages.append(
                    "{name} in {location} from {price} per night. Highlights: {features}."
                    .format(
                        name=result["name"],
                        location=result["location"],
                        price=result.get("price_per_night", "Unknown"),
                        features=", ".join(result.get("features", [])) or "None",
                    )
                )
            elif result["type"] == "flight":
                messages.append(
                    "{route} {travel_class} at {price}. Extras: {features}. Next availability: {availability}."
                    .format(
                        route=result["route"],
                        travel_class=result.get("class", ""),
                        price=result.get("price", "Unknown"),
                        features=", ".join(result.get("features", [])) or "None",
                        availability=result.get("availability", "Unknown"),
                    )
                )
        return "Here is what I found: " + " " + " ".join(messages)

    # ------------------------------------------------------------------
    @staticmethod
    def _format_price(quote: Optional[PriceQuote]) -> str:
        if not quote:
            return "Unknown"
        return f"${quote.price:,.0f} {quote.currency}"
