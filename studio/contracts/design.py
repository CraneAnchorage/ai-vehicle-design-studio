"""Design request/result contracts — the language plugins and core share."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DesignSpec(BaseModel):
    """A single vehicle design spec. Units: millimeters unless noted."""

    name: str
    body_style: str  # sedan | coupe | suv | hypercar | pickup | van | concept
    wheelbase_mm: float = Field(gt=1500, lt=4200)
    length_mm: float = Field(gt=2500, lt=6500)
    width_mm: float = Field(gt=1200, lt=2400)
    height_mm: float = Field(gt=900, lt=2200)
    drag_coefficient: float = Field(gt=0.15, lt=1.2, default=0.32)
    tags: list[str] = Field(default_factory=list)


class DesignRequest(BaseModel):
    prompt: str
    spec: DesignSpec | None = None
    seed: int = 6767
    plugins: list[str] = Field(default_factory=list)


class DesignResult(BaseModel):
    request: DesignRequest
    spec: DesignSpec
    mesh_uri: str
    preview_png: bytes | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def write(self, path: "PathLike") -> None:
        from pathlib import Path

        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.model_dump_json(indent=2))


PathLike = str | "object"