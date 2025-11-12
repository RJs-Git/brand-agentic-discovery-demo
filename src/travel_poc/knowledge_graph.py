"""In-memory representation of the travel product knowledge graph."""
from __future__ import annotations

import itertools
from typing import Dict, Iterable, List, Optional

from .models import Amenity, Flight, Hotel, Service


class KnowledgeGraph:
    """Lightweight graph store that mimics the behaviour of Amazon Neptune for the PoC."""

    _amenity_counter = itertools.count(1)
    _service_counter = itertools.count(1)

    def __init__(self, hotels: Iterable[Hotel], flights: Iterable[Flight]) -> None:
        self._hotels: Dict[str, Hotel] = {hotel.id: hotel for hotel in hotels}
        self._flights: Dict[str, Flight] = {flight.id: flight for flight in flights}

    # ------------------------------------------------------------------
    # Mutation helpers (Stage 1)
    # ------------------------------------------------------------------
    def add_hotel_amenity(
        self,
        hotel_id: str,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Amenity:
        """Create a new amenity node attached to a hotel."""

        hotel = self._hotels.get(hotel_id)
        if hotel is None:
            raise KeyError(f"Unknown hotel id: {hotel_id}")

        amenity = Amenity(
            id=f"amenity-{next(self._amenity_counter)}",
            name=name,
            description=description,
            metadata=metadata or {},
        )
        hotel.amenities.append(amenity)
        return amenity

    def add_flight_service(
        self,
        flight_id: str,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Service:
        """Create a new service node attached to a flight route/class."""

        flight = self._flights.get(flight_id)
        if flight is None:
            raise KeyError(f"Unknown flight id: {flight_id}")

        service = Service(
            id=f"service-{next(self._service_counter)}",
            name=name,
            description=description,
            metadata=metadata or {},
        )
        flight.services.append(service)
        return service

    # ------------------------------------------------------------------
    # Query helpers (Stage 2)
    # ------------------------------------------------------------------
    def get_hotel(self, hotel_id: str) -> Hotel:
        return self._hotels[hotel_id]

    def get_flight(self, flight_id: str) -> Flight:
        return self._flights[flight_id]

    def list_hotels(self) -> List[Hotel]:
        return list(self._hotels.values())

    def list_flights(self) -> List[Flight]:
        return list(self._flights.values())

    # ------------------------------------------------------------------
    # Tagging utilities (used by intent catalog updates)
    # ------------------------------------------------------------------
    def add_tag(self, product_id: str, tag: str) -> None:
        if product_id in self._hotels:
            self._hotels[product_id].tags.append(tag)
        elif product_id in self._flights:
            self._flights[product_id].tags.append(tag)
        else:
            raise KeyError(f"Unknown product id: {product_id}")

    def get_tags(self, product_id: str) -> List[str]:
        if product_id in self._hotels:
            return list(self._hotels[product_id].tags)
        if product_id in self._flights:
            return list(self._flights[product_id].tags)
        raise KeyError(f"Unknown product id: {product_id}")

    # ------------------------------------------------------------------
    # Helper lookups for the search service
    # ------------------------------------------------------------------
    def find_hotels_by_ids(self, hotel_ids: Iterable[str], location: Optional[str] = None) -> List[Hotel]:
        hotels = [self._hotels[h_id] for h_id in hotel_ids if h_id in self._hotels]
        if location:
            hotels = [hotel for hotel in hotels if hotel.location.lower() == location.lower()]
        return hotels

    def find_flights_by_ids(self, flight_ids: Iterable[str], route_filter: Optional[str] = None) -> List[Flight]:
        flights = [self._flights[f_id] for f_id in flight_ids if f_id in self._flights]
        if route_filter:
            flights = [flight for flight in flights if flight.route.lower() == route_filter.lower()]
        return flights
