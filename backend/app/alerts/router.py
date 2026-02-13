from fastapi import APIRouter

router = APIRouter()


@router.get("")
def get_alerts() -> list[dict[str, str | float]]:
    return [
        {
            "product_id": "milk-1l",
            "target_price": 1.20,
            "channel": "email",
            "active": True,
        }
    ]
