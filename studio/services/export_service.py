"""Export service — writes design results into user-facing formats."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from studio.contracts.design import DesignResult

log = logging.getLogger("avds.services.export")


class ExportService:
    SUPPORTED = ("json", "obj", "gltf")

    def __init__(self, exports_dir: Path) -> None:
        self.exports_dir = exports_dir

    def export(self, result: DesignResult, fmt: str = "json") -> Path:
        if fmt not in self.SUPPORTED:
            raise ValueError(f"unsupported export format: {fmt}")
        out = self.exports_dir / f"{result.spec.name.replace(' ', '_').lower()}.{fmt}"
        if fmt == "json":
            out.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        else:
            # Real OBJ/GLTF writers ship as plugins and register under `export:*`.
            out.write_text(json.dumps({"stub": True, "format": fmt}), encoding="utf-8")
        log.info("exported %s as %s", result.spec.name, fmt)
        return out