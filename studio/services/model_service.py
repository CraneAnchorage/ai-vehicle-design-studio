"""ModelService — loads generator checkpoints from models_cache and runs inference.

Weights are expected as .onnx or .pt files named `generator_<body_style>.<ext>`.
SHA-256 sidecars are required for anything fetched from the network.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any

import numpy as np

log = logging.getLogger("avds.services.model")


class ModelService:
    def __init__(self, models_dir: Path, device: str = "cpu") -> None:
        self.models_dir = models_dir
        self.device = device
        self._cache: dict[str, Any] = {}

    def available(self) -> list[str]:
        if not self.models_dir.is_dir():
            return []
        return sorted(p.stem for p in self.models_dir.glob("generator_*.*"))

    def load(self, body_style: str) -> Any | None:
        if body_style in self._cache:
            return self._cache[body_style]
        candidates = list(self.models_dir.glob(f"generator_{body_style}.*"))
        if not candidates:
            log.info("no checkpoint for body_style=%s, using heuristic generator", body_style)
            return None
        path = candidates[0]
        self._verify_sidecar(path)
        # Real load is deferred to the backend plugin (onnxruntime / torch).
        handle = {"path": str(path), "device": self.device}
        self._cache[body_style] = handle
        return handle

    @staticmethod
    def _verify_sidecar(weights: Path) -> None:
        sidecar = weights.with_suffix(weights.suffix + ".sha256")
        if not sidecar.is_file():
            log.warning("no sha256 sidecar for %s — skipping integrity check", weights)
            return
        expected = sidecar.read_text(encoding="utf-8").split()[0].strip()
        digest = hashlib.sha256(weights.read_bytes()).hexdigest()
        if digest != expected:
            raise RuntimeError(f"checkpoint hash mismatch for {weights}")

    @staticmethod
    def probe_latent(dim: int, seed: int) -> np.ndarray:
        """Deterministic latent for heuristic fallback generators."""
        rng = np.random.default_rng(seed)
        return rng.standard_normal(dim).astype(np.float32)