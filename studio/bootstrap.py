"""Entry point. Boots the plugin host, loads extensions, starts the CLI/TUI loop."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import typer
from rich.console import Console

from studio.config.settings import StudioSettings
from studio.core.host import PluginHost
from studio.registry.registry import PluginRegistry
from studio.utils.logging_bus import configure_logging

app = typer.Typer(
    name="avds",
    help="AI Vehicle Design Studio — plugin-host vehicle design generator.",
    no_args_is_help=True,
)
console = Console()


def _bootstrap(settings: StudioSettings) -> PluginHost:
    configure_logging(settings.log_level, settings.log_dir)
    registry = PluginRegistry(settings.plugins_dir)
    host = PluginHost(settings=settings, registry=registry)
    host.load_extensions()
    return host


@app.command()
def run(
    plugins_dir: Path | None = typer.Option(None, "--plugins-dir", help="Override plugin folder."),
    log_level: str = typer.Option("INFO", "--log-level"),
) -> None:
    """Start the studio host with all discovered plugins loaded."""
    settings = StudioSettings.load(plugins_dir=plugins_dir, log_level=log_level)
    host = _bootstrap(settings)
    console.print(f"[bold green]avds[/] v{settings.version} — {len(host.registry)} plugin(s) loaded")
    host.run()


@app.command("list-plugins")
def list_plugins(plugins_dir: Path | None = typer.Option(None, "--plugins-dir")) -> None:
    """List discovered plugins and their declared capabilities."""
    settings = StudioSettings.load(plugins_dir=plugins_dir)
    host = _bootstrap(settings)
    for entry in host.registry.describe():
        console.print(f"  [cyan]{entry.plugin_id}[/] v{entry.version} — {entry.capabilities}")


@app.command("generate")
def generate(
    prompt: str = typer.Argument(..., help="Design prompt, e.g. 'mid-engine hypercar, 1970s wedge'"),
    out: Path = typer.Option(Path("exports/design.vdsproj"), "--out", "-o"),
) -> None:
    """Run the full generation pipeline for a single design prompt."""
    settings = StudioSettings.load()
    host = _bootstrap(settings)
    result = host.pipeline.run(prompt)
    result.write(out)
    console.print(f"[bold green]wrote[/] {out}")


def main() -> None:
    try:
        app()
    except KeyboardInterrupt:
        logging.getLogger("avds").info("interrupted by user")
        sys.exit(130)


if __name__ == "__main__":
    main()