"""PluginHost — the runtime that ties registry, pipeline, and services together."""

from __future__ import annotations

import logging

from studio.config.settings import StudioSettings
from studio.core.pipeline import DesignPipeline
from studio.registry.registry import PluginRegistry
from studio.services.mesh_service import MeshService
from studio.services.model_service import ModelService

log = logging.getLogger("avds.host")


class PluginHost:
    """Owns the plugin registry, the generation pipeline, and shared services."""

    def __init__(self, settings: StudioSettings, registry: PluginRegistry) -> None:
        self.settings = settings
        self.registry = registry
        self.model_service = ModelService(settings.models_dir, device=settings.device)
        self.mesh_service = MeshService(settings.exports_dir)
        self.pipeline = DesignPipeline(
            registry=registry,
            model_service=self.model_service,
            mesh_service=self.mesh_service,
            seed=settings.seed,
        )

    def load_extensions(self) -> None:
        loaded = self.registry.discover_and_load()
        log.info("loaded %d plugin(s)", loaded)

    def run(self) -> None:
        """Interactive loop. Real UI lives in a plugin; core just pumps prompts."""
        log.info("avds host running — %d plugin(s)", len(self.registry))
        self.pipeline.run_interactive()

    def shutdown(self) -> None:
        for plugin in self.registry.iter_plugins():
            try:
                plugin.teardown()
            except Exception:  # noqa: BLE001
                log.exception("plugin teardown failed: %s", plugin)