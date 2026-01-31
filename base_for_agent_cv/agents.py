from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Generic, Iterable, TypeVar

from openai import OpenAI
from pydantic import BaseModel

T = TypeVar("T")


@dataclass(frozen=True)
class ModelSettings:
    temperature: float | None = None
    top_p: float | None = None
    max_output_tokens: int | None = None
    response_include: list[str] | None = None

    def resolve(self, override: ModelSettings | None) -> ModelSettings:
        if override is None:
            return self
        return ModelSettings(
            temperature=override.temperature
            if override.temperature is not None
            else self.temperature,
            top_p=override.top_p if override.top_p is not None else self.top_p,
            max_output_tokens=override.max_output_tokens
            if override.max_output_tokens is not None
            else self.max_output_tokens,
            response_include=override.response_include
            if override.response_include is not None
            else self.response_include,
        )


class Tool:
    def to_tool_param(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass(frozen=True)
class FileSearchTool(Tool):
    vector_store_ids: list[str]
    max_num_results: int = 5
    include_search_results: bool = True

    def to_tool_param(self) -> dict[str, Any]:
        return {
            "type": "file_search",
            "vector_store_ids": self.vector_store_ids,
            "max_num_results": self.max_num_results,
        }


@dataclass(frozen=True)
class CodeInterpreterTool(Tool):
    tool_config: dict[str, Any]

    def to_tool_param(self) -> dict[str, Any]:
        return dict(self.tool_config)


@dataclass(frozen=True)
class AgentOutputSchema:
    output_type: type[BaseModel]
    strict_json_schema: bool = True

    @property
    def name(self) -> str:
        return self.output_type.__name__

    def response_format(self) -> dict[str, Any]:
        schema = self.output_type.model_json_schema()
        description = (self.output_type.__doc__ or "").strip()
        payload: dict[str, Any] = {
            "type": "json_schema",
            "name": self.name,
            "schema": schema,
            "strict": self.strict_json_schema,
        }
        if description:
            payload["description"] = description
        return payload


@dataclass(frozen=True)
class Agent(Generic[T]):
    name: str
    instructions: str
    model: str | None = None
    model_settings: ModelSettings | None = None
    tools: list[Tool] | None = None
    output_type: AgentOutputSchema | None = None
    handoff_description: str | None = None


@dataclass(frozen=True)
class RunResult(Generic[T]):
    final_output: T
    response: Any | None = None


class Runner:
    @staticmethod
    async def run(agent: Agent[T], prompt: str | list[dict[str, Any]]) -> RunResult[T]:
        return await asyncio.to_thread(Runner.run_sync, agent, prompt)

    @staticmethod
    def run_sync(agent: Agent[T], prompt: str | list[dict[str, Any]]) -> RunResult[T]:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required to run agents.")

        client = OpenAI()
        request: dict[str, Any] = {
            "model": agent.model,
            "instructions": agent.instructions,
            "input": prompt,
        }
        _apply_model_settings(request, agent.model_settings, agent.tools)

        tools = _serialize_tools(agent.tools)
        if tools:
            request["tools"] = tools

        if agent.output_type is not None:
            request["text"] = {"format": agent.output_type.response_format()}

        response = client.responses.create(**request)
        output_text = response.output_text
        if agent.output_type is not None:
            parsed = _parse_json_output(output_text)
            return RunResult(final_output=parsed, response=response)
        return RunResult(final_output=output_text, response=response)


def _serialize_tools(tools: list[Tool] | None) -> list[dict[str, Any]]:
    if not tools:
        return []
    return [tool.to_tool_param() for tool in tools]


def _apply_model_settings(
    request: dict[str, Any],
    settings: ModelSettings | None,
    tools: list[Tool] | None,
) -> None:
    if settings is None:
        settings = ModelSettings()
    if settings.temperature is not None:
        request["temperature"] = settings.temperature
    if settings.top_p is not None:
        request["top_p"] = settings.top_p
    if settings.max_output_tokens is not None:
        request["max_output_tokens"] = settings.max_output_tokens

    include = list(settings.response_include or [])
    if _needs_file_search_results(tools) and "file_search_call.results" not in include:
        include.append("file_search_call.results")
    if include:
        request["include"] = include


def _needs_file_search_results(tools: list[Tool] | None) -> bool:
    if not tools:
        return False
    return any(isinstance(tool, FileSearchTool) and tool.include_search_results for tool in tools)


def _parse_json_output(output_text: str) -> Any:
    text = output_text.strip()
    if text.startswith("```"):
        text = _strip_code_fence(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        extracted = _extract_json_fragment(text)
        if extracted is None:
            raise
        return json.loads(extracted)


def _strip_code_fence(text: str) -> str:
    lines = text.splitlines()
    if not lines:
        return text
    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _extract_json_fragment(text: str) -> str | None:
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        return text[brace_start : brace_end + 1]
    bracket_start = text.find("[")
    bracket_end = text.rfind("]")
    if bracket_start != -1 and bracket_end != -1 and bracket_end > bracket_start:
        return text[bracket_start : bracket_end + 1]
    return None


__all__ = [
    "Agent",
    "AgentOutputSchema",
    "CodeInterpreterTool",
    "FileSearchTool",
    "ModelSettings",
    "RunResult",
    "Runner",
    "Tool",
]
