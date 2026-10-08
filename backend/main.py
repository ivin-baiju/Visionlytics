import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from api.routers import router
from api.data_routers import router as data_router

app = FastAPI(
    title="Visionlytics API",
    description="Backend Microservice for Crowd Analytics",
    version="2.0.0"
)

app.include_router(router)
app.include_router(data_router)

@app.on_event("startup")
async def startup_event():
    # Pre-load ML predictor and YOLO detector in background so first request is instant
    try:
        from api.routers import detector, predictor
        if predictor.is_loaded:
            predictor._load()
        detector.warm_up()
    except Exception as e:
        print(f"[Visionlytics API] Warm-up warning: {e}")

@app.get("/health")
def health_check():
    return {"status": "ok"}
