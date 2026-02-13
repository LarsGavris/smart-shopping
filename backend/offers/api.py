from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


@dataclass
class Offer:
    id: int
    product_id: int
    product_name: str
    market: str
    region: str
    current_price: float
    valid_until: date
    updated_at: datetime


@dataclass
class PricePoint:
    product_id: int
    market: str
    price: float
    captured_at: datetime


class AlertCreate(BaseModel):
    product_id: int
    threshold: float = Field(..., gt=0)
    channel: Literal["email", "push", "webhook"]


class Alert(BaseModel):
    id: int
    product_id: int
    threshold: float
    channel: Literal["email", "push", "webhook"]
    active: bool = True
    created_at: datetime


OFFERS: list[Offer] = [
    Offer(1, 101, "Organic Milk 1L", "FreshMart", "north", 2.49, date.today(), datetime.utcnow()),
    Offer(2, 101, "Organic Milk 1L", "ValueFoods", "north", 2.29, date.today(), datetime.utcnow()),
    Offer(3, 102, "Wholegrain Bread", "FreshMart", "south", 1.99, date.today(), datetime.utcnow()),
    Offer(4, 103, "Free-range Eggs 12pk", "BudgetBuy", "north", 3.59, date.today(), datetime.utcnow()),
]

PRICE_HISTORY: list[PricePoint] = [
    PricePoint(101, "FreshMart", 2.99, datetime.utcnow()),
    PricePoint(101, "FreshMart", 2.79, datetime.utcnow()),
    PricePoint(101, "FreshMart", 2.49, datetime.utcnow()),
    PricePoint(101, "ValueFoods", 2.69, datetime.utcnow()),
    PricePoint(101, "ValueFoods", 2.29, datetime.utcnow()),
    PricePoint(102, "FreshMart", 2.29, datetime.utcnow()),
    PricePoint(102, "FreshMart", 1.99, datetime.utcnow()),
]

ALERTS: list[Alert] = []
NEXT_ALERT_ID = 1


@router.get("/offers")
def get_offers(
    query: str | None = Query(None),
    market: str | None = Query(None),
    max_price: float | None = Query(None, gt=0),
    region: str | None = Query(None),
):
    offers = OFFERS
    if query:
        query_lower = query.lower()
        offers = [o for o in offers if query_lower in o.product_name.lower()]
    if market:
        offers = [o for o in offers if o.market.lower() == market.lower()]
    if max_price is not None:
        offers = [o for o in offers if o.current_price <= max_price]
    if region:
        offers = [o for o in offers if o.region.lower() == region.lower()]

    lowest_price_per_product: dict[int, float] = {}
    for o in offers:
        lowest_price_per_product[o.product_id] = min(lowest_price_per_product.get(o.product_id, o.current_price), o.current_price)

    payload = []
    today = date.today()
    for offer in offers:
        data = asdict(offer)
        data["is_best_price"] = offer.current_price == lowest_price_per_product[offer.product_id]
        data["is_new_today"] = offer.updated_at.date() == today
        payload.append(data)
    return payload


@router.get("/products/{product_id}/history")
def product_history(product_id: int):
    points = [p for p in PRICE_HISTORY if p.product_id == product_id]
    if not points:
        raise HTTPException(status_code=404, detail="Product history not found")

    grouped: dict[str, list[dict]] = {}
    for point in sorted(points, key=lambda p: p.captured_at):
        grouped.setdefault(point.market, []).append(
            {"price": point.price, "captured_at": point.captured_at.isoformat()}
        )

    active_promotions = [asdict(o) for o in OFFERS if o.product_id == product_id]
    return {
        "product_id": product_id,
        "history": grouped,
        "active_promotions": active_promotions,
    }


@router.post("/alerts", response_model=Alert, status_code=201)
def create_alert(payload: AlertCreate):
    global NEXT_ALERT_ID
    alert = Alert(id=NEXT_ALERT_ID, created_at=datetime.utcnow(), **payload.model_dump())
    ALERTS.append(alert)
    NEXT_ALERT_ID += 1
    return alert


@router.get("/alerts", response_model=list[Alert])
def list_alerts():
    return ALERTS


@router.delete("/alerts/{alert_id}", status_code=204)
def delete_alert(alert_id: int):
    idx = next((i for i, alert in enumerate(ALERTS) if alert.id == alert_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    ALERTS.pop(idx)
    return None
