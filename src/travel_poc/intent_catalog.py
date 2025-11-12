"""Intent catalog management for Stage 3 of the PoC."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Set

from .events import InventoryAddedEvent
from .knowledge_graph import KnowledgeGraph


class IntentCatalog:
    """Simple in-memory substitute for a DynamoDB backed intent catalog."""

    def __init__(self, seeds: Dict[str, Iterable[str]] | None = None) -> None:
        self._store: Dict[str, Set[str]] = {
            intent: set(items) for intent, items in (seeds or {}).items()
        }

    def add_product(self, intent: str, product_id: str) -> None:
        self._store.setdefault(intent, set()).add(product_id)

    def list_products(self, intent: str) -> List[str]:
        return sorted(self._store.get(intent, []))

    def snapshot(self) -> Dict[str, List[str]]:
        return {intent: sorted(values) for intent, values in self._store.items()}


@dataclass
class IntentCatalogUpdater:
    """Rules-based mapper that reacts to `InventoryAddedEvent` notifications."""

    catalog: IntentCatalog
    graph: KnowledgeGraph
    classification_rules: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "kids' club": ["FamilyVacation"],
            "ride app pickup": ["BusinessTrip", "SeamlessJourney"],
            "lounge access": ["BusinessTrip"],
        }
    )
    activity_log: List[str] = field(default_factory=list)

    def __call__(self, event: InventoryAddedEvent) -> None:
        intents = self._classify(event.item_name)
        if not intents:
            self.activity_log.append(
                f"No intent classification found for {event.item_name}."
            )
            return

        for intent in intents:
            self.catalog.add_product(intent, event.parent_id)
            self.graph.add_tag(event.parent_id, intent)
            self.activity_log.append(
                f"Mapped {event.item_name} ({event.item_type}) to intent {intent}."
            )

        # Optional bundle note for storytelling
        if "FamilyVacation" in intents and event.parent_type == "Hotel":
            self.activity_log.append(
                f"Updated Family Fun package definitions to include {event.parent_id}."
            )
        if "SeamlessJourney" in intents and event.parent_type == "Flight":
            self.activity_log.append(
                f"Flagged {event.parent_id} for seamless journey bundle refresh."
            )

    # ------------------------------------------------------------------
    def _classify(self, item_name: str) -> List[str]:
        key = item_name.lower()
        return self.classification_rules.get(key, [])
