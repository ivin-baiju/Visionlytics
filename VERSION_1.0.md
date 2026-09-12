# VISIONLYTICS — Version 1.0

## Release: Clean Streamlit Production Baseline

Version 1.0 marks the first cleaned and stabilized release of VISIONLYTICS as a Streamlit-focused computer-vision and statistical machine-learning application.

### Highlights

- Streamlined the repository around the actual application architecture.
- Removed Snowflake-specific launcher/configuration files.
- Removed Docker deployment files that are no longer part of the supported deployment path.
- Removed local development-environment configuration that does not belong in the runtime repository.
- Removed the unused YOLOv8n weight file; YOLOv8s remains the primary detector.
- Fixed the person-detection data model so detections consistently expose class metadata and attributes.
- Added explicit YOLO model-file validation with a clear error when runtime weights are missing.
- Hardened inference-device selection for local CPU/GPU environments.
- Improved repository ignore rules for caches, environments, logs, and generated output.
- Reworked GitHub Actions so CI runs lightweight tracking tests without installing the full application runtime.
- Updated project documentation and repository layout for a clean 1.0 release.

### Runtime

The supported local entrypoint is:

```bash
streamlit run app/main.py
```

The application retains image analysis, video analysis, tracking, browser-camera snapshots, machine-learning prediction, dataset inspection, and model benchmarking.
