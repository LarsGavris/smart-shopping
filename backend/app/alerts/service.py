"""Reminder and alerting logic for watched products."""

from dataclasses import dataclass


@dataclass(slots=True)
class PriceAlert:
    product_id: str
    target_price: float
    channel: str


def evaluate_alert(alert: PriceAlert, current_price: float) -> bool:
    return current_price <= alert.target_price
