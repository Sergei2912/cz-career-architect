"""
CZ Career Architect - Validation Logic
Handles GDPR and CSN typography validation
"""

import sys
from pathlib import Path

# Add packages to path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "packages"))

from validators.cz_cv_validator_adapter import (
    apply_fixes_to_text,
    build_summary,
    check_csn_typography,
    check_gdpr,
)


def validate_text(text, enable_nbsp=False):
    """
    Validate text for GDPR and CSN typography compliance.
    
    Args:
        text: Text to validate
        enable_nbsp: Whether to check for non-breaking spaces
        
    Returns:
        tuple: (findings, summary_line)
    """
    findings = []
    findings.extend(check_gdpr(text))
    findings.extend(check_csn_typography(text, check_nbsp=enable_nbsp))
    
    if not findings:
        return findings, "✅ No issues"
    
    summary = build_summary(findings)
    summary_line = (
        f"  CRITICAL: {summary['CRITICAL']}, ERROR: {summary['ERROR']}, "
        f"WARNING: {summary['WARNING']}"
    )
    return findings, summary_line


def apply_validation_fixes(text, enable_nbsp=False):
    """
    Apply automatic fixes to text.
    
    Args:
        text: Text to fix
        enable_nbsp: Whether to apply non-breaking space fixes
        
    Returns:
        str: Fixed text
    """
    return apply_fixes_to_text(text, enable_nbsp=enable_nbsp)


__all__ = [
    "validate_text",
    "apply_validation_fixes",
    "build_summary",
    "check_gdpr",
    "check_csn_typography",
]
