from __future__ import annotations

import asyncio
from collections.abc import Coroutine, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeVar

from agents import Agent, ModelSettings

from .config import (
    resolve_include_results,
    resolve_max_num_results,
    resolve_model,
    resolve_model_settings,
    resolve_vector_store_ids,
    use_assistant_api,
)
from .factory import create_extract_agent, create_render_agent
from .pipeline import (
    ExtractOutput,
    GenerateRequest,
    GenerateResponse,
    extract_facts,
    generate_full_package,
    render_documents,
    revise_package,
)

T = TypeVar("T")


@dataclass(frozen=True)
class SDKConfig:
    model: str | None = None
    vector_store_ids: Sequence[str] | None = None
    max_num_results: int | None = None
    include_search_results: bool | None = None
    model_settings: ModelSettings | None = None
    use_assistant: bool | None = None


class CZCareerArchitectSDK:
    def __init__(self, config: SDKConfig | None = None) -> None:
        resolved = config or SDKConfig()
        self._model = resolved.model or resolve_model()
        self._vector_store_ids = (
            list(resolved.vector_store_ids)
            if resolved.vector_store_ids is not None
            else resolve_vector_store_ids()
        )
        self._max_num_results = (
            resolved.max_num_results
            if resolved.max_num_results is not None
            else resolve_max_num_results()
        )
        self._include_search_results = (
            resolve_include_results()
            if resolved.include_search_results is None
            else resolved.include_search_results
        )
        self._model_settings = resolve_model_settings(resolved.model_settings)
        self._use_assistant = (
            use_assistant_api() if resolved.use_assistant is None else resolved.use_assistant
        )

    @property
    def model(self) -> str:
        return self._model

    @property
    def vector_store_ids(self) -> list[str]:
        return list(self._vector_store_ids)

    @property
    def model_settings(self) -> ModelSettings:
        return self._model_settings

    def create_extract_agent(
        self,
        *,
        instructions: str | None = None,
        output_type: type | None = None,
        strict_json_schema: bool = True,
    ) -> Agent[None]:
        return create_extract_agent(
            instructions=instructions,
            model=self._model,
            model_settings=self._model_settings,
            vector_store_ids=self._vector_store_ids,
            max_num_results=self._max_num_results,
            include_search_results=self._include_search_results,
            output_type=output_type,
            strict_json_schema=strict_json_schema,
        )

    def create_render_agent(self, *, instructions: str | None = None) -> Agent[None]:
        return create_render_agent(
            instructions=instructions,
            model=self._model,
            model_settings=self._model_settings,
        )

    async def extract_facts(self, request: GenerateRequest) -> ExtractOutput:
        agent = self.create_extract_agent(output_type=ExtractOutput, strict_json_schema=False)
        return await extract_facts(request, agent=agent)

    async def render_documents(
        self,
        cv_ssot_json: dict[str, Any],
        request: GenerateRequest,
        *,
        revision_note: str | None = None,
        use_assistant: bool | None = None,
    ) -> tuple[str, str, str]:
        resolved_use_assistant = self._use_assistant if use_assistant is None else use_assistant
        agent = self.create_render_agent()
        return await render_documents(
            cv_ssot_json,
            request,
            revision_note=revision_note,
            use_assistant=resolved_use_assistant,
            render_agent=agent,
        )

    async def generate_full_package(
        self,
        request: GenerateRequest,
        *,
        out_dir: Path = Path("out"),
        use_assistant: bool | None = None,
    ) -> GenerateResponse:
        resolved_use_assistant = self._use_assistant if use_assistant is None else use_assistant
        extract_agent = self.create_extract_agent(
            output_type=ExtractOutput, strict_json_schema=False
        )
        render_agent = self.create_render_agent()
        return await generate_full_package(
            request,
            out_dir=out_dir,
            extract_agent=extract_agent,
            render_agent=render_agent,
            use_assistant=resolved_use_assistant,
        )

    async def revise_package(
        self,
        cv_ssot_json: dict[str, Any],
        request: GenerateRequest,
        revision_note: str,
        *,
        out_dir: Path = Path("out"),
        use_assistant: bool | None = None,
    ) -> GenerateResponse:
        resolved_use_assistant = self._use_assistant if use_assistant is None else use_assistant
        render_agent = self.create_render_agent()
        return await revise_package(
            cv_ssot_json,
            request,
            revision_note,
            out_dir=out_dir,
            render_agent=render_agent,
            use_assistant=resolved_use_assistant,
        )

    def extract_facts_sync(self, request: GenerateRequest) -> ExtractOutput:
        return self._run_sync(self.extract_facts(request))

    def render_documents_sync(
        self,
        cv_ssot_json: dict[str, Any],
        request: GenerateRequest,
        *,
        revision_note: str | None = None,
        use_assistant: bool | None = None,
    ) -> tuple[str, str, str]:
        return self._run_sync(
            self.render_documents(
                cv_ssot_json,
                request,
                revision_note=revision_note,
                use_assistant=use_assistant,
            )
        )

    def generate_full_package_sync(
        self,
        request: GenerateRequest,
        *,
        out_dir: Path = Path("out"),
        use_assistant: bool | None = None,
    ) -> GenerateResponse:
        return self._run_sync(
            self.generate_full_package(
                request,
                out_dir=out_dir,
                use_assistant=use_assistant,
            )
        )

    def revise_package_sync(
        self,
        cv_ssot_json: dict[str, Any],
        request: GenerateRequest,
        revision_note: str,
        *,
        out_dir: Path = Path("out"),
        use_assistant: bool | None = None,
    ) -> GenerateResponse:
        return self._run_sync(
            self.revise_package(
                cv_ssot_json,
                request,
                revision_note,
                out_dir=out_dir,
                use_assistant=use_assistant,
            )
        )

    def _run_sync(self, coro: Coroutine[Any, Any, T]) -> T:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        raise RuntimeError("Use the async SDK methods inside a running event loop.")
