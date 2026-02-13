from fastapi import FastAPI

from backend.offers.api import router as offers_router

app = FastAPI(title="Smart Shopping API")
app.include_router(offers_router)
