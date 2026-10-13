"""Helpers to build and validate vehicle specs from partial inputs."""

from __future__ import annotations

from studio.contracts.design import DesignSpec
from studio.models.body_style import get_profile


def spec_from_body_style(
    name: str,
    body_style: str,
    length_mm: float = 4500.0,
    width_mm: float = 1900.0,
    tags: list[str] | None = None,
) -> DesignSpec:
    """Fill in derived dimensions from the body style profile."""
    profile = get_profile(body_style)
    return DesignSpec(
        name=name,
        body_style=body_style,
        wheelbase_mm=round(length_mm * profile.wheelbase_ratio, 1),
        length_mm=length_mm,
        width_mm=width_mm,
        height_mm=round(length_mm * profile.height_ratio, 1),
        drag_coefficient=profile.drag_coefficient,
        tags=tags or [],
    )