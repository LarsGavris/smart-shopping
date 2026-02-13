from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .repositories import OfferRepository


@dataclass
class OfferQueryWindow:
    from_dt: datetime
    to_dt: datetime


class OfferAnalyticsService:
    """Business-facing APIs for best-current offers and historical trends."""

    def __init__(self, offer_repository: OfferRepository):
        self.offer_repository = offer_repository

    def best_current_offers(self, *, now: datetime, normalized_key: str | None = None, limit: int = 20):
        return self.offer_repository.get_best_current_offers(now=now, normalized_key=normalized_key, limit=limit)

    def historical_trends(self, *, normalized_key: str, window: OfferQueryWindow, bucket: str = "day"):
        return self.offer_repository.get_price_trend(
            normalized_key=normalized_key,
            from_dt=window.from_dt,
            to_dt=window.to_dt,
            bucket=bucket,
        )
