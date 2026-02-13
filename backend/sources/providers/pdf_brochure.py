from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.request import urlopen

from backend.sources.connectors import BaseSourceConnector, DateRange


@dataclass
class PdfBrochureSource(BaseSourceConnector):
    """Connector for PDF-based promotional brochures."""

    brochure_urls: list[str] = field(default_factory=list)
    timeout_s: int = 20

    def fetch_raw_offers(self, date_range: DateRange) -> list[dict[str, Any]]:
        payloads: list[dict[str, Any]] = []
        for url in self.brochure_urls:
            with urlopen(url, timeout=self.timeout_s) as response:
                payloads.append(
                    {
                        "source_url": url,
                        "region": self.region,
                        "market": self.market,
                        "format": self.format,
                        "content_type": response.headers.get("Content-Type", "application/pdf"),
                        "bytes": response.read(),
                        "date_range": date_range,
                    }
                )
        return payloads


class LidlPdfBrochureSource(PdfBrochureSource):
    def __init__(self, region: str, brochure_urls: list[str], timeout_s: int = 20) -> None:
        super().__init__(region=region, market="Lidl", format="pdf", brochure_urls=brochure_urls, timeout_s=timeout_s)


class TescoPdfBrochureSource(PdfBrochureSource):
    def __init__(self, region: str, brochure_urls: list[str], timeout_s: int = 20) -> None:
        super().__init__(region=region, market="Tesco", format="pdf", brochure_urls=brochure_urls, timeout_s=timeout_s)
