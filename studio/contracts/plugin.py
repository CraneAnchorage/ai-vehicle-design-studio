"""Plugin contract. Any extension module must implement `Plugin`."""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class PluginCapability(StrEnum):
    NETWORK = "network"
    PROCESS = "process"
    FILESYSTEM = "filesystem"
    GPU = "gpu"


class PluginManifest(BaseModel):
    """Parsed from plugin.toml. Validated at load time."""

    plugin_id: str = Field(pattern=r"^[a-z][a-z0-9_]{2,39}$")
    version: str
    display_name: str
    author: str
    entry: str = "plugin:register"
    capabilities: list[PluginCapability] = Field(default_factory=list)
    provides: list[str] = Field(default_factory=list)
    requires_studio: str = ">=0.4.0"


@runtime_checkable
class Plugin(Protocol):
    """Every plugin implements `register` and optionally `teardown`."""

    manifest: PluginManifest

    def register(self, registry: "PluginRegistryLike") -> None: ...

    def teardown(self) -> None: ...


class PluginRegistryLike(Protocol):
    def add_generator(self, name: str, fn: object) -> None: ...
    def add_exporter(self, name: str, fn: object) -> None: ...