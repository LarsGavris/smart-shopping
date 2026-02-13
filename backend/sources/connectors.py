from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class DateRange:
    """Inclusive date interval used by offer source connectors."""

    start: date
    end: date


class SourceConnector(ABC):
    """Contract implemented by supermarket offer source connectors."""

    region: str
    market: str
    format: str

    @abstractmethod
    def fetch_raw_offers(self, date_range: DateRange) -> list[dict[str, Any]]:
        """Retrieve raw offer payloads for a given date range."""


@dataclass
class BaseSourceConnector(SourceConnector):
    """Simple dataclass-backed connector with metadata fields."""

    region: str
    market: str
    format: str

    @abstractmethod
    def fetch_raw_offers(self, date_range: DateRange) -> list[dict[str, Any]]:
        raise NotImplementedError
