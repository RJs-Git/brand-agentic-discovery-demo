"""Event definitions used to connect the demo stages."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class InventoryAddedEvent:
    """Represents the EventBridge notification emitted after Stage 1."""

    item_id: str
    item_name: str
    item_type: Literal["Amenity", "Service"]
    parent_id: str
    parent_type: Literal["Hotel", "Flight"]
    description: Optional[str] = None


class EventBus:
    """A tiny synchronous event bus for the in-memory simulation."""

    def __init__(self) -> None:
        self._subscribers = []

    def subscribe(self, handler) -> None:
        self._subscribers.append(handler)

    def publish(self, event: InventoryAddedEvent) -> None:
        for handler in list(self._subscribers):
            handler(event)
