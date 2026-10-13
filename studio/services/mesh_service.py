"""MeshService — turns a DesignSpec into a mesh file on disk.

The default backend is a parametric box/shape builder; heavier backends
(Blender headless, OpenCascade) ship as plugins and register under `mesh:*`.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from studio.contracts.design import DesignSpec

log = logging.getLogger("avds.services.mesh")


class MeshService:
    def __init__(self, exports_dir: Path) -> None:
        self.exports_dir = exports_dir
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def build(self, spec: DesignSpec, seed: int = 6767) -> str:
        """Return a URI/path to the generated mesh. Format: .vdsmesh (JSON)."""
        out = self.exports_dir / f"{spec.name.replace(' ', '_').lower()}.vdsmesh"
        mesh = self._parametric_mesh(spec, seed=seed)
        out.write_text(json.dumps(mesh, indent=2), encoding="utf-8")
        log.info("mesh written: %s (%d verts)", out, len(mesh["vertices"]))
        return str(out)

    @staticmethod
    def _parametric_mesh(spec: DesignSpec, seed: int) -> dict[str, object]:
        # 8-corner bounding box scaled by spec, plus a rough hood/roof profile.
        L, W, H = spec.length_mm, spec.width_mm, spec.height_mm
        half_L, half_W = L / 2, W / 2
        verts = [
            (-half_L, 0.0, -half_W), (half_L, 0.0, -half_W),
            (half_L, 0.0, half_W), (-half_L, 0.0, half_W),
            (-half_L, H * 0.55, -half_W), (half_L * 0.4, H * 0.55, -half_W),
            (half_L * 0.4, H * 0.55, half_W), (-half_L, H * 0.55, half_W),
            (-half_L * 0.1, H, -half_W * 0.85), (half_L * 0.3, H, -half_W * 0.85),
            (half_L * 0.3, H, half_W * 0.85), (-half_L * 0.1, H, half_W * 0.85),
        ]
        return {
            "format": "vdsmesh/1",
            "seed": seed,
            "body_style": spec.body_style,
            "units": "mm",
            "vertices": [list(map(float, v)) for v in verts],
            "metadata": {
                "wheelbase_mm": spec.wheelbase_mm,
                "drag_coefficient": spec.drag_coefficient,
                "tags": spec.tags,
            },
        }