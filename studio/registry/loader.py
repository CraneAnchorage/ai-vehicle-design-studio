"""Low-level import helpers used by the registry (kept separate for testability)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def load_module_from_path(module_name: str, path: Path) -> ModuleType:
    """Import a module from a file path without polluting sys.path."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_package_from_dir(module_name: str, folder: Path) -> ModuleType:
    """Import a package directory as a module without a package install."""
    init_file = folder / "__init__.py"
    if not init_file.is_file():
        raise ImportError(f"no __init__.py in {folder}")
    spec = importlib.util.spec_from_file_location(
        module_name, init_file, submodule_search_locations=[str(folder)]
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load package from {folder}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module