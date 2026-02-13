"""Data normalization and parsing utilities."""

from dataclasses import dataclass

from app.sources.connectors import RawSourceOffer


@dataclass(slots=True)
class NormalizedOffer:
    product_id: str
    name: str
    current_price: float
    source: str


def normalize_offer(raw_offer: RawSourceOffer) -> NormalizedOffer:
    return NormalizedOffer(
        product_id=raw_offer.sku.strip().lower(),
        name=raw_offer.title.strip(),
        current_price=round(raw_offer.price, 2),
        source=raw_offer.source,
    )
