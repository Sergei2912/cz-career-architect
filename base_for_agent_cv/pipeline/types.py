"""Pipeline types (foundation).

This module standardizes request/response contracts used by API + CLI.
It is intentionally minimal and additive for PR#1.
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class JobSpec(BaseModel):
    hospital_name: str | None = None
    department: str | None = None
    vacancy_text: str | None = None


class LanguagePrefs(BaseModel):
    documents: str = "cs"  # cs|en
    comments: str = "ru"   # ru|en|cs


class GenerateRequest(BaseModel):
    mode: Literal["full_package", "cv_only", "letter_only"] = "full_package"
    profile_id: str = "hr_review_default"
    job: JobSpec | None = None
    user_input: str = Field(..., description="Free-form intake text")
    language: LanguagePrefs = Field(default_factory=LanguagePrefs)


class QualityReport(BaseModel):
    gdpr_ok: bool | None = None
    csn_typography_ok: bool | None = None
    ats_ok: bool | None = None
    medical_ok: bool | None = None
    schema_ok: bool | None = None
    validator_summary: dict[str, int] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class GenerateResponse(BaseModel):
    analysis_ru: str = ""
    cv_md_cs: str = ""
    cover_letter_cs: str = ""
    cv_ssot_json: dict[str, Any] = Field(default_factory=dict)
    quality: QualityReport = Field(default_factory=QualityReport)
    evidence_map: list[dict[str, Any]] = Field(default_factory=list)
    revision_id: str = ""
