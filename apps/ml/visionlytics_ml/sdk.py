"""
Official Python SDK client for the Visionlytics REST API.
"""
from __future__ import annotations

import base64
import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


class VisionlyticsPythonSDK:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:4000",
        api_key: str | None = None,
        bearer_token: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers: dict[str, str] = {"Content-Type": "application/json"}
        if api_key:
            self.headers["x-api-key"] = api_key
        if bearer_token:
            self.headers["Authorization"] = f"Bearer {bearer_token}"

    def infer_image_file(
        self,
        image_path: str | Path,
        preset: str = "balanced",
        uncertain_threshold: float = 0.50,
        tiled: bool = False,
        open_vocab_query: str | None = None,
    ) -> dict[str, Any]:
        b64 = base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
        payload = json.dumps(
            {
                "imageBase64": b64,
                "preset": preset,
                "uncertainThreshold": uncertain_threshold,
                "tiled": tiled,
                "openVocabQuery": open_vocab_query,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/v1/ml/infer-frame",
            data=payload,
            headers=self.headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))  # type: ignore[no-any-return]

    def search_events(
        self,
        min_people: int | None = None,
        label: str | None = None,
        colour: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, str] = {}
        if min_people is not None:
            params["minPeople"] = str(min_people)
        if label:
            params["label"] = label
        if colour:
            params["colour"] = colour
        qs = urllib.parse.urlencode(params)
        req = urllib.request.Request(
            f"{self.base_url}/v1/events/search?{qs}",
            headers=self.headers,
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))  # type: ignore[no-any-return]
