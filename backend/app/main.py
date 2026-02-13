from fastapi import FastAPI

from app.alerts.router import router as alerts_router
from app.offers.router import router as offers_router

app = FastAPI(title="Smart Shopping API", version="0.1.0")


@app.get("/health", tags=["system"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(offers_router, prefix="/offers", tags=["offers"])
app.include_router(alerts_router, prefix="/alerts", tags=["alerts"])
