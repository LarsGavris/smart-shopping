from __future__ import annotations

from dataclasses import asdict
from datetime import datetime

from backend.offers.api import ALERTS, OFFERS


def _emit(channel: str, message: dict) -> None:
    """Pluggable notification emitter."""
    if channel == "email":
        print(f"[EMAIL] {message}")
    elif channel == "push":
        print(f"[PUSH] {message}")
    elif channel == "webhook":
        print(f"[WEBHOOK] {message}")


def evaluate_alerts() -> list[dict]:
    """Evaluate active alert rules against current offers and emit notifications."""
    emissions: list[dict] = []
    now = datetime.utcnow().isoformat()

    active_alerts = [alert for alert in ALERTS if alert.active]
    for alert in active_alerts:
        matching_offers = [
            offer
            for offer in OFFERS
            if offer.product_id == alert.product_id and offer.current_price <= alert.threshold
        ]
        if not matching_offers:
            continue

        best_offer = min(matching_offers, key=lambda offer: offer.current_price)
        message = {
            "alert_id": alert.id,
            "product_id": alert.product_id,
            "threshold": alert.threshold,
            "triggered_price": best_offer.current_price,
            "market": best_offer.market,
            "channel": alert.channel,
            "triggered_at": now,
        }
        _emit(alert.channel, message)
        emissions.append(message)

    return emissions


if __name__ == "__main__":
    results = evaluate_alerts()
    print({"triggered": len(results), "events": [asdict(a) if hasattr(a, "__dataclass_fields__") else a for a in results]})
