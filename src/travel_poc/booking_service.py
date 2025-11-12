"""Simulated booking API for Stage 5 of the PoC."""
from __future__ import annotations

import random
import string
from dataclasses import dataclass
from typing import Dict, Optional

from .models import PriceQuote


@dataclass
class BookingConfirmation:
    """Represents the ACP confirmation returned to the agent."""

    product_id: str
    confirmation_code: str
    status: str
    pricing: Optional[PriceQuote]
    message: str


class BookingService:
    """Processes mock booking requests and returns confirmations."""

    def __init__(self, price_catalog: Dict[str, PriceQuote]) -> None:
        self._price_catalog = price_catalog
        self.bookings: Dict[str, BookingConfirmation] = {}

    def book(
        self,
        product_id: str,
        user_reference: str,
        stay_or_travel_details: Optional[str] = None,
    ) -> BookingConfirmation:
        confirmation_code = self._generate_confirmation(product_id)
        pricing = self._price_catalog.get(product_id)
        message = self._build_message(product_id, stay_or_travel_details)
        confirmation = BookingConfirmation(
            product_id=product_id,
            confirmation_code=confirmation_code,
            status="CONFIRMED",
            pricing=pricing,
            message=message,
        )
        self.bookings[confirmation_code] = confirmation
        return confirmation

    # ------------------------------------------------------------------
    def _generate_confirmation(self, product_id: str) -> str:
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        prefix = "HTL" if product_id.startswith("hotel") else "FLT"
        return f"{prefix}-{suffix}"

    def _build_message(self, product_id: str, details: Optional[str]) -> str:
        base = "Reservation confirmed" if product_id.startswith("hotel") else "Flight booked"
        if details:
            base += f" for {details}"
        return base + "."
