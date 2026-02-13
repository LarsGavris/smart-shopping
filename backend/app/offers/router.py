from fastapi import APIRouter

from app.offers.service import list_offers

router = APIRouter()


@router.get("")
def get_offers() -> list[dict[str, str | float]]:
    offers = list_offers()
    return [
        {
            "product_id": offer.product_id,
            "name": offer.name,
            "current_price": offer.current_price,
            "source": offer.source,
        }
        for offer in offers
    ]
