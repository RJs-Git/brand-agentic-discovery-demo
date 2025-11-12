"""Inventory ingestion stage of the PoC."""
from __future__ import annotations

from typing import Optional

from .events import EventBus, InventoryAddedEvent
from .knowledge_graph import KnowledgeGraph


class InventoryManager:
    """Handles Stage 1: adding new inventory into the knowledge graph."""

    def __init__(self, graph: KnowledgeGraph, event_bus: EventBus) -> None:
        self._graph = graph
        self._event_bus = event_bus

    def add_hotel_amenity(
        self,
        hotel_id: str,
        name: str,
        description: Optional[str] = None,
    ) -> InventoryAddedEvent:
        amenity = self._graph.add_hotel_amenity(
            hotel_id=hotel_id,
            name=name,
            description=description,
        )
        event = InventoryAddedEvent(
            item_id=amenity.id,
            item_name=amenity.name,
            item_type="Amenity",
            parent_id=hotel_id,
            parent_type="Hotel",
            description=description,
        )
        self._event_bus.publish(event)
        return event

    def add_flight_service(
        self,
        flight_id: str,
        name: str,
        description: Optional[str] = None,
    ) -> InventoryAddedEvent:
        service = self._graph.add_flight_service(
            flight_id=flight_id,
            name=name,
            description=description,
        )
        event = InventoryAddedEvent(
            item_id=service.id,
            item_name=service.name,
            item_type="Service",
            parent_id=flight_id,
            parent_type="Flight",
            description=description,
        )
        self._event_bus.publish(event)
        return event
