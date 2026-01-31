---
id: S07
group_id: SCHEMA-VALIDATION
title: GDPR Consent Clause CS
type: validation
path: base knowledge/schemas/validation/gdpr_consent_clause_cs.md
format: md
language: cs-CZ
jurisdiction: CZ
status: active
quality: 10
source:
  name: Custom
  retrieved: '2026-01-21'
updated: '2026-01-21'
qa_date: '2026-01-26'
---

# GDPR Consent Clause CS


# GDPR SOUHLAS PRO ŽIVOTOPIS (CS-CZ)
# Verze: 1.0.0
# Datum: 2026-01-18
# Zdroj: Adaptace z PL/EN verze s ověřením dle českého práva

================================================================================
## ⚠️ KDY JE SOUHLAS NUTNÝ?
================================================================================

| Situace | Souhlas v CV | Právní základ |
|---------|--------------|---------------|
| Odpověď na konkrétní inzerát | ❌ **NE** | Čl. 6(1)(b) GDPR |
| Spekulativní žádost | ✅ ANO | Čl. 6(1)(a) GDPR |
| Personální agentura | ✅ ANO | Čl. 6(1)(a) GDPR |
| Databáze kandidátů | ✅ ANO | Čl. 6(1)(a) GDPR |

**Poznámka:** Vyžadování souhlasu tam, kde není nutný ("nadbytečný souhlas"),
je porušením zásady transparentnosti dle GDPR.

**Zdroj:** ÚOOÚ, Vema.cz (právní analýza)

================================================================================
## TEXT SOUHLASU (pro kopírování)
================================================================================

Souhlasím se zpracováním osobních údajů pro účely výběrového řízení dle nařízení (EU) 2016/679 (GDPR).

================================================================================
## PRÁVNÍ ODKAZY
================================================================================

### EU
- Nařízení (EU) 2016/679 (GDPR), čl. 6 odst. 1 písm. a)
- EUR-Lex: https://eur-lex.europa.eu/eli/reg/2016/679/oj

### Česká republika
- Zákon č. 110/2019 Sb., o zpracování osobních údajů
- ÚOOÚ: https://uoou.gov.cz/

================================================================================
## JSON FRAGMENT PRO CZ CAREER ARCHITECT
================================================================================

```json
{
  "gdpr_consent": {
    "enabled": true,
    "required": false,
    "text_cs": "Souhlasím se zpracováním osobních údajů pro účely výběrového řízení dle nařízení (EU) 2016/679 (GDPR).",
    "usage_rule": "Použít pouze pro spekulativní žádosti, personální agentury nebo databáze kandidátů. Pro odpověď na konkrétní inzerát NEPOUŽÍVAT."
  }
}
```

================================================================================
