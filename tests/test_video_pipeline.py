"""
Video pipeline tests: the frame loop end-to-end, without Streamlit or the API.

`_process_video` is the hot path that used to be re-executed on every Streamlit
rerun. These tests drive it with a real (tiny) video file and a stubbed backend
response so sampling, capping, persistence and cleanup are verified.
"""

import importlib
import os

import numpy as np
import pytest

video = importlib.import_module("app.ui.video_analysis")


class _DummyElement:
    """Stands in for any Streamlit element (method calls are no-ops)."""

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def __getattr__(self, _name):
        return lambda *args, **kwargs: self


def _fake_columns(spec, **_kwargs):
    count = spec if isinstance(spec, int) else len(spec)
    return [_DummyElement() for _ in range(count)]


class _FakeUpload:
    """Minimal stand-in for a Streamlit UploadedFile."""

    def __init__(self, name: str, data: bytes):
        self.name = name
        self.size = len(data)
        self._data = data

    def read(self):
        return self._data


def _make_video(tmp_path, frames: int = 6, fps: int = 30):
    import cv2

    path = os.path.join(str(tmp_path), "clip.avi")
    writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"MJPG"), float(fps), (64, 64))
    if not writer.isOpened():
        pytest.skip("OpenCV video writer unavailable in this environment")

    for idx in range(frames):
        writer.write(np.full((64, 64, 3), idx * 20 % 255, dtype=np.uint8))
    writer.release()

    with open(path, "rb") as fh:
        return fh.read()


def _api_payload(people: int = 3):
    return {
        "density_label": "MEDIUM",
        "confidence": 0.8,
        "probabilities": {"LOW": 0.1, "MEDIUM": 0.8, "HIGH": 0.1},
        "people_count": people,
        "detections": [
            {"bbox": [5, 5, 40, 60], "confidence": 0.7, "class_id": 0, "person_id": 1}
        ],
        "attributes": [],
        "tracking": True,
        "features": {
            "people_count": people,
            "occupancy_ratio": 0.25,
            "avg_person_area": 0.1,
            "avg_distance": 0.4,
            "min_distance": 0.3,
            "spatial_spread": 0.05,
            "top_region_count": 1,
            "middle_region_count": 1,
            "bottom_region_count": 1,
            "frame_occupancy_density": 0.25,
        },
        "model_name": "Decision Tree",
    }


@pytest.fixture
def stubbed_ui(monkeypatch):
    """Replace the Streamlit UI calls and DB writes used by the frame loop."""
    saved = []

    monkeypatch.setattr(video.st, "progress", lambda *a, **k: _DummyElement())
    monkeypatch.setattr(video.st, "empty", lambda *a, **k: _DummyElement())
    monkeypatch.setattr(video.st, "columns", _fake_columns)
    monkeypatch.setattr(video.st, "session_state", {}, raising=False)
    monkeypatch.setattr(video, "save_analysis_record", lambda **kwargs: saved.append(kwargs))
    return saved


def test_process_video_samples_frames_and_reports_results(tmp_path, monkeypatch, stubbed_ui):
    payload = _api_payload()
    calls = {"n": 0}

    def fake_api(frame, confidence=None, track=False, attributes=False):
        calls["n"] += 1
        calls["confidence"] = confidence
        calls["track"] = track
        return payload

    monkeypatch.setattr(video, "analyze_frame_api", fake_api)

    upload = _FakeUpload("clip.avi", _make_video(tmp_path, frames=6, fps=30))
    results = video._process_video(
        upload,
        sample_interval=2,
        min_confidence=0.35,
        enable_tracking=True,
        crops=(0, 0, 0, 0),
    )

    # 6 frames at a stride of 2 -> frames 0, 2 and 4 are analysed.
    assert results["frame_count"] == 3
    assert calls["n"] == 3
    assert results["error"] is None
    assert results["completed"] is True
    assert results["fps"] == pytest.approx(30.0)
    assert results["people_counts"] == [3, 3, 3]
    assert results["densities"] == ["MEDIUM"] * 3
    assert results["timestamps"] == pytest.approx([0.0, 2 / 30, 4 / 30])
    assert calls["confidence"] == 0.35
    assert calls["track"] is True
    assert results["last_preview"] is not None
    assert results["last_stats"]["active_tracks"] == 1
    assert len(results["previews"]) <= video.MAX_PREVIEWS


def test_process_video_caps_timeline_length(tmp_path, monkeypatch, stubbed_ui):
    monkeypatch.setattr(video, "analyze_frame_api", lambda *a, **k: _api_payload())
    monkeypatch.setattr(video, "MAX_POINTS", 2)

    upload = _FakeUpload("clip.avi", _make_video(tmp_path, frames=10, fps=30))
    results = video._process_video(
        upload,
        sample_interval=1,
        min_confidence=0.3,
        enable_tracking=False,
        crops=(0, 0, 0, 0),
    )

    assert results["frame_count"] == 10
    assert len(results["timestamps"]) == 2, "long videos must not grow unbounded"


def test_process_video_reports_backend_loss_without_raising(tmp_path, monkeypatch, stubbed_ui):
    monkeypatch.setattr(video, "analyze_frame_api", lambda *a, **k: None)

    upload = _FakeUpload("clip.avi", _make_video(tmp_path, frames=4, fps=30))
    results = video._process_video(
        upload,
        sample_interval=1,
        min_confidence=0.3,
        enable_tracking=False,
        crops=(0, 0, 0, 0),
    )

    assert results["completed"] is False
    assert results["error"], "expected an error message"
    assert results["frame_count"] == 0


def test_process_video_rejects_impossible_crops(tmp_path, monkeypatch, stubbed_ui):
    monkeypatch.setattr(video, "analyze_frame_api", lambda *a, **k: _api_payload())

    upload = _FakeUpload("clip.avi", _make_video(tmp_path, frames=2, fps=30))
    results = video._process_video(
        upload,
        sample_interval=1,
        min_confidence=0.3,
        enable_tracking=False,
        crops=(60, 60, 0, 0),  # top and bottom crops overlap
    )

    assert results["completed"] is False
    assert "crop" in results["error"].lower()


def test_process_video_persists_sparsely(tmp_path, monkeypatch, stubbed_ui):
    monkeypatch.setattr(video, "analyze_frame_api", lambda *a, **k: _api_payload())

    upload = _FakeUpload("clip.avi", _make_video(tmp_path, frames=8, fps=30))
    results = video._process_video(
        upload,
        sample_interval=1,
        min_confidence=0.3,
        enable_tracking=False,
        crops=(0, 0, 0, 0),
    )

    assert results["frame_count"] == 8
    # Writes land every DB_SAVE_EVERY sampled frames, not on every frame.
    assert stubbed_ui == []


def test_process_video_reuses_tracking_only_when_enabled(tmp_path, monkeypatch, stubbed_ui):
    seen = []
    monkeypatch.setattr(
        video,
        "analyze_frame_api",
        lambda frame, confidence=None, track=False, attributes=False: (
            seen.append(track) or _api_payload()
        ),
    )

    upload = _FakeUpload("clip.avi", _make_video(tmp_path, frames=2, fps=30))
    video._process_video(
        upload,
        sample_interval=1,
        min_confidence=0.3,
        enable_tracking=False,
        crops=(0, 0, 0, 0),
    )

    assert seen == [False, False], "tracking must be off by default"
    assert all(track is False for track in seen)
