from __future__ import annotations

from collections.abc import Sequence

from openai.types.responses.tool_param import CodeInterpreter

from agents import (
    Agent,
    AgentOutputSchema,
    CodeInterpreterTool,
    FileSearchTool,
    ModelSettings,
    Tool,
)

from .config import (
    resolve_include_results,
    resolve_max_num_results,
    resolve_model,
    resolve_model_settings,
    resolve_vector_store_ids,
)
from .prompts import load_extract_prompt, load_system_prompt


def _build_tools(
    vector_store_ids: Sequence[str],
    max_num_results: int,
    include_search_results: bool,
    *,
    include_code_interpreter: bool,
) -> list[Tool]:
    tools: list[Tool] = [
        FileSearchTool(
            vector_store_ids=list(vector_store_ids),
            max_num_results=max_num_results,
            include_search_results=include_search_results,
        )
    ]
    if include_code_interpreter:
        tools.append(
            CodeInterpreterTool(
                tool_config=CodeInterpreter(type="code_interpreter", container={"type": "auto"})
            )
        )
    return tools


def create_extract_agent(
    *,
    instructions: str | None = None,
    model: str | None = None,
    model_settings: ModelSettings | None = None,
    vector_store_ids: Sequence[str] | None = None,
    max_num_results: int | None = None,
    include_search_results: bool | None = None,
    output_type: type | None = None,
    strict_json_schema: bool = True,
) -> Agent[None]:
    resolved_instructions = instructions or load_extract_prompt()
    resolved_model = model or resolve_model()
    resolved_model_settings = resolve_model_settings(model_settings)
    resolved_vector_store_ids = (
        list(vector_store_ids) if vector_store_ids is not None else resolve_vector_store_ids()
    )
    resolved_max_results = max_num_results or resolve_max_num_results()
    resolved_include_results = (
        resolve_include_results() if include_search_results is None else include_search_results
    )

    tools = _build_tools(
        resolved_vector_store_ids,
        resolved_max_results,
        resolved_include_results,
        include_code_interpreter=True,
    )

    resolved_output_type = None
    if output_type is not None:
        resolved_output_type = AgentOutputSchema(output_type, strict_json_schema=strict_json_schema)

    return Agent(
        name="CZ Medical Career Architect (Extract)",
        handoff_description="Extracts SSOT facts with evidence map.",
        instructions=resolved_instructions,
        model=resolved_model,
        model_settings=resolved_model_settings,
        tools=tools,
        output_type=resolved_output_type,
    )


def create_render_agent(
    *,
    instructions: str | None = None,
    model: str | None = None,
    model_settings: ModelSettings | None = None,
) -> Agent[None]:
    resolved_instructions = instructions or load_system_prompt()
    resolved_model = model or resolve_model()
    resolved_model_settings = resolve_model_settings(model_settings)

    return Agent(
        name="CZ Medical Career Architect (Render)",
        handoff_description="Renders CZ CV + cover letter from SSOT JSON.",
        instructions=resolved_instructions,
        model=resolved_model,
        model_settings=resolved_model_settings,
        tools=[
            CodeInterpreterTool(
                tool_config=CodeInterpreter(type="code_interpreter", container={"type": "auto"})
            )
        ],
    )
