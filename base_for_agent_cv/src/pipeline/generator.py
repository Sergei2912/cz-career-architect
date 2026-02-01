"""
CZ Career Architect - Document Generation Logic
Handles CV and cover letter generation with logging, caching, and metrics
"""

import sys
from pathlib import Path
from typing import Optional

# Add packages to path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "packages"))

from src.logging_config import get_logger
from src.config import get_settings
from src.exceptions import DocumentGenerationError, ModelResponseError
from src.cache import cached
from src.metrics import (
    record_cv_generated,
    record_cover_letter_generated,
    track_model_request
)

logger = get_logger(__name__)


SYSTEM_PROMPT = """You are CZ Career Architect v1.2.3.

GDPR FIREWALL (ALL documents):
- Art. 5(1)(c): birth_date, age, marital_status, children, photo, nationality, full_address
- Art. 9: ethnicity, religion, health_status, union_member
- Art. 87: rodne_cislo

TITLE: MDDr./MUDr. ONLY if approbation_status == "Plne aprobovan"
CONSENT: NOT required for specific job. Only for talent pool.
ATS: No tables, columns, graphics. Single language (cs-CZ).
CSN: Dates "15. 1. 2025", Phone "+420 777 123 456", Currency "25 000 Kc"

OUTPUT:
### RU: Profile Analysis
### CZ: CV
### CZ: Motivacni dopis
"""


@track_model_request('gpt-5.2')
@cached('full_package_generation', ttl=86400)  # Cache for 24 hours
async def generate_full_package(agent, user_request: str, runner_class) -> str:
    """
    Generate a full HR document package.
    
    Args:
        agent: Agent instance
        user_request: User's request string
        runner_class: Runner class for executing the agent
        
    Returns:
        str: Generated output
        
    Raises:
        DocumentGenerationError: If generation fails
    """
    logger.info("Starting full package generation")
    logger.debug(f"User request length: {len(user_request)} chars")
    
    try:
        result = await runner_class.run(agent, user_request)
        
        if not hasattr(result, 'final_output'):
            logger.error("Invalid response from agent: missing final_output")
            raise ModelResponseError("Agent response missing final_output")
        
        output = str(result.final_output)
        
        if not output or len(output.strip()) < 200:
            logger.error(f"Generated package too short: {len(output)} chars")
            raise DocumentGenerationError("Generated package is too short or empty")
        
        logger.info(f"✓ Full package generated successfully ({len(output)} chars)")
        
        # Record metrics (CV + cover letter in package)
        record_cv_generated()
        record_cover_letter_generated()
        
        return output
        
    except (DocumentGenerationError, ModelResponseError):
        raise
    except Exception as e:
        logger.error(f"Full package generation error: {e}", exc_info=True)
        raise DocumentGenerationError(f"Failed to generate package: {e}", model_error=str(e))


def get_default_user_request() -> str:
    """
    Get the default user request template.
    
    Returns:
        str: Default request template
    """
    logger.debug("Getting default user request template")
    
    return """
Vytvor kompletni balicek HR dokumentu.

INTAKE (12 poli):
1. Cel: konkretni vakance - FN Motol
2. Typ dokumentu: CV + motivacni dopis
3. Pozice: Zubni lekar - vseobecna stomatologie
4. Zamestnavatel: FN Motol, Praha
5. Profil: MEDICAL-SENIOR-EU
6. Jmeno: Sergii Anipreyev (bez titulu - neni Plne aprobovan)
7. Lokace: Praha, Ceska republika
8. Kontakty: sergii.anipreyev@email.cz | +420 777 123 456
9. Med. statusy: Nostrifikace dokoncena (UK Praha, c.j. UKRUK/123456/2025),
   Povoleni k vykonu odborne praxe, CSK
10. Pracovni povoleni: Zamestnanecka karta
11. Zkusenosti: 10+ let v Izraeli, endodoncie 1700+ vykonu,
    mikroskop 375+ hodin, IDF Medical Corps Kapitan 2015-2023
12. Vzdelani: DMD Tel Aviv University 2014, Jazyky: CS B2, EN C1, HE C2, RU native

PRAVIDLA:
- BEZ titulu MDDr. (neni Plne aprobovan)
- BEZ consent clause (konkretni pozice)
- Pouze cestina v dokumentech
"""


__all__ = [
    "SYSTEM_PROMPT",
    "generate_full_package",
    "get_default_user_request",
]
