# Repository Guidelines

## Project Structure & Module Organization
Runtime entry points live at the repo root: `chat.py` (interactive intake) and `main.py` (batch generation/validation). Core logic and orchestration live alongside them in `pipeline.py`, `sdk.py`, and `assistant_runner.py`, with a local OpenAI wrapper in `agents.py`. Domain assets live in `packages/` (prompts, types, validators), while `Schemas/` holds profiles, validation references, and rules knowledge. `Examples/` contains reference CVs, cover letters, and HR emails used as training/examples. Generated outputs should go under `out/` when applicable.

## Build, Test, and Development Commands
- `python chat.py`: run the interactive intake flow.
- `python main.py --validate`: generate and validate a full package.
- `python main.py --mode check --text "Datum narozeni: 15.1.1985"`: run a validator check on a single text snippet.
- `python main.py --help`: list all supported modes and flags.

### Local dev environment
```bash
cd base_for_agent_cv
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements_api.txt -r requirements_dev.txt
pre-commit install
```

### Quality gates
```bash
cd base_for_agent_cv
ruff check .
black --check .
pytest
```

There is no separate build step; scripts run directly with Python.

## Coding Style & Naming Conventions
Use Python 3.9+ with 4-space indentation. Prefer `snake_case` for functions/modules, `PascalCase` for classes, and `UPPER_SNAKE` for constants. Keep prompts and schemas in their respective `packages/` and `Schemas/` paths; when you change validator logic, update related rules or schema references in the same change.

## Testing Guidelines
No automated test suite is currently configured. Use `python main.py --validate` as a smoke check after changes, and add focused regression examples under `Examples/` when you adjust prompts or validators. If you introduce a test suite in the future, place it under `tests/` and use `test_<behavior>.py` naming.

## Commit & Pull Request Guidelines
Follow the existing imperative style in commit history (e.g., “Add assistant smoke check runner”). Keep commits scoped and include a brief validation note in PR descriptions (command + outcome). If you change prompts or schemas, note whether any example assets were updated to reflect the new behavior.

## Security & Configuration Tips
Set credentials such as `OPENAI_API_KEY` via environment variables or local `.env` files that are not committed. Avoid embedding API keys or user data in prompts, schemas, or examples.
