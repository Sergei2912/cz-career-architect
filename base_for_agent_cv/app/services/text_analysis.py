import sys
from pathlib import Path
from typing import List

# Add project root to sys.path to allow imports from packages
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "packages"))

from validators.cz_cv_validator_adapter import check_csn_typography, check_gdpr


def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()

    if suffix == ".txt":
        return file_path.read_text(encoding="utf-8", errors="ignore")

    elif suffix == ".pdf":
        try:
            import fitz

            doc = fitz.open(file_path)
            text = "\n".join([page.get_text() for page in doc])
            doc.close()
            return text
        except Exception:
            try:
                import pdfplumber

                with pdfplumber.open(file_path) as pdf:
                    return "\n".join([p.extract_text() or "" for p in pdf.pages])
            except Exception:
                return "[Не удалось прочитать PDF]"

    elif suffix in {".docx", ".doc"}:
        try:
            import docx

            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception:
            return "[Не удалось прочитать DOCX]"

    return "[Неподдерживаемый формат]"


def analyze_text(text: str) -> List[str]:
    issues = []
    findings = check_gdpr(text) + check_csn_typography(text, check_nbsp=False)

    for f in findings:
        if "BIRTH" in f.code or "RODNE" in f.code:
            issues.append("❌ Найдена дата рождения — нужно удалить")
        elif "MARITAL" in f.code or "CHILDREN" in f.code:
            issues.append("❌ Семейный статус/дети — нужно удалить")
        elif "DATE" in f.code:
            issues.append('⚠️ Формат даты: используй "15. 1. 2025"')
        elif "YEAR_RANGE" in f.code:
            issues.append('⚠️ Диапазон лет: используй тире "2020–2024"')

    return list(set(issues))[:5]
