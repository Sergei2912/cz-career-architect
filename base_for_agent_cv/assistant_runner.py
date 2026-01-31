from __future__ import annotations

import asyncio

from openai import OpenAI

from .config import resolve_assistant_id, resolve_assistant_vector_store_id


def _extract_text_blocks(message: object) -> str:
    parts: list[str] = []
    content = getattr(message, "content", None) or []
    for block in content:
        if getattr(block, "type", None) != "text":
            continue
        text = getattr(block, "text", None)
        value = getattr(text, "value", None)
        if value:
            parts.append(value)
    return "\n".join(parts).strip()


def run_assistant_sync(
    prompt: str,
    *,
    assistant_id: str | None = None,
    vector_store_id: str | None = None,
    additional_instructions: str | None = None,
) -> str:
    client = OpenAI()
    resolved_assistant_id = assistant_id or resolve_assistant_id()
    if not resolved_assistant_id:
        raise ValueError("OPENAI_ASSISTANT_ID is not set.")

    resolved_vector_store_id = vector_store_id or resolve_assistant_vector_store_id()
    extra_body = None
    if resolved_vector_store_id:
        extra_body = {
            "tool_resources": {
                "file_search": {"vector_store_ids": [resolved_vector_store_id]},
            }
        }

    thread = client.beta.threads.create(messages=[{"role": "user", "content": prompt}])
    run_kwargs: dict[str, object] = {}
    if additional_instructions:
        run_kwargs["additional_instructions"] = additional_instructions
    if extra_body:
        run_kwargs["extra_body"] = extra_body

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=resolved_assistant_id,
        **run_kwargs,
    )
    if run.status != "completed":
        raise RuntimeError(f"Assistant run failed with status: {run.status}")

    messages = client.beta.threads.messages.list(thread_id=thread.id, order="desc")
    for message in messages.data:
        if getattr(message, "role", None) != "assistant":
            continue
        text = _extract_text_blocks(message)
        if text:
            return text
    raise ValueError("Assistant produced no output.")


async def run_assistant(
    prompt: str,
    *,
    assistant_id: str | None = None,
    vector_store_id: str | None = None,
    additional_instructions: str | None = None,
) -> str:
    return await asyncio.to_thread(
        run_assistant_sync,
        prompt,
        assistant_id=assistant_id,
        vector_store_id=vector_store_id,
        additional_instructions=additional_instructions,
    )
