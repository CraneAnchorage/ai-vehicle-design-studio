"""Shared contracts every plugin codes against. Frozen surface."""

from studio.contracts.plugin import Plugin, PluginManifest, PluginCapability
from studio.contracts.design import DesignRequest, DesignResult, DesignSpec

__all__ = [
    "Plugin",
    "PluginManifest",
    "PluginCapability",
    "DesignRequest",
    "DesignResult",
    "DesignSpec",
]