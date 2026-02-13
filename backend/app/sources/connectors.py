"""Source connectors for supermarket integrations."""

from dataclasses import dataclass


@dataclass(slots=True)
class RawSourceOffer:
    source: str
    sku: str
    title: str
    price: float


class SourceConnector:
    """Base connector contract for supermarket providers."""

    source_name: str = "base"

    def fetch_offers(self) -> list[RawSourceOffer]:
        raise NotImplementedError


class ExampleMarketConnector(SourceConnector):
    source_name = "example_market"

    def fetch_offers(self) -> list[RawSourceOffer]:
        return [
            RawSourceOffer(
                source=self.source_name,
                sku="milk-1l",
                title="Semi-skimmed Milk 1L",
                price=1.29,
            )
        ]
