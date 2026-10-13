"""PluginRegistry — discovers plugins on disk, validates manifests, exposes lookups."""

from __future__ import annotations

import importlib.util
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from pydantic import ValidationError

from studio.contracts.plugin import Plugin, PluginManifest

log = logging.getLogger("avds.registry")


@dataclass(slots=True)
class RegistryEntry:
    plugin_id: str
    version: str
    capabilities: list[str]
    path: Path


class PluginRegistry:
    def __init__(self, plugins_dir: Path) -> None:
        self.plugins_dir = plugins_dir
        self._manifests: dict[str, PluginManifest] = {}
        self._plugins: dict[str, Plugin] = {}
        self._generators: dict[str, Any] = {}
        self._exporters: dict[str, Any] = {}

    def __len__(self) -> int:
        return len(self._plugins)

    def describe(self) -> list[RegistryEntry]:
        return [
            RegistryEntry(
                plugin_id=m.plugin_id,
                version=m.version,
                capabilities=[c.value for c in m.capabilities],
                path=self.plugins_dir / m.plugin_id,
            )
            for m in self._manifests.values()
        ]

    def iter_plugins(self) -> Iterator[Plugin]:
        yield from self._plugins.values()

    def add_generator(self, name: str, fn: object) -> None:
        self._generators[name] = fn

    def add_exporter(self, name: str, fn: object) -> None:
        self._exporters[name] = fn

    def get_generator(self, body_style: str) -> Any | None:
        return self._generators.get(body_style) or self._generators.get("*")

    def discover_and_load(self) -> int:
        if not self.plugins_dir.is_dir():
            log.warning("plugins dir not found: %s", self.plugins_dir)
            return 0
        loaded = 0
        for entry in sorted(self.plugins_dir.iterdir()):
            manifest_path = entry / "plugin.toml"
            if not manifest_path.is_file():
                continue
            try:
                manifest = self._load_manifest(manifest_path)
            except (ValidationError, ValueError) as exc:
                log.error("bad manifest in %s: %s", entry, exc)
                continue
            plugin = self._import_plugin(entry, manifest)
            if plugin is None:
                continue
            try:
                plugin.register(self)
            except Exception:  # noqa: BLE001
                log.exception("plugin register failed: %s", manifest.plugin_id)
                continue
            self._manifests[manifest.plugin_id] = manifest
            self._plugins[manifest.plugin_id] = plugin
            loaded += 1
        return loaded

    @staticmethod
    def _load_manifest(path: Path) -> PluginManifest:
        import tomllib

        data = tomllib.loads(path.read_text(encoding="utf-8"))
        return PluginManifest.model_validate(data.get("plugin", data))

    @staticmethod
    def _import_plugin(folder: Path, manifest: PluginManifest) -> Plugin | None:
        module_name, _, attr = manifest.entry.partition(":")
        init_file = folder / "__init__.py"
        if not init_file.is_file():
            log.error("no __init__.py in %s", folder)
            return None
        mod_name = f"avds_plugin_{manifest.plugin_id}"
        spec = importlib.util.spec_from_file_location(
            mod_name, init_file, submodule_search_locations=[str(folder)]
        )
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        factory = getattr(module, attr or "register", None)
        if factory is None:
            log.error("entry attr %s missing in plugin %s", attr, manifest.plugin_id)
            return None
        result = factory()
        if not isinstance(result, Plugin):
            log.error("plugin %s did not return a Plugin", manifest.plugin_id)
            return None
        return result