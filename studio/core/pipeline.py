"""DesignPipeline — orchestrates prompt -> spec -> mesh -> export."""

from __future__ import annotations

import logging

from studio.contracts.design import DesignRequest, DesignResult, DesignSpec
from studio.registry.registry import PluginRegistry
from studio.services.mesh_service import MeshService
from studio.services.model_service import ModelService
from studio.utils.prompt_parser import parse_prompt

log = logging.getLogger("avds.pipeline")


class DesignPipeline:
    def __init__(
        self,
        registry: PluginRegistry,
        model_service: ModelService,
        mesh_service: MeshService,
        seed: int = 6767,
    ) -> None:
        self.registry = registry
        self.model_service = model_service
        self.mesh_service = mesh_service
        self.seed = seed

    def run(self, prompt: str) -> DesignResult:
        parsed = parse_prompt(prompt)
        request = DesignRequest(prompt=prompt, spec=parsed.spec, seed=self.seed)
        generator = self.registry.get_generator(parsed.spec.body_style)
        raw_spec = generator(request) if generator else parsed.spec
        spec: DesignSpec = raw_spec if isinstance(raw_spec, DesignSpec) else parsed.spec
        mesh_uri = self.mesh_service.build(spec, seed=self.seed)
        log.info("generated design '%s' -> %s", spec.name, mesh_uri)
        return DesignResult(request=request, spec=spec, mesh_uri=mesh_uri)

    def run_interactive(self) -> None:
        print("avds studio — type a design prompt, or 'quit'")
        while True:
            try:
                prompt = input("design> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if prompt.lower() in {"quit", "exit", ":q"}:
                break
            if not prompt:
                continue
            result = self.run(prompt)
            print(f"  -> {result.spec.name} [{result.spec.body_style}] mesh={result.mesh_uri}")