from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

NBSP = "\u00a0"
EN_DASH = "\u2013"

SINGLE_LETTER_PREPS = "ksvzoauiaKS VZOAUIA".replace(" ", "")
CASE_NUMBER_CONTEXT_RE = re.compile(
    r"(?:c|č)\s*\.?\s*j\s*\.?|cislo jednaci|číslo jednací",
    re.IGNORECASE,
)


@dataclass
class Finding:
    level: str
    code: str
    message: str
    location: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate CZ medical CV SSOT JSON or DOCX exports."
    )
    parser.add_argument("input_path", help="Path to cv.json or export.docx")
    parser.add_argument(
        "--schema",
        required=False,
        help="Path to cz_dentist_cv_gov_ats_gdpr_csn_v1.1.0.schema.json",
    )
    parser.add_argument(
        "--profile",
        default="PUBLIC_SECTOR",
        help="Validation profile: ATS_SAFE | HR_REVIEW | PUBLIC_SECTOR",
    )
    parser.add_argument("--out", default="out", help="Output directory for reports")
    parser.add_argument("--fix", action="store_true", help="Apply safe auto-fixes")
    parser.add_argument("--no-nbsp", action="store_true", help="Disable NBSP auto-fix")
    parser.add_argument("--max-errors", type=int, default=50, help="Max errors before stop")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_strings(item)


def apply_fixes_to_text(text: str, *, enable_nbsp: bool) -> str:
    fixed = text

    fixed = re.sub(
        r"\b(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})\b",
        r"\1. \2. \3",
        fixed,
    )
    fixed = re.sub(r"\b(\d{4})\s*-\s*(\d{4})\b", rf"\1{EN_DASH}\2", fixed)

    if enable_nbsp:
        fixed = re.sub(rf"\b([{SINGLE_LETTER_PREPS}])\s+", rf"\1{NBSP}", fixed)
        fixed = re.sub(r"\b(\d[\d\s]*)\s+Kč\b", rf"\1{NBSP}Kč", fixed)

    return fixed


def apply_fixes_to_json(data: Any, *, enable_nbsp: bool) -> Any:
    if isinstance(data, str):
        return apply_fixes_to_text(data, enable_nbsp=enable_nbsp)
    if isinstance(data, list):
        return [apply_fixes_to_json(item, enable_nbsp=enable_nbsp) for item in data]
    if isinstance(data, dict):
        return {
            key: apply_fixes_to_json(value, enable_nbsp=enable_nbsp) for key, value in data.items()
        }
    return data


def check_gdpr(text: str) -> list[Finding]:
    findings: list[Finding] = []
    lower = text.lower()

    if "rodné číslo" in lower or "rodne cislo" in lower:
        findings.append(
            Finding(
                level="ERROR",
                code="GDPR_RODNE_CISLO",
                message="Rodné číslo is forbidden in public-sector CVs.",
            )
        )

    for match in re.finditer(r"\b\d{6}/\d{4}\b", text):
        if _is_case_number_context(text, match.start()):
            continue
        findings.append(
            Finding(
                level="ERROR",
                code="GDPR_RODNE_CISLO_PATTERN",
                message="Potential Rodné číslo pattern detected.",
            )
        )
        break

    if re.search(r"\b(datum narozen[ií]|date of birth|dob)\b", lower):
        if re.search(r"\b\d{1,2}\.\s?\d{1,2}\.\s?\d{4}\b", text):
            findings.append(
                Finding(
                    level="ERROR",
                    code="GDPR_BIRTH_DATE",
                    message="Full birth date is not allowed.",
                )
            )

    if re.search(
        r"\b(rodinn[ýy] stav|marital status|vdan[aá]|ženat[ýy]|rozveden[ýa]|děti|počet dětí)\b",
        lower,
    ):
        findings.append(
            Finding(
                level="ERROR",
                code="GDPR_MARITAL_CHILDREN",
                message="Marital status/children data is not allowed.",
            )
        )

    return findings


def _is_case_number_context(text: str, start: int) -> bool:
    window = text[max(0, start - 40) : start]
    return bool(CASE_NUMBER_CONTEXT_RE.search(window))


def check_csn_typography(text: str, *, check_nbsp: bool) -> list[Finding]:
    findings: list[Finding] = []

    date_pattern = re.compile(r"\b\d{1,2}\.\s?\d{1,2}\.\s?\d{4}\b")
    for match in date_pattern.finditer(text):
        if not re.fullmatch(r"\d{1,2}\.\s\d{1,2}\.\s\d{4}", match.group(0)):
            findings.append(
                Finding(
                    level="WARNING",
                    code="CSN_DATE_SPACING",
                    message="Date should include spaces after dots (D. M. YYYY).",
                )
            )
            break

    if re.search(r"\b\d{4}\s*-\s*\d{4}\b", text):
        findings.append(
            Finding(
                level="WARNING",
                code="CSN_YEAR_RANGE",
                message="Year ranges should use en-dash (2019–2022).",
            )
        )

    if check_nbsp:
        if re.search(rf"\b([{SINGLE_LETTER_PREPS}])\s+[A-Za-zÁ-ž]", text):
            findings.append(
                Finding(
                    level="WARNING",
                    code="CSN_NBSP_PREP",
                    message="Single-letter prepositions should use NBSP.",
                )
            )
        if re.search(r"\b\d[\d\s]*\s+Kč\b", text):
            findings.append(
                Finding(
                    level="WARNING",
                    code="CSN_NBSP_CURRENCY",
                    message="Currency should use NBSP between amount and Kč.",
                )
            )

    return findings


def check_profile_restrictions(data: dict[str, Any], profile: str) -> list[Finding]:
    findings: list[Finding] = []
    profile_upper = profile.upper()
    if profile_upper != "ATS_SAFE":
        return findings

    meta = data.get("meta", {}) if isinstance(data, dict) else {}
    layout = meta.get("layout", {}) if isinstance(meta, dict) else {}
    columns = layout.get("columns")
    has_photo = layout.get("has_photo")

    if isinstance(columns, int) and columns > 1:
        findings.append(
            Finding(
                level="ERROR",
                code="ATS_COLUMNS",
                message="ATS_SAFE forbids multi-column layouts.",
                location="meta.layout.columns",
            )
        )
    if has_photo is True:
        findings.append(
            Finding(
                level="ERROR",
                code="ATS_PHOTO",
                message="ATS_SAFE forbids photos.",
                location="meta.layout.has_photo",
            )
        )
    if isinstance(data, dict) and "basics" in data:
        basics = data.get("basics", {})
        if isinstance(basics, dict) and basics.get("photo_url"):
            findings.append(
                Finding(
                    level="ERROR",
                    code="ATS_PHOTO_URL",
                    message="ATS_SAFE forbids photo URLs.",
                    location="basics.photo_url",
                )
            )

    return findings


def validate_schema(data: Any, schema_path: Path, max_errors: int) -> list[Finding]:
    if not schema_path.exists():
        return [
            Finding(
                level="CRITICAL",
                code="SCHEMA_MISSING",
                message=f"Schema file not found: {schema_path}",
            )
        ]

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    findings: list[Finding] = []

    for error in validator.iter_errors(data):
        location = ".".join([str(part) for part in error.path]) if error.path else None
        findings.append(
            Finding(
                level="ERROR",
                code="SCHEMA_VALIDATION",
                message=error.message,
                location=location,
            )
        )
        if len(findings) >= max_errors:
            findings.append(
                Finding(
                    level="ERROR",
                    code="SCHEMA_MAX_ERRORS",
                    message="Max error limit reached.",
                )
            )
            break

    return findings


def build_summary(findings: Iterable[Finding]) -> dict[str, int]:
    summary = {"CRITICAL": 0, "ERROR": 0, "WARNING": 0, "INFO": 0}
    for finding in findings:
        summary[finding.level] = summary.get(finding.level, 0) + 1
    return summary


def extract_docx_text(path: Path) -> tuple[str, list[str]]:
    if not zipfile.is_zipfile(path):
        raise ValueError("Invalid DOCX file.")

    text_parts: list[str] = []
    metadata_flags: list[str] = []

    with zipfile.ZipFile(path) as docx:
        try:
            document_xml = docx.read("word/document.xml").decode("utf-8")
            text_parts.append(document_xml)
        except KeyError as exc:
            raise ValueError("DOCX document.xml missing.") from exc

        if any(name.startswith("word/header") for name in docx.namelist()):
            metadata_flags.append("HAS_HEADER")
        if any(name.startswith("word/footer") for name in docx.namelist()):
            metadata_flags.append("HAS_FOOTER")
        if any(name.startswith("word/media/") for name in docx.namelist()):
            metadata_flags.append("HAS_MEDIA")

    return "\n".join(text_parts), metadata_flags


def validate_docx(path: Path, profile: str, max_errors: int) -> list[Finding]:
    findings: list[Finding] = []
    try:
        text, flags = extract_docx_text(path)
    except ValueError as exc:
        return [
            Finding(
                level="CRITICAL",
                code="DOCX_READ_ERROR",
                message=str(exc),
            )
        ]

    findings.extend(check_gdpr(text))
    findings.extend(check_csn_typography(text, check_nbsp=True))

    if profile.upper() == "ATS_SAFE":
        if "HAS_MEDIA" in flags:
            findings.append(
                Finding(
                    level="ERROR",
                    code="ATS_MEDIA",
                    message="ATS_SAFE forbids embedded media/photos.",
                )
            )
        if "HAS_HEADER" in flags or "HAS_FOOTER" in flags:
            findings.append(
                Finding(
                    level="ERROR",
                    code="ATS_HEADER_FOOTER",
                    message="ATS_SAFE forbids headers/footers.",
                )
            )
        if re.search(r"<w:tbl\b", text):
            findings.append(
                Finding(
                    level="ERROR",
                    code="ATS_TABLE",
                    message="ATS_SAFE forbids tables.",
                )
            )
        if re.search(r"<w:cols\b", text):
            findings.append(
                Finding(
                    level="ERROR",
                    code="ATS_COLUMNS",
                    message="ATS_SAFE forbids multi-column layouts.",
                )
            )

    if len(findings) >= max_errors:
        findings = findings[:max_errors]
        findings.append(
            Finding(
                level="ERROR",
                code="MAX_ERRORS",
                message="Max error limit reached.",
            )
        )

    return findings


def validate_json(
    data: Any,
    schema_path: Path,
    profile: str,
    max_errors: int,
    *,
    check_nbsp: bool,
) -> list[Finding]:
    findings: list[Finding] = []

    findings.extend(validate_schema(data, schema_path, max_errors))
    if len(findings) >= max_errors:
        return findings

    for text in iter_strings(data):
        findings.extend(check_gdpr(text))
        findings.extend(check_csn_typography(text, check_nbsp=check_nbsp))
        if len(findings) >= max_errors:
            return findings

    if isinstance(data, dict):
        findings.extend(check_profile_restrictions(data, profile))

    return findings


def write_report(out_dir: Path, stem: str, report: dict[str, Any]) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{stem}_report.json"
    md_path = out_dir / f"{stem}_report.md"

    write_json(json_path, report)

    lines = [f"# Validation report: {stem}", ""]
    summary = report.get("summary", {})
    lines.append("## Summary")
    for key in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
        lines.append(f"- {key}: {summary.get(key, 0)}")
    lines.append("")
    lines.append("## Findings")
    for item in report.get("findings", []):
        location = f" ({item.get('location')})" if item.get("location") else ""
        lines.append(f"- [{item.get('level')}] {item.get('code')}: {item.get('message')}{location}")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    return json_path, md_path


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_path)
    out_dir = Path(args.out)
    profile = args.profile

    if not input_path.exists():
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    report: dict[str, Any] = {
        "input_path": str(input_path),
        "profile": profile,
        "mode": input_path.suffix.lower().lstrip("."),
    }

    if input_path.suffix.lower() == ".json":
        if not args.schema:
            print("--schema is required for JSON validation", file=sys.stderr)
            return 2
        schema_path = Path(args.schema)
        data = load_json(input_path)

        summary_before = None
        fixed_path = None
        if args.fix:
            summary_before = build_summary(
                validate_json(
                    data,
                    schema_path,
                    profile,
                    args.max_errors,
                    check_nbsp=not args.no_nbsp,
                )
            )
            data = apply_fixes_to_json(data, enable_nbsp=not args.no_nbsp)
            fixed_path = out_dir / f"{input_path.stem}_fixed.json"
            out_dir.mkdir(parents=True, exist_ok=True)
            write_json(fixed_path, data)

        findings = validate_json(
            data,
            schema_path,
            profile,
            args.max_errors,
            check_nbsp=not args.no_nbsp,
        )

        report["summary"] = build_summary(findings)
        if args.fix:
            report["auto_fix"] = {
                "applied": True,
                "summary_before": summary_before,
                "summary_after": report["summary"],
                "fixed_path": str(fixed_path) if fixed_path else None,
            }
    elif input_path.suffix.lower() == ".docx":
        findings = validate_docx(input_path, profile, args.max_errors)
        report["summary"] = build_summary(findings)
        if args.fix:
            report["auto_fix"] = {
                "applied": False,
                "reason": "DOCX auto-fix is not supported.",
            }
    else:
        print("Unsupported file type. Use .json or .docx", file=sys.stderr)
        return 2

    report["findings"] = [finding.__dict__ for finding in findings]
    report["block_export"] = (report["summary"]["CRITICAL"] + report["summary"]["ERROR"]) > 0

    stem = input_path.stem
    json_report, md_report = write_report(out_dir, stem, report)
    print(f"Report written: {json_report}")
    print(f"Report written: {md_report}")

    return 2 if report["block_export"] else 0


if __name__ == "__main__":
    sys.exit(main())
