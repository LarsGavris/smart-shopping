from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.request import urlopen

from backend.sources.connectors import BaseSourceConnector, DateRange


@dataclass
class ImageFlyerSource(BaseSourceConnector):
    """Connector for image-based promotional flyers."""

    flyer_urls: list[str] = field(default_factory=list)
    timeout_s: int = 20

    def fetch_raw_offers(self, date_range: DateRange) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for url in self.flyer_urls:
            with urlopen(url, timeout=self.timeout_s) as response:
                items.append(
                    {
                        "source_url": url,
                        "region": self.region,
                        "market": self.market,
                        "format": self.format,
                        "content_type": response.headers.get("Content-Type", "image/*"),
                        "bytes": response.read(),
                        "date_range": date_range,
                    }
                )
        return items


class AldiImageFlyerSource(ImageFlyerSource):
    def __init__(self, region: str, flyer_urls: list[str], timeout_s: int = 20) -> None:
        super().__init__(region=region, market="Aldi", format="image", flyer_urls=flyer_urls, timeout_s=timeout_s)


class SparImageFlyerSource(ImageFlyerSource):
    def __init__(self, region: str, flyer_urls: list[str], timeout_s: int = 20) -> None:
        super().__init__(region=region, market="SPAR", format="image", flyer_urls=flyer_urls, timeout_s=timeout_s)
