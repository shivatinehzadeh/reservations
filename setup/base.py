from fastapi import FastAPI

from app import reservation_service

app = FastAPI()
app.include_router(reservation_service.router)
