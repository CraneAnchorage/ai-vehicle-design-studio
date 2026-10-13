"""Handles a single design prompt end to end, from CLI or UI plugin."""

from __future__ import annotations

import logging
from pathlib import Path

from studio.contracts.design import DesignResult
from studio.core.pipeline import DesignPipeline

log = logging.getLogger("avds.handlers.design")


class DesignHandler:
    def __init__(self, pipeline: DesignPipeline, exports_dir: Path) -> None:
        self.pipeline = pipeline
        self.exports_dir = exports_dir

    def handle(self, prompt: str, out_name: str | None = None) -> Path:
        result: DesignResult = self.pipeline.run(prompt)
        safe = out_name or f"{result.spec.name.replace(' ', '_').lower()}.vdsproj"
        out_path = self.exports_dir / safe
        result.write(out_path)
        log.info("handler wrote %s", out_path)
        return out_path