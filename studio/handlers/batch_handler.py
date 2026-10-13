"""Batch handler — run a list of prompts from a text file, one design per line."""

from __future__ import annotations

import logging
from pathlib import Path

from studio.handlers.design_handler import DesignHandler

log = logging.getLogger("avds.handlers.batch")


class BatchHandler:
    def __init__(self, design_handler: DesignHandler) -> None:
        self.design_handler = design_handler

    def run_file(self, prompt_file: Path, out_dir: Path) -> list[Path]:
        out_dir.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        for i, line in enumerate(prompt_file.read_text(encoding="utf-8").splitlines(), 1):
            prompt = line.strip()
            if not prompt or prompt.startswith("#"):
                continue
            try:
                out = self.design_handler.handle(prompt, out_name=f"batch_{i:03d}.vdsproj")
            except Exception:  # noqa: BLE001
                log.exception("batch item %d failed: %s", i, prompt)
                continue
            written.append(out)
        return written