"""
CZ Career Architect - Configuration
Version: 1.2.2
Updated: 2026-01-26
"""

from __future__ import annotations

import os
from pathlib import Path

from agents import ModelSettings

VERSION = "2.0.0"

# Directories
ROOT_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = ROOT_DIR / "packages" / "prompts"
TYPES_DIR = ROOT_DIR / "packages" / "types"
VALIDATORS_DIR = ROOT_DIR / "packages" / "validators"
SCHEMAS_DIR = ROOT_DIR / "Schemas"
OUT_DIR = ROOT_DIR / "out"

# File paths
SYSTEM_PROMPT_PATH = PROMPTS_DIR / "system_v1.txt"
EXTRACT_PROMPT_PATH = PROMPTS_DIR / "extract_facts_v1.txt"
SSOT_SCHEMA_PATH = TYPES_DIR / "cz_dentist_cv_gov_ats_gdpr_csn_v1.1.0.schema.json"
VALIDATOR_SCRIPT_PATH = VALIDATORS_DIR / "cz_cv_validator_adapter.py"

# Default values
DEFAULT_MODEL = "gpt-5.2"
DEFAULT_VECTOR_STORE_ID = "vs_697776db24488191bf2f9bf0528d2845"
DEFAULT_ASSISTANT_ID = "asst_fdpLEm4Rp5GlrU7ZOCvl6XZc"
DEFAULT_USE_ASSISTANT_API = False
DEFAULT_MAX_NUM_RESULTS = 5
DEFAULT_INCLUDE_RESULTS = True

# Environment variable names
ENV_MODEL = "OPENAI_MODEL"
ENV_VECTOR_STORE_ID = "OPENAI_VECTOR_STORE_ID"
ENV_COMPLIANCE_VECTOR_STORE_ID = "OPENAI_COMPLIANCE_VECTOR_STORE_ID"
ENV_ASSISTANT_ID = "OPENAI_ASSISTANT_ID"
ENV_USE_ASSISTANT_API = "USE_ASSISTANT_API"
ENV_MAX_NUM_RESULTS = "MAX_NUM_RESULTS"
ENV_INCLUDE_RESULTS = "ENABLE_INCLUDE_RESULTS"

DEFAULT_MODEL_SETTINGS = ModelSettings(response_include=["file_search_call.results"])


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def resolve_model() -> str:
    return os.getenv(ENV_MODEL, DEFAULT_MODEL)


def resolve_vector_store_ids() -> list[str]:
    ids = [os.getenv(ENV_VECTOR_STORE_ID, DEFAULT_VECTOR_STORE_ID)]
    if compliance_id := os.getenv(ENV_COMPLIANCE_VECTOR_STORE_ID):
        ids.append(compliance_id)
    return ids


def resolve_assistant_id() -> str:
    return os.getenv(ENV_ASSISTANT_ID, DEFAULT_ASSISTANT_ID)


def resolve_assistant_vector_store_id() -> str | None:
    ids = resolve_vector_store_ids()
    return ids[0] if ids else None


def use_assistant_api() -> bool:
    return _env_bool(ENV_USE_ASSISTANT_API, DEFAULT_USE_ASSISTANT_API)


def resolve_max_num_results() -> int:
    raw = os.getenv(ENV_MAX_NUM_RESULTS)
    if raw is None:
        return DEFAULT_MAX_NUM_RESULTS
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_MAX_NUM_RESULTS


def resolve_include_results() -> bool:
    return _env_bool(ENV_INCLUDE_RESULTS, DEFAULT_INCLUDE_RESULTS)


def resolve_model_settings(override: ModelSettings | None = None) -> ModelSettings:
    if override is None:
        return DEFAULT_MODEL_SETTINGS
    return DEFAULT_MODEL_SETTINGS.resolve(override)


def ensure_out_dir() -> Path:
    OUT_DIR.mkdir(exist_ok=True)
    return OUT_DIR


def get_version() -> str:
    return VERSION
