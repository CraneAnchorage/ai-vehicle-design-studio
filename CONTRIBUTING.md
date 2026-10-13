# Contributing to AI Vehicle Design Studio

Thanks for wanting to help build the future of AI-assisted vehicle design. This repo is a **plugin host** — the core is intentionally small, and most features ship as extensions.

## Ground Rules

1. **Core stays thin.** If your idea can live as a plugin, it lives as a plugin.
2. **Contracts are frozen once merged.** `studio/contracts/` is the API surface every plugin codes against. Breaking changes require a major version bump and a migration note.
3. **Every plugin ships with a manifest.** See `plugins/example_bodykit/plugin.toml` for the reference format.
4. **Tests or it didn't happen.** New service, new model adapter, new loader path — all need a test under `tests/`.

## Dev Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
python -m studio.bootstrap --list-plugins
```

## Plugin Authoring

Place a folder under `plugins/` containing:

- `plugin.toml` — manifest (id, version, entry point, capabilities)
- `__init__.py` — exports `register(registry)` 
- your implementation modules

The host discovers plugins on boot via `studio/registry/registry.py` and validates them against `studio/contracts/plugin.py`.

## Style

- Python 3.12+, `ruff` + `black` + `mypy --strict` on `studio/`
- Type hints everywhere on public surfaces
- No global mutable state outside the registry
- Logging via `studio/utils/logging_bus.py`, never `print`

## PR Flow

1. Fork, branch off `main` as `feat/<short-name>` or `fix/<short-name>`
2. Run `pytest -q && ruff check . && mypy studio`
3. Open PR with a short description and a screenshot of the design canvas if UI changed

## Code of Conduct

Be decent. Critique the code, not the coder.