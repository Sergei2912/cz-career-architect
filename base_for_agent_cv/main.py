#!/usr/bin/env python3
"""
CZ Career Architect - Main Entry Point
Version: 1.2.2
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "packages"))

env_path = ROOT_DIR / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key, val = line.split("=", 1)
            os.environ[key] = val


def parse_args():
    parser = argparse.ArgumentParser(
        description="CZ Career Architect v1.2.3 - HR Document Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Generate full package
  python main.py --validate         # With validation
  python main.py --mode chat        # Interactive chat
  python main.py --mode check --text "..."
        """,
    )
    parser.add_argument(
        "--mode", choices=["full_package", "chat", "check", "rewrite"], default="full_package"
    )
    parser.add_argument("--text", type=str)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=ROOT_DIR / "out")
    return parser.parse_args()


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


async def mode_full_package(args):
    from validators.cz_cv_validator_adapter import (
        apply_fixes_to_text,
        build_summary,
        check_csn_typography,
        check_gdpr,
    )

    from agents import Agent, ModelSettings, Runner

    print("=" * 60)
    print("CZ CAREER ARCHITECT v1.2.3 - Full Package")
    print("=" * 60)

    model = os.getenv("OPENAI_MODEL")
    print(f"Model: {model}")

    agent = Agent(
        name="CZ Career Architect v1.2.3",
        instructions=SYSTEM_PROMPT,
        model=model,
        model_settings=ModelSettings(),
    )

    user_request = """
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

    print("\nGenerating...")
    result = await Runner.run(agent, user_request)
    output = apply_fixes_to_text(str(result.final_output), enable_nbsp=False)

    if args.validate:
        print("\nValidating...")
        findings = []
        findings.extend(check_gdpr(output))
        findings.extend(check_csn_typography(output, check_nbsp=False))
        summary = build_summary(findings)
        summary_line = (
            f"  CRITICAL: {summary['CRITICAL']}, ERROR: {summary['ERROR']}, "
            f"WARNING: {summary['WARNING']}"
        )
        print(summary_line)
        if findings:
            for f in findings:
                print(f"    [{f.level}] {f.code}")

    args.output_dir.mkdir(exist_ok=True)
    (args.output_dir / "full_package.md").write_text(output, encoding="utf-8")
    print(f"\nSaved: {args.output_dir}/full_package.md")
    print("\n" + "=" * 60)
    print(output)


def mode_chat(args):
    from chat import main as chat_main

    chat_main()


async def mode_check(args):
    from validators.cz_cv_validator_adapter import build_summary, check_csn_typography, check_gdpr

    text = args.text or sys.stdin.read()
    if not text.strip():
        print('No text. Use --text "..."')
        return

    print("CZ CAREER ARCHITECT v1.2.3 - Validation")
    print(f"Text: {text[:80]}..." if len(text) > 80 else f"Text: {text}")

    findings = check_gdpr(text) + check_csn_typography(text, check_nbsp=False)

    if not findings:
        print("\n✅ No issues")
    else:
        summary = build_summary(findings)
        summary_line = (
            f"\n❌ {summary['CRITICAL']} critical, {summary['ERROR']} errors, "
            f"{summary['WARNING']} warnings"
        )
        print(summary_line)
        for f in findings:
            print(f"  [{f.level}] {f.code}: {f.message}")


async def mode_rewrite(args):
    from agents import Agent, ModelSettings, Runner

    text = args.text or sys.stdin.read()
    if not text.strip():
        print("No text.")
        return

    agent = Agent(
        name="Rewriter",
        instructions="Rewrite for Czech CV. Output Czech only. CSN typography.",
        model=os.getenv("OPENAI_MODEL"),
        model_settings=ModelSettings(),
    )

    print(f"Original: {text}")
    result = await Runner.run(agent, f"Rewrite: {text}")
    print(f"Result: {result.final_output}")


async def main():
    args = parse_args()
    if args.mode == "full_package":
        await mode_full_package(args)
    elif args.mode == "chat":
        mode_chat(args)
    elif args.mode == "check":
        await mode_check(args)
    elif args.mode == "rewrite":
        await mode_rewrite(args)


if __name__ == "__main__":
    asyncio.run(main())
