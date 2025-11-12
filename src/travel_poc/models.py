"""Domain models for the travel agent PoC demo."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Amenity:
    """Representation of a hotel amenity within the knowledge graph."""

    id: str
    name: str
    description: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class Service:
    """Representation of an airline service add-on within the knowledge graph."""

    id: str
    name: str
    description: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class Hotel:
    """Simplified hotel node stored in the knowledge graph."""

    id: str
    name: str
    location: str
    amenities: List[Amenity] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class Flight:
    """Simplified flight route/class node stored in the knowledge graph."""

    id: str
    route: str
    travel_class: str
    services: List[Service] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class PriceQuote:
    """Price and availability information returned to the agent."""

    product_id: str
    price: float
    currency: str
    availability: str
    extra: Dict[str, str] = field(default_factory=dict)
