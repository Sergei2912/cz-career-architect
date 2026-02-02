from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from agents import Agent, Runner
from packages.validators import cz_cv_validator_adapter as validator

from .assistant_runner import run_assistant
from .config import SSOT_SCHEMA_PATH, use_assistant_api
from .factory import create_extract_agent, create_render_agent


class EvidenceSource(BaseModel):
    file_id: str
    quote: str
    location: str | None = None


class EvidenceItem(BaseModel):
    claim: str
    source: EvidenceSource


class ExtractOutput(BaseModel):
    cv_ssot_json: dict[str, Any]
    evidence_map: list[EvidenceItem] = Field(default_factory=list)


class QualityReport(BaseModel):
    gdpr_ok: bool
    csn_typography_ok: bool
    anti_hallucination_ok: bool
    schema_ok: bool
    validator_summary: dict[str, int]
    reports: dict[str, str]
    notes: list[str] = Field(default_factory=list)


class GenerateResponse(BaseModel):
    analysis_ru: str
    cv_md_cs: str
    cover_letter_cs: str
    cv_ssot_json: dict[str, Any]
    quality: QualityReport
    evidence_map: list[EvidenceItem] = Field(default_factory=list)
    revision_id: str


class JobSpec(BaseModel):
    hospital_name: str | None = None
    department: str | None = None
    vacancy_text: str | None = None


class Preferences(BaseModel):
    tone: str | None = None
    include_photo_note: bool | None = None


class LanguagePrefs(BaseModel):
    documents: str = "cs"
    comments: str = "ru"


class GenerateRequest(BaseModel):
    mode: Literal["full_package", "cv_only", "letter_only"] = "full_package"
    job: JobSpec | None = None
    preferences: Preferences | None = None
    language: LanguagePrefs = Field(default_factory=LanguagePrefs)


SECTION_PATTERNS = {
    "analysis": re.compile(r"^###\s*RU\s*:\s*Profile Analysis\s*$", re.IGNORECASE),
    "cv": re.compile(r"^###\s*CZ\s*:\s*CV\s*$", re.IGNORECASE),
    "letter": re.compile(r"^###\s*CZ\s*:\s*Motiva(?:ční|cni)\s*dopis\s*$", re.IGNORECASE),
}


def _build_extract_prompt(request: GenerateRequest) -> str:
    parts = ["Extract facts for a public-sector dentist application."]
    if request.job and request.job.vacancy_text:
        parts.append("Vacancy text:")
        parts.append(request.job.vacancy_text)
    if request.job and request.job.hospital_name:
        parts.append(f"Hospital: {request.job.hospital_name}")
    if request.job and request.job.department:
        parts.append(f"Department: {request.job.department}")
    return "\n".join(parts)


def _build_render_prompt(
    cv_ssot_json: dict[str, Any],
    request: GenerateRequest,
    revision_note: str | None = None,
) -> str:
    instructions = [
        "Render documents strictly from the provided cv_ssot_json. Do not add new facts.",
        "Use the following explicit section headers so the backend can split output:",
        "### RU: Profile Analysis",
        "### CZ: CV",
        "### CZ: Motivačni dopis",
    ]
    if request.job and request.job.vacancy_text:
        instructions.append("Tailor to this vacancy text:")
        instructions.append(request.job.vacancy_text)
    if request.job and request.job.hospital_name:
        instructions.append(f"Target hospital: {request.job.hospital_name}")
    if request.job and request.job.department:
        instructions.append(f"Target department: {request.job.department}")
    if revision_note:
        instructions.append("Revision instructions:")
        instructions.append(revision_note)
    payload = json.dumps(cv_ssot_json, ensure_ascii=False)
    instructions.append("cv_ssot_json:")
    instructions.append(payload)
    return "\n".join(instructions)


def _split_sections(text: str) -> tuple[str, str, str]:
    analysis = []
    cv = []
    letter = []
    current: list[str] | None = None
    for line in text.splitlines():
        if SECTION_PATTERNS["analysis"].match(line.strip()):
            current = analysis
            continue
        if SECTION_PATTERNS["cv"].match(line.strip()):
            current = cv
            continue
        if SECTION_PATTERNS["letter"].match(line.strip()):
            current = letter
            continue
        if current is not None:
            current.append(line)
    analysis_text = "\n".join(analysis).strip()
    cv_text = "\n".join(cv).strip()
    letter_text = "\n".join(letter).strip()
    if not any([analysis_text, cv_text, letter_text]):
        return (text.strip(), "", "")
    return (analysis_text, cv_text, letter_text)


def _findings_to_quality(findings: list[validator.Finding]) -> QualityReport:
    summary = validator.build_summary(findings)
    gdpr_ok = not any(item.code.startswith("GDPR") for item in findings)
    csn_ok = not any(item.code.startswith("CSN") for item in findings)
    schema_ok = not any(item.code.startswith("SCHEMA") for item in findings)
    anti_hallucination_ok = True
    return QualityReport(
        gdpr_ok=gdpr_ok,
        csn_typography_ok=csn_ok,
        anti_hallucination_ok=anti_hallucination_ok,
        schema_ok=schema_ok,
        validator_summary=summary,
        reports={},
        notes=[],
    )


def _evidence_required(cv_ssot_json: dict[str, Any], evidence_map: list[EvidenceItem]) -> bool:
    if evidence_map:
        return False
    for value in validator.iter_strings(cv_ssot_json):
        if re.search(r"\d", value):
            return True
    return False


def _build_report_payload(
    findings: list[validator.Finding],
    input_path: Path,
    profile: str,
) -> dict[str, Any]:
    summary = validator.build_summary(findings)
    return {
        "input_path": str(input_path),
        "profile": profile,
        "mode": "json",
        "summary": summary,
        "findings": [finding.__dict__ for finding in findings],
        "block_export": (summary["CRITICAL"] + summary["ERROR"]) > 0,
    }


async def extract_facts(
    request: GenerateRequest,
    *,
    agent: Agent[None] | None = None,
) -> ExtractOutput:
    resolved_agent = agent or create_extract_agent(
        output_type=ExtractOutput, strict_json_schema=False
    )
    prompt = _build_extract_prompt(request)
    result = await Runner.run(resolved_agent, prompt)
    return ExtractOutput.model_validate(result.final_output)


def validate_ssot_json(
    cv_ssot_json: dict[str, Any],
    *,
    out_dir: Path,
    profile: str = "PUBLIC_SECTOR",
) -> tuple[list[validator.Finding], dict[str, str]]:
    findings = validator.validate_json(
        cv_ssot_json,
        SSOT_SCHEMA_PATH,
        profile,
        max_errors=50,
        check_nbsp=True,
    )
    report = _build_report_payload(findings, out_dir / "cv.json", profile)
    json_report, md_report = validator.write_report(out_dir, "cv", report)
    return findings, {"json_report_path": str(json_report), "md_report_path": str(md_report)}


async def render_documents(
    cv_ssot_json: dict[str, Any],
    request: GenerateRequest,
    *,
    revision_note: str | None = None,
    use_assistant: bool | None = None,
    render_agent: Agent[None] | None = None,
) -> tuple[str, str, str]:
    prompt = _build_render_prompt(cv_ssot_json, request, revision_note=revision_note)
    if use_assistant is None:
        use_assistant = use_assistant_api()
    if use_assistant:
        output_text = await run_assistant(prompt)
    else:
        resolved_agent = render_agent or create_render_agent()
        result = await Runner.run(resolved_agent, prompt)
        output_text = str(result.final_output)
    output_text = validator.apply_fixes_to_text(output_text, enable_nbsp=False)
    return _split_sections(output_text)


async def revise_package(
    cv_ssot_json: dict[str, Any],
    request: GenerateRequest,
    revision_note: str,
    *,
    out_dir: Path = Path("out"),
    render_agent: Agent[None] | None = None,
    use_assistant: bool | None = None,
) -> GenerateResponse:
    findings, report_paths = validate_ssot_json(cv_ssot_json, out_dir=out_dir)
    quality = _findings_to_quality(findings)
    quality.reports = report_paths

    analysis_ru, cv_md_cs, cover_letter_cs = await render_documents(
        cv_ssot_json,
        request,
        revision_note=revision_note,
        render_agent=render_agent,
        use_assistant=use_assistant,
    )
    if not all([analysis_ru, cv_md_cs, cover_letter_cs]):
        raise ValueError("Output format validation failed.")

    return GenerateResponse(
        analysis_ru=analysis_ru,
        cv_md_cs=cv_md_cs,
        cover_letter_cs=cover_letter_cs,
        cv_ssot_json=cv_ssot_json,
        quality=quality,
        evidence_map=[],
        revision_id=f"rev_{uuid.uuid4().hex[:12]}",
    )


async def generate_full_package(
    request: GenerateRequest,
    *,
    out_dir: Path = Path("out"),
    extract_agent: Agent[None] | None = None,
    render_agent: Agent[None] | None = None,
    use_assistant: bool | None = None,
) -> GenerateResponse:
    extract_output = await extract_facts(request, agent=extract_agent)

    findings, report_paths = validate_ssot_json(extract_output.cv_ssot_json, out_dir=out_dir)
    quality = _findings_to_quality(findings)
    quality.reports = report_paths

    if _evidence_required(extract_output.cv_ssot_json, extract_output.evidence_map):
        quality.anti_hallucination_ok = False
        quality.notes.append("Evidence map missing for claims with numeric facts.")

    analysis_ru, cv_md_cs, cover_letter_cs = await render_documents(
        extract_output.cv_ssot_json,
        request,
        render_agent=render_agent,
        use_assistant=use_assistant,
    )
    if not all([analysis_ru, cv_md_cs, cover_letter_cs]):
        analysis_ru, cv_md_cs, cover_letter_cs = await render_documents(
            extract_output.cv_ssot_json,
            request,
            revision_note="Output format invalid. Use the required section headers exactly.",
            render_agent=render_agent,
            use_assistant=use_assistant,
        )
        if not all([analysis_ru, cv_md_cs, cover_letter_cs]):
            raise ValueError("Output format validation failed.")

    return GenerateResponse(
        analysis_ru=analysis_ru,
        cv_md_cs=cv_md_cs,
        cover_letter_cs=cover_letter_cs,
        cv_ssot_json=extract_output.cv_ssot_json,
        quality=quality,
        evidence_map=extract_output.evidence_map,
        revision_id=f"rev_{uuid.uuid4().hex[:12]}",
    )
