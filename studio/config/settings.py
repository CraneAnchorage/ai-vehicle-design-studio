"""Typed, layered settings. Loads from env, then TOML, then defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import tomli_w


@dataclass(slots=True, frozen=True)
class StudioSettings:
    version: str = "0.4.2"
    plugins_dir: Path = field(default_factory=lambda: Path("plugins"))
    models_dir: Path = field(default_factory=lambda: Path("models_cache"))
    exports_dir: Path = field(default_factory=lambda: Path("exports"))
    log_dir: Path = field(default_factory=lambda: Path("logs"))
    log_level: str = "INFO"
    device: str = "cpu"  # cpu | cuda | directml
    seed: int = 6767

    @classmethod
    def load(
        cls,
        plugins_dir: Path | None = None,
        log_level: str | None = None,
    ) -> "StudioSettings":
        base = cls()
        return cls(
            version=base.version,
            plugins_dir=plugins_dir or Path(os.getenv("AVDS_PLUGINS_DIR", base.plugins_dir)),
            models_dir=Path(os.getenv("AVDS_MODELS_DIR", base.models_dir)),
            exports_dir=Path(os.getenv("AVDS_EXPORTS_DIR", base.exports_dir)),
            log_dir=base.log_dir,
            log_level=log_level or os.getenv("AVDS_LOG_LEVEL", base.log_level),
            device=os.getenv("AVDS_DEVICE", base.device),
            seed=int(os.getenv("AVDS_SEED", base.seed)),
        )

    def dump(self, path: Path) -> None:
        path.write_bytes(
            tomli_w.dumps(
                {
                    "studio": {
                        "version": self.version,
                        "plugins_dir": str(self.plugins_dir),
                        "models_dir": str(self.models_dir),
                        "exports_dir": str(self.exports_dir),
                        "device": self.device,
                        "seed": self.seed,
                    }
                }
            ).encode()
        )