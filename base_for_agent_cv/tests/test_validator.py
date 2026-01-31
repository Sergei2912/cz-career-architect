"""Tests for packages/validators/cz_cv_validator_adapter.py"""

import json
from pathlib import Path

import pytest

from packages.validators.cz_cv_validator_adapter import (
    Finding,
    apply_fixes_to_json,
    apply_fixes_to_text,
    build_summary,
    check_csn_typography,
    check_gdpr,
    check_profile_restrictions,
    iter_strings,
    validate_json,
    validate_schema,
)

EN_DASH = "\u2013"
NBSP = "\u00a0"

SCHEMA_PATH = Path("Schemas/cz_dentist_cv_gov_ats_gdpr_csn_v1.1.0.schema.json")


# ── GDPR checks ──────────────────────────────────────────────


class TestCheckGdpr:
    def test_clean_text_no_findings(self):
        text = "Sergii Anipreyev, Praha, +420 777 123 456"
        assert check_gdpr(text) == []

    def test_detects_rodne_cislo_phrase_cz(self):
        findings = check_gdpr("Rodné číslo: 850101/1234")
        codes = [f.code for f in findings]
        assert "GDPR_RODNE_CISLO" in codes

    def test_detects_rodne_cislo_phrase_ascii(self):
        findings = check_gdpr("rodne cislo kandidata")
        assert any(f.code == "GDPR_RODNE_CISLO" for f in findings)

    def test_detects_rodne_cislo_pattern(self):
        findings = check_gdpr("Identifikator: 850101/1234")
        assert any(f.code == "GDPR_RODNE_CISLO_PATTERN" for f in findings)

    def test_case_number_not_flagged_as_rodne_cislo(self):
        text = "č. j. UKRUK/123456/2025 a číslo jednací 850101/1234"
        findings = check_gdpr(text)
        assert not any(f.code == "GDPR_RODNE_CISLO_PATTERN" for f in findings)

    def test_detects_birth_date(self):
        text = "Datum narození: 15. 1. 1985"
        findings = check_gdpr(text)
        assert any(f.code == "GDPR_BIRTH_DATE" for f in findings)

    def test_date_without_birth_label_not_flagged(self):
        text = "Nastup: 15. 1. 2025"
        findings = check_gdpr(text)
        assert not any(f.code == "GDPR_BIRTH_DATE" for f in findings)

    def test_detects_marital_status_czech(self):
        findings = check_gdpr("Rodinný stav: ženatý")
        assert any(f.code == "GDPR_MARITAL_CHILDREN" for f in findings)

    def test_detects_children(self):
        findings = check_gdpr("Počet dětí: 2")
        assert any(f.code == "GDPR_MARITAL_CHILDREN" for f in findings)

    def test_detects_marital_english(self):
        findings = check_gdpr("Marital status: married")
        assert any(f.code == "GDPR_MARITAL_CHILDREN" for f in findings)


# ── ČSN typography checks ────────────────────────────────────


class TestCheckCsnTypography:
    def test_correct_date_no_warning(self):
        text = "Datum: 15. 1. 2025"
        findings = check_csn_typography(text, check_nbsp=False)
        assert not any(f.code == "CSN_DATE_SPACING" for f in findings)

    def test_date_missing_spaces(self):
        text = "Datum: 15.1.2025"
        findings = check_csn_typography(text, check_nbsp=False)
        assert any(f.code == "CSN_DATE_SPACING" for f in findings)

    def test_date_partial_space(self):
        text = "Datum: 15. 1.2025"
        findings = check_csn_typography(text, check_nbsp=False)
        assert any(f.code == "CSN_DATE_SPACING" for f in findings)

    def test_year_range_with_hyphen(self):
        text = "Praxe 2015-2023"
        findings = check_csn_typography(text, check_nbsp=False)
        assert any(f.code == "CSN_YEAR_RANGE" for f in findings)

    def test_year_range_with_en_dash_ok(self):
        text = f"Praxe 2015{EN_DASH}2023"
        findings = check_csn_typography(text, check_nbsp=False)
        assert not any(f.code == "CSN_YEAR_RANGE" for f in findings)

    def test_nbsp_prep_warning(self):
        text = "k dispozici na vyžádání"
        findings = check_csn_typography(text, check_nbsp=True)
        assert any(f.code == "CSN_NBSP_PREP" for f in findings)

    def test_nbsp_prep_not_checked_when_disabled(self):
        text = "k dispozici na vyžádání"
        findings = check_csn_typography(text, check_nbsp=False)
        assert not any(f.code == "CSN_NBSP_PREP" for f in findings)

    def test_nbsp_currency_warning(self):
        text = "Plat: 25 000 Kč"
        findings = check_csn_typography(text, check_nbsp=True)
        assert any(f.code == "CSN_NBSP_CURRENCY" for f in findings)

    def test_nbsp_currency_not_checked_when_disabled(self):
        text = "Plat: 25 000 Kč"
        findings = check_csn_typography(text, check_nbsp=False)
        assert not any(f.code == "CSN_NBSP_CURRENCY" for f in findings)


# ── Auto-fix ─────────────────────────────────────────────────


class TestApplyFixes:
    def test_fix_date_spacing(self):
        assert "15. 1. 2025" in apply_fixes_to_text("15.1.2025", enable_nbsp=False)

    def test_fix_year_range_en_dash(self):
        fixed = apply_fixes_to_text("2015-2023", enable_nbsp=False)
        assert EN_DASH in fixed
        assert "-" not in fixed

    def test_nbsp_single_letter_prep(self):
        fixed = apply_fixes_to_text("k dispozici", enable_nbsp=True)
        assert f"k{NBSP}dispozici" in fixed

    def test_nbsp_currency(self):
        fixed = apply_fixes_to_text("25 000 Kč", enable_nbsp=True)
        assert NBSP in fixed

    def test_no_nbsp_when_disabled(self):
        fixed = apply_fixes_to_text("k dispozici", enable_nbsp=False)
        assert NBSP not in fixed

    def test_apply_fixes_to_json_recursive(self):
        data = {"a": "15.1.2025", "b": ["2015-2023"], "c": {"d": "1.6.2014"}}
        fixed = apply_fixes_to_json(data, enable_nbsp=False)
        assert "15. 1. 2025" in fixed["a"]
        assert EN_DASH in fixed["b"][0]
        assert "1. 6. 2014" in fixed["c"]["d"]

    def test_apply_fixes_preserves_non_strings(self):
        data = {"count": 42, "active": True, "items": [1, 2]}
        fixed = apply_fixes_to_json(data, enable_nbsp=False)
        assert fixed == data


# ── Profile restrictions (ATS) ───────────────────────────────


class TestProfileRestrictions:
    def test_ats_safe_multi_column_error(self):
        data = {"meta": {"layout": {"columns": 2, "has_photo": False}}}
        findings = check_profile_restrictions(data, "ATS_SAFE")
        assert any(f.code == "ATS_COLUMNS" for f in findings)

    def test_ats_safe_photo_error(self):
        data = {"meta": {"layout": {"columns": 1, "has_photo": True}}}
        findings = check_profile_restrictions(data, "ATS_SAFE")
        assert any(f.code == "ATS_PHOTO" for f in findings)

    def test_ats_safe_photo_url_error(self):
        data = {"basics": {"photo_url": "https://example.com/photo.jpg"}}
        findings = check_profile_restrictions(data, "ATS_SAFE")
        assert any(f.code == "ATS_PHOTO_URL" for f in findings)

    def test_ats_safe_single_column_no_photo_clean(self):
        data = {"meta": {"layout": {"columns": 1, "has_photo": False}}}
        findings = check_profile_restrictions(data, "ATS_SAFE")
        assert findings == []

    def test_non_ats_profile_skips_checks(self):
        data = {"meta": {"layout": {"columns": 2, "has_photo": True}}}
        assert check_profile_restrictions(data, "PUBLIC_SECTOR") == []
        assert check_profile_restrictions(data, "HR_REVIEW") == []


# ── build_summary ────────────────────────────────────────────


class TestBuildSummary:
    def test_empty_findings(self):
        s = build_summary([])
        assert s == {"CRITICAL": 0, "ERROR": 0, "WARNING": 0, "INFO": 0}

    def test_counts_levels(self):
        findings = [
            Finding("ERROR", "A", "msg"),
            Finding("ERROR", "B", "msg"),
            Finding("WARNING", "C", "msg"),
            Finding("CRITICAL", "D", "msg"),
        ]
        s = build_summary(findings)
        assert s["CRITICAL"] == 1
        assert s["ERROR"] == 2
        assert s["WARNING"] == 1
        assert s["INFO"] == 0


# ── iter_strings ─────────────────────────────────────────────


class TestIterStrings:
    def test_flat_string(self):
        assert list(iter_strings("hello")) == ["hello"]

    def test_nested_dict(self):
        data = {"a": "x", "b": {"c": "y"}}
        assert sorted(iter_strings(data)) == ["x", "y"]

    def test_list(self):
        assert list(iter_strings(["a", "b"])) == ["a", "b"]

    def test_mixed(self):
        data = {"a": ["x", {"b": "y"}], "c": "z"}
        assert sorted(iter_strings(data)) == ["x", "y", "z"]

    def test_non_string_skipped(self):
        assert list(iter_strings(42)) == []
        assert list(iter_strings(None)) == []


# ── Schema validation ────────────────────────────────────────


class TestValidateSchema:
    def test_missing_schema_file(self, tmp_path):
        findings = validate_schema({}, tmp_path / "nonexistent.json", 50)
        assert any(f.code == "SCHEMA_MISSING" for f in findings)

    def test_valid_data_against_trivial_schema(self, tmp_path):
        schema_path = tmp_path / "schema.json"
        schema_path.write_text(json.dumps({"type": "object"}))
        findings = validate_schema({"key": "value"}, schema_path, 50)
        assert findings == []

    def test_invalid_data_against_schema(self, tmp_path):
        schema_path = tmp_path / "schema.json"
        schema_path.write_text(json.dumps({
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
        }))
        findings = validate_schema({}, schema_path, 50)
        assert any(f.code == "SCHEMA_VALIDATION" for f in findings)

    def test_max_errors_limit(self, tmp_path):
        schema_path = tmp_path / "schema.json"
        schema_path.write_text(json.dumps({
            "type": "object",
            "required": ["a", "b", "c", "d", "e"],
        }))
        findings = validate_schema({}, schema_path, 2)
        assert len(findings) <= 3  # 2 + MAX_ERRORS marker


# ── validate_json (integration) ──────────────────────────────


class TestValidateJson:
    def test_clean_data_trivial_schema(self, tmp_path):
        schema_path = tmp_path / "schema.json"
        schema_path.write_text(json.dumps({"type": "object"}))
        data = {"name": "Sergii Anipreyev", "city": "Praha"}
        findings = validate_json(data, schema_path, "PUBLIC_SECTOR", 50, check_nbsp=False)
        assert findings == []

    def test_gdpr_violation_in_json_values(self, tmp_path):
        schema_path = tmp_path / "schema.json"
        schema_path.write_text(json.dumps({"type": "object"}))
        data = {"info": "Rodinný stav: ženatý, datum narození: 15. 1. 1985"}
        findings = validate_json(data, schema_path, "PUBLIC_SECTOR", 50, check_nbsp=False)
        assert any(f.code == "GDPR_MARITAL_CHILDREN" for f in findings)
        assert any(f.code == "GDPR_BIRTH_DATE" for f in findings)

    def test_csn_issues_in_json_values(self, tmp_path):
        schema_path = tmp_path / "schema.json"
        schema_path.write_text(json.dumps({"type": "object"}))
        data = {"period": "2015-2023", "date": "15.1.2025"}
        findings = validate_json(data, schema_path, "PUBLIC_SECTOR", 50, check_nbsp=False)
        assert any(f.code == "CSN_YEAR_RANGE" for f in findings)
        assert any(f.code == "CSN_DATE_SPACING" for f in findings)
