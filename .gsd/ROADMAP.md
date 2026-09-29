# Visionlytics Roadmap

## Wave 0: Environment & Repo Hygiene [DONE]
- [x] Create GSD tracking files (SPEC, ROADMAP, STATE)
- [x] Add `scipy` to `backend/pyproject.toml`, `joblib` & `streamlit>=1.63.0` to `frontend/pyproject.toml`
- [x] Add root `requirements.txt`
- [x] Rebuild `.venv` using `/opt/homebrew/bin/python3.14`
- [x] Verify core imports

## Wave 1: Crash-Level Fixes [DONE]
- [x] Fix F821 undefined variable errors across backend/frontend
- [x] Correct relative paths for weights (`yolov8s.pt`, `yolov8s.onnx`) and models
- [x] Fix root `app.py` wrapper
- [x] Validate backend FastAPI startup & health check

## Wave 2: Flat Theme Foundation [DONE]
- [x] Create `frontend/app/components/theme.py` (tokens, badge/card primitives)
- [x] Rewrite `frontend/app/components/styles.py` (eliminate blur, gradients, animations)
- [x] Update `frontend/app/components/icons.py` (currentColor SVGs, flat brand logo)
- [x] Update `frontend/app/components/charts.py` (flat clean Plotly styles)
- [x] Update `.streamlit/config.toml` (remove dark sidebar inversion, apply light palette)

## Wave 3: UI Migration [DONE]
- [x] Migrate `frontend/app/main.py` sidebar to white rail
- [x] Migrate `frontend/app/ui/dashboard.py` to 3-zone layout with analyses panel
- [x] Convert `st.tabs` to `st.segmented_control` where applicable
- [x] Replace inline hex colors with theme tokens in all UI pages

## Wave 4: Dataset & ML Models Backend [CURRENT]
- [ ] Implement `/dataset/*` and `/models/*` endpoints in FastAPI router
- [ ] Ensure model prediction fallback and champion weights are correctly wired
- [ ] Validate live prediction flow

## Wave 5: E2E Verification & Closure
- [ ] Write integration and AppTest tests
- [ ] Validate Docker Compose build and start
- [ ] Capture UI screenshots
- [ ] Final state snapshot & documentation update

