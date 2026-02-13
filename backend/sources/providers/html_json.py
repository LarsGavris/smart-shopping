from __future__ import annotations

import json
from dataclasses import dataclass, field
from urllib.request import Request, urlopen

from backend.sources.connectors import BaseSourceConnector, DateRange


@dataclass
class HtmlJsonSource(BaseSourceConnector):
    """Connector for HTML pages and JSON APIs."""

    endpoints: list[str] = field(default_factory=list)
    timeout_s: int = 20
    user_agent: str = "smart-shopping-bot/1.0"

    def fetch_raw_offers(self, date_range: DateRange) -> list[dict[str, object]]:
        payloads: list[dict[str, object]] = []
        for endpoint in self.endpoints:
            req = Request(endpoint, headers={"User-Agent": self.user_agent})
            with urlopen(req, timeout=self.timeout_s) as response:
                content_type = response.headers.get("Content-Type", "text/html")
                body = response.read()
                parsed: object
                if "application/json" in content_type:
                    parsed = json.loads(body.decode("utf-8"))
                else:
                    parsed = body.decode("utf-8", errors="replace")

                payloads.append(
                    {
                        "source_url": endpoint,
                        "region": self.region,
                        "market": self.market,
                        "format": self.format,
                        "content_type": content_type,
                        "raw": parsed,
                        "date_range": date_range,
                    }
                )
        return payloads


class CarrefourHtmlSource(HtmlJsonSource):
    def __init__(self, region: str, endpoints: list[str], timeout_s: int = 20) -> None:
        super().__init__(region=region, market="Carrefour", format="html", endpoints=endpoints, timeout_s=timeout_s)


class WalmartJsonSource(HtmlJsonSource):
    def __init__(self, region: str, endpoints: list[str], timeout_s: int = 20) -> None:
        super().__init__(region=region, market="Walmart", format="json", endpoints=endpoints, timeout_s=timeout_s)
