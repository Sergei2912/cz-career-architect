#!/usr/bin/env python3
"""
CZ Career Architect - Interactive Chat Mode
Version: 1.2.2
"""

import asyncio
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "packages"))

from env_loader import load_env

load_env(ROOT_DIR)

# System prompt v1.2.3
CHAT_SYSTEM_PROMPT = """You are CZ Career Architect v1.2.3 - expert consultant for Czech
healthcare job applications.

USER INTAKE TEMPLATE (12 fields) - ask user to provide:
1) Purpose: specific vacancy OR talent pool
2) Document type: CV / cover letter / HR email (which kind)
3) Position + specialization
4) Employer + city (if known)
5) Profile: HR-REVIEW / MEDICAL-SENIOR-EU
6) Name (no DOB/citizenship/family/photo)
7) Location: city + country
8) Contacts: email + phone (+420)
9) Medical credentials: nostrifikace, approbation, chamber
10) Work permit status
11) Experience: 2-4 roles with dates
12) Education + languages + skills

GDPR RULES:
- Art. 5(1)(c) blocks: birth_date, age, marital_status, children, photo, nationality, full_address
- Art. 9 blocks (special category): ethnicity, religion, health_status, union_member
- Art. 87 blocks: rodne_cislo
Note: nationality is NOT Art. 9, but still blocked via Art. 5(1)(c)

CONSENT CLAUSE:
- Specific job: NOT required (Art. 6(1)(b) or 6(1)(f))
- Talent pool: Required with withdrawal option

TITLE RULE:
MDDr./MUDr. ONLY when approbation_status == "Plne aprobovan"

ATS: No tables, columns, graphics. Single language (cs-CZ).

CSN 01 6910: Dates "15. 1. 2025", Phone "+420 777 123 456", Currency "25 000 Kc"

EMPLOYER EXCEPTION:
If portal requires blocked data -> warn user, enter only in portal, never duplicate in documents.

Answer in user language. Be concise. Cite correct legal basis.
"""

INTAKE_TEMPLATE_RU = """
Заполните анкету (можно кратко, на RU/EN - переведу в cs-CZ):

1. Цель: конкретная вакансия / talent pool
2. Тип документа: CV / motivacni dopis / HR email (какой)
3. Позиция и специализация:
4. Работодатель и город:
5. Профиль: HR-REVIEW / MEDICAL-SENIOR-EU
6. Имя (без даты рождения, гражданства, фото):
7. Локация: город + страна
8. Контакты: email + телефон (+420)
9. Медстатусы: nostrifikace (+ c.j.) / approbation / komora
10. Разрешение на работу:
11. Опыт (2-4 позиции): период + роль + достижения
12. Образование + языки + навыки:
"""


class ChatAssistant:
    def __init__(self):
        from agents import Agent, ModelSettings, Runner

        self._Runner = Runner
        self.model = os.getenv("OPENAI_MODEL")
        self.agent = Agent(
            name="CZ Career Architect v1.2.3",
            instructions=CHAT_SYSTEM_PROMPT,
            model=self.model,
            model_settings=ModelSettings(),
        )

    def validate_text(self, text):
        from validators.cz_cv_validator_adapter import check_csn_typography, check_gdpr

        findings = []
        findings.extend(check_gdpr(text))
        findings.extend(check_csn_typography(text, check_nbsp=False))
        return findings

    def format_validation(self, findings):
        if not findings:
            return "No issues found"
        return "\n".join([f"[{f.level}] {f.code}: {f.message}" for f in findings])

    async def process(self, user_input):
        lower = user_input.lower()

        # Show intake template
        if any(
            w in lower
            for w in [
                "anketa",
                "template",
                "intake",
                "shablon",
                "анкет",
                "шаблон",
                "начать",
                "start",
            ]
        ):
            return INTAKE_TEMPLATE_RU

        # Validation mode
        if any(w in lower for w in ["prover", "check", "zkontroluj", "validate", "проверь"]):
            findings = self.validate_text(user_input)
            validation = self.format_validation(findings)
            prompt = (
                f'Check this text: "{user_input}"\n\nValidation:\n{validation}\n\n'
                "Explain with correct legal basis."
            )
        else:
            prompt = user_input

        result = await self._Runner.run(self.agent, prompt)
        return str(result.final_output)

    def process_sync(self, user_input):
        return asyncio.run(self.process(user_input))


def print_header():
    print()
    print("=" * 60)
    print("  CZ CAREER ARCHITECT v1.2.3 - Chat")
    print("=" * 60)
    print("  Commands: /intake, /help, /exit")
    print("-" * 60)
    print()


def main():
    print_header()
    assistant = ChatAssistant()
    print(f"Model: {assistant.model}")
    print("Type /intake to get the 12-field template\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() == "/exit":
                print("Goodbye!")
                break
            if user_input.lower() == "/intake":
                print(INTAKE_TEMPLATE_RU)
                continue
            if user_input.lower() == "/help":
                print("Commands:")
                print("  /intake - Show 12-field intake template")
                print("  /exit   - Exit chat")
                print("Examples:")
                print("  - Mozhno li ukazat grazhdanstvo?")
                print("  - Proverь: Telefon 777123456")
                print("  - Mogu pisat MDDr.?")
                continue

            print("\nAgent: ", end="", flush=True)
            response = assistant.process_sync(user_input)
            print(response)
            print()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
