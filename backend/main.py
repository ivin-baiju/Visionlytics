import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from api.routers import router

app = FastAPI(
    title="Visionlytics API",
    description="Backend Microservice for Crowd Analytics",
    version="2.0.0"
)

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
