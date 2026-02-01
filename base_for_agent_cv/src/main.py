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

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "packages"))

from src.sdk.utils import load_env_file, ensure_output_dir, save_output
from src.sdk.model import create_agent, get_runner, get_model_name
from src.pipeline.validator import validate_text, apply_validation_fixes
from src.pipeline.generator import SYSTEM_PROMPT, generate_full_package, get_default_user_request

load_env_file()


def parse_args():
    parser = argparse.ArgumentParser(
        description="CZ Career Architect v1.2.3 - HR Document Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py                    # Generate full package
  python src/main.py --validate         # With validation
  python src/main.py --mode chat        # Interactive chat
  python src/main.py --mode check --text "..."
        """,
    )
    parser.add_argument(
        "--mode", choices=["full_package", "chat", "check", "rewrite"], default="full_package"
    )
    parser.add_argument("--text", type=str)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=ROOT_DIR / "out")
    return parser.parse_args()


async def mode_full_package(args):
    print("=" * 60)
    print("CZ CAREER ARCHITECT v1.2.3 - Full Package")
    print("=" * 60)

    model = get_model_name()
    print(f"Model: {model}")

    agent = create_agent("CZ Career Architect v1.2.3", SYSTEM_PROMPT, model)
    user_request = get_default_user_request()
    
    Runner = get_runner()

    print("\nGenerating...")
    result = await generate_full_package(agent, user_request, Runner)
    output = apply_validation_fixes(result, enable_nbsp=False)

    if args.validate:
        print("\nValidating...")
        findings, summary_line = validate_text(output, enable_nbsp=False)
        print(summary_line)
        if findings:
            for f in findings:
                print(f"    [{f.level}] {f.code}")

    ensure_output_dir(args.output_dir)
    save_output(output, args.output_dir / "full_package.md")
    print(f"\nSaved: {args.output_dir}/full_package.md")
    print("\n" + "=" * 60)
    print(output)


def mode_chat(args):
    from src.chat import main as chat_main

    chat_main()


async def mode_check(args):
    text = args.text or sys.stdin.read()
    if not text.strip():
        print('No text. Use --text "..."')
        return

    print("CZ CAREER ARCHITECT v1.2.3 - Validation")
    print(f"Text: {text[:80]}..." if len(text) > 80 else f"Text: {text}")

    findings, summary_line = validate_text(text, enable_nbsp=False)

    if not findings:
        print("\n✅ No issues")
    else:
        print(f"\n❌ {summary_line}")
        for f in findings:
            print(f"  [{f.level}] {f.code}: {f.message}")


async def mode_rewrite(args):
    text = args.text or sys.stdin.read()
    if not text.strip():
        print("No text.")
        return

    agent = create_agent(
        "Rewriter",
        "Rewrite for Czech CV. Output Czech only. CSN typography.",
        get_model_name()
    )
    
    Runner = get_runner()

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
