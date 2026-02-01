"""
CZ Career Architect - Validation Logic
Handles GDPR and CSN typography validation with caching and metrics
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Add packages to path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "packages"))

from validators.cz_cv_validator_adapter import (
    apply_fixes_to_text,
    build_summary,
    check_csn_typography,
    check_gdpr,
)

from src.logging_config import get_logger
from src.config import get_settings
from src.exceptions import GDPRValidationError, CSNTypographyError
from src.cache import cached
from src.metrics import record_validation_error

logger = get_logger(__name__)


@cached('validation_text', ttl=3600)  # Cache for 1 hour
def validate_text(text: str, enable_nbsp: bool = False) -> Tuple[List[Dict], str]:
    """
    Validate text for GDPR and CSN typography compliance.
    
    Args:
        text: Text to validate
        enable_nbsp: Whether to check for non-breaking spaces
        
    Returns:
        tuple: (findings, summary_line)
        
    Raises:
        GDPRValidationError: If critical GDPR violations found
        CSNTypographyError: If critical ČSN violations found
    """
    logger.info(f"Validating text (length: {len(text)} chars, nbsp={enable_nbsp})")
    
    try:
        findings = []
        
        # GDPR checks
        gdpr_findings = check_gdpr(text)
        findings.extend(gdpr_findings)
        
        # ČSN typography checks
        csn_findings = check_csn_typography(text, check_nbsp=enable_nbsp)
        findings.extend(csn_findings)
        
        if not findings:
            logger.info("✓ Validation passed: No issues found")
            return findings, "✅ No issues"
        
        # Build summary
        summary_dict = build_summary(findings)
        summary_line = (
            f"  CRITICAL: {summary_dict['CRITICAL']}, ERROR: {summary_dict['ERROR']}, "
            f"WARNING: {summary_dict['WARNING']}"
        )
        
        logger.warning(f"Validation found {len(findings)} issue(s)")
        
        # Record metrics
        if gdpr_findings:
            record_validation_error('GDPR')
        if csn_findings:
            record_validation_error('CSN')
        
        # Check for critical violations
        critical_findings = [f for f in findings if f.get('severity') == 'CRITICAL']
        if critical_findings:
            critical_gdpr = [f for f in critical_findings if 'GDPR' in f.get('code', '')]
            critical_csn = [f for f in critical_findings if 'CSN' in f.get('code', '')]
            
            if critical_gdpr:
                logger.error(f"Critical GDPR violations: {len(critical_gdpr)}")
                raise GDPRValidationError(critical_gdpr)
            elif critical_csn:
                logger.error(f"Critical ČSN violations: {len(critical_csn)}")
                raise CSNTypographyError(critical_csn)
        
        return findings, summary_line
        
    except (GDPRValidationError, CSNTypographyError):
        raise
    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        raise


def apply_validation_fixes(text: str, enable_nbsp: bool = False) -> str:
    """
    Apply automatic fixes to text.
    
    Args:
        text: Text to fix
        enable_nbsp: Whether to apply non-breaking space fixes
        
    Returns:
        str: Fixed text
    """
    logger.info(f"Applying validation fixes (nbsp={enable_nbsp})")
    
    try:
        fixed_text = apply_fixes_to_text(text, enable_nbsp=enable_nbsp)
        logger.info("✓ Validation fixes applied successfully")
        return fixed_text
        
    except Exception as e:
        logger.error(f"Error applying fixes: {e}", exc_info=True)
        raise


def quick_gdpr_check(text: str) -> bool:
    """
    Quick GDPR check without full validation.
    
    Args:
        text: Text to check
        
    Returns:
        True if GDPR compliant, False otherwise
    """
    logger.debug("Performing quick GDPR check")
    
    try:
        gdpr_findings = check_gdpr(text)
        critical_gdpr = [f for f in gdpr_findings if f.get('severity') == 'CRITICAL']
        
        is_compliant = len(critical_gdpr) == 0
        logger.debug(f"GDPR check result: {'✓ Compliant' if is_compliant else '✗ Non-compliant'}")
        
        return is_compliant
        
    except Exception as e:
        logger.error(f"Quick GDPR check error: {e}")
        return False


__all__ = [
    "validate_text",
    "apply_validation_fixes",
    "quick_gdpr_check",
    "build_summary",
    "check_gdpr",
    "check_csn_typography",
]
