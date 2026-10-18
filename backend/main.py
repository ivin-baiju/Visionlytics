import os
import sys
from contextlib import asynccontextmanager

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import router
from api.data_routers import router as data_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-load ML predictor and YOLO detector so first request is instant
    try:
        from api.routers import get_detector, get_predictor
        _predictor = get_predictor()
        if not _predictor.is_loaded:
            try:
                _predictor._load()
            except FileNotFoundError:
                pass
        try:
            get_detector().warm_up()
        except Exception as warm_err:
            print(f"[Visionlytics API] Detector warm-up skipped: {warm_err}")
    except Exception as e:
        print(f"[Visionlytics API] Warm-up warning: {e}")
    yield


app = FastAPI(
    title="Visionlytics API",
    description="Backend Microservice for Crowd Analytics",
    version="2.0.0",
    lifespan=lifespan,
)

# Enable CORS for Next.js frontend running locally or on Vercel.
# Overridable via ALLOWED_ORIGINS env (comma-separated). Vercel preview
# deployments (*.vercel.app) are allowed by regex so every preview works.
_allowed = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]
if not _allowed:
    _allowed = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://visionlytics-alpha.vercel.app",
    ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(data_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/ready")
def readiness_check():
    """Deeper probe: are model artifacts present on disk?"""
    try:
        from machine_learning.preprocessing import MODELS_DIR
        best = os.path.join(MODELS_DIR, "best_model.joblib")
        scaler = os.path.join(MODELS_DIR, "scaler.joblib")
        ok = os.path.exists(best) and os.path.exists(scaler)
        return {
            "status": "ready" if ok else "degraded",
            "has_best_model": os.path.exists(best),
            "has_scaler": os.path.exists(scaler),
            "models_dir": MODELS_DIR,
        }
    except Exception as exc:
        return {"status": "degraded", "error": str(exc)}


@app.get("/")
def root():
    return {
        "service": "Visionlytics API",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
    }
