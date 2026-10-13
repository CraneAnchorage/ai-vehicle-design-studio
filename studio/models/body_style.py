"""Body style catalog — canonical names and default proportions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BodyStyleProfile:
    name: str
    wheelbase_ratio: float  # wheelbase / length
    height_ratio: float     # height / length
    drag_coefficient: float


BODY_STYLES: dict[str, BodyStyleProfile] = {
    "sedan":    BodyStyleProfile("sedan",    0.62, 0.28, 0.28),
    "coupe":    BodyStyleProfile("coupe",    0.60, 0.24, 0.30),
    "suv":      BodyStyleProfile("suv",      0.58, 0.38, 0.36),
    "hypercar": BodyStyleProfile("hypercar", 0.66, 0.19, 0.32),
    "pickup":   BodyStyleProfile("pickup",   0.60, 0.36, 0.42),
    "van":      BodyStyleProfile("van",      0.55, 0.46, 0.38),
    "concept":  BodyStyleProfile("concept",  0.63, 0.22, 0.26),
}


def get_profile(body_style: str) -> BodyStyleProfile:
    return BODY_STYLES.get(body_style, BODY_STYLES["concept"])