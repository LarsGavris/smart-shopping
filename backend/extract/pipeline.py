from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable

from backend.extract.normalization import normalize_decimal_separator, normalize_product_name

PRICE_PATTERN = re.compile(
    r"(?P<name>[A-Za-z0-9\s\-,'/%]+?)\s+(?P<price>\d+[\.,]\d{1,2})\s*(?P<currency>€|EUR|\$|USD|£|GBP)\s*(?P<unit>/\w+)?",
    flags=re.IGNORECASE,
)

DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")


@dataclass
class ParsedOffer:
    product_name: str
    price: float
    currency: str
    unit: str | None = None
    valid_from: date | None = None
    valid_to: date | None = None


class OfferExtractionPipeline:
    """Pipeline with OCR, candidate detection, and entity extraction."""

    def ocr_pages(self, payload: dict[str, object]) -> str:
        """OCR step placeholder.

        If text content exists, returns it directly. For bytes payloads this is where OCR
        engine integration (e.g., tesseract/vision API) should be plugged in.
        """

        if isinstance(payload.get("raw"), str):
            return payload["raw"]  # type: ignore[return-value]

        raw_bytes = payload.get("bytes")
        if isinstance(raw_bytes, (bytes, bytearray)):
            return raw_bytes.decode("utf-8", errors="ignore")

        return ""

    def detect_product_line_candidates(self, text: str) -> list[str]:
        return [line.strip() for line in text.splitlines() if PRICE_PATTERN.search(line)]

    def extract_entities(self, lines: Iterable[str]) -> list[ParsedOffer]:
        offers: list[ParsedOffer] = []
        for line in lines:
            match = PRICE_PATTERN.search(line)
            if not match:
                continue

            price_value = normalize_decimal_separator(match.group("price"))
            if price_value is None:
                continue

            date_hits = DATE_PATTERN.findall(line)
            valid_from = self._parse_date(date_hits[0]) if len(date_hits) > 0 else None
            valid_to = self._parse_date(date_hits[1]) if len(date_hits) > 1 else None

            offers.append(
                ParsedOffer(
                    product_name=normalize_product_name(match.group("name")),
                    price=price_value,
                    currency=match.group("currency").upper(),
                    unit=match.group("unit"),
                    valid_from=valid_from,
                    valid_to=valid_to,
                )
            )
        return offers

    def run(self, payload: dict[str, object]) -> list[ParsedOffer]:
        text = self.ocr_pages(payload)
        candidates = self.detect_product_line_candidates(text)
        return self.extract_entities(candidates)

    @staticmethod
    def _parse_date(value: str) -> date | None:
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None
