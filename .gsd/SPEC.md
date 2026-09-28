# Visionlytics Specification

**Status: FINALIZED**

## Overview
Visionlytics is an intelligent visual crowd analytics application providing real-time crowd density estimation, YOLOv8-based person detection, Gaussian heatmaps, and machine learning classification.

## Requirements
1. **End-to-End Reliability**: Run both FastAPI backend and Streamlit frontend without runtime crashes, missing modules, or missing weights.
2. **Flat Reference Design**: Replace glassmorphism UI with clean, high-density light-themed design inspired by Ronas IT delivery tracking interface (flat surfaces `#FFFFFF`, hairline borders `#E9EAEC`, solid ink `#14161A`, lime `#B4E04C` accents, pill badges).
3. **Dashboard Structure**: Navigation sidebar as white rail, with an analyses filter panel and detailed cards mirroring the reference design.
4. **Backend & ML Integrity**: Real API endpoints for dataset stats and ML model evaluation, with trained model artifacts tracked.
5. **Testing & Deployment**: Automated verification via pytest / Streamlit AppTest, with Docker Compose and Hugging Face Spaces compatibility.
