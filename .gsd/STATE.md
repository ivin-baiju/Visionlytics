# Visionlytics Session State

## Current Position
- Phase: Wave 3 (UI Migration) — COMPLETED
- Next: Wave 4 (Dataset & ML Models Backend)
- Working Directory: `/Users/ivinbaiju/PRIMUS/Visionlytics`
- Mode: Act

## Environment
- Interpreter: `/opt/homebrew/bin/python3.14` (`.venv` active)
- Host: Darwin arm64
- Backend API: `/analyze/frame` returns HTTP 200 with YOLOv8s ONNX + Decision Tree ML
- FastAPI `/health` returns `{"status":"ok"}`

## Key Decisions
- Glassmorphism UI replaced by Ronas IT delivery tracking design language.
- Sidebar transformed into white rail; Dashboard gains analyses list panel.
- YOLO weights (`yolov8s.onnx`, `yolov8s.pt`) resolved by searching both backend dir and project root.
- ML joblib models resolved via `_resolve_models_dir()` — prefers `backend/models` then `./models` (project root) or `MODELS_DIR` env override.
- `app.py` root wrapper enforces `FRONTEND_DIR` at `sys.path[0]` so `frontend/app` package wins over the local `app.py` module.
- Docker-compose mounts `./models`, `./yolov8s.pt`, `./yolov8s.onnx` into backend container so containerized mode works too.
- `libgl1-mesa-glx` replaced with `libgl1` in both Dockerfiles (removed from newer Debian).

## Wave 1 Verification
- `ruff check --select F821`: All checks passed
- Backend `TestClient`: 200 for `/health` and `/analyze/frame`
- `python app.py`: no exceptions during Streamlit bare-mode boot

## Files Touched in Wave 1
- `app.py` (sys.path ordering to avoid `app.py` shadowing `frontend/app`)
- `backend/api/routers.py` (add `model_name` to `/analyze/frame` response)
- `backend/computer_vision/person_detection.py` (multi-candidate YOLO weight paths)
- `backend/machine_learning/preprocessing.py` (`_resolve_models_dir()` helper)
- `backend/pyproject.toml` (added `onnx`, `onnxruntime`)
- `backend/Dockerfile` (`libgl1-mesa-glx` -> `libgl1`)
- `frontend/Dockerfile` (same)
- `frontend/app/ui/image_analysis.py` (measure `detection_time`; use `api_response["model_name"]`)
- `frontend/app/ui/live_camera.py` (added missing `save_analysis_record`, `get_detector`, `get_extractor`, `get_predictor` imports)
- `frontend/app/ui/video_analysis.py` (added `save_analysis_record`, `draw_boxes` imports; switched `detector.draw_detections` -> `draw_boxes` and dict-key access for tracking overlays)
- `docker-compose.yml` (mount `models` + YOLO weights into backend; drop deprecated `version`)

