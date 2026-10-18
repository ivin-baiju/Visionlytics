import os
import sys
from contextlib import asynccontextmanager

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from api.routers import router
from api.data_routers import router as data_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-load ML predictor and YOLO detector so first request is instant
    try:
        from api.routers import detector, predictor
        if not predictor.is_loaded:
            predictor._load()
        detector.warm_up()
    except Exception as e:
        print(f"[Visionlytics API] Warm-up warning: {e}")
    yield


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Visionlytics API",
    description="Backend Microservice for Crowd Analytics",
    version="2.0.0",
    lifespan=lifespan,
)

# Enable CORS for Next.js frontend running locally or on Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(data_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
