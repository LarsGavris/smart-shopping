"""Business logic for retrieving and composing offers."""

from app.extract.normalize import NormalizedOffer, normalize_offer
from app.sources.connectors import ExampleMarketConnector


def list_offers() -> list[NormalizedOffer]:
    connector = ExampleMarketConnector()
    return [normalize_offer(raw_offer) for raw_offer in connector.fetch_offers()]
