# AGENTS.md

## Interaction Contract

- For questions, planning, tradeoff analysis, or brainstorming: do not edit files and do not run modifying commands. Read-only commands are allowed.
- In those cases, respond with analysis, options, or a plan only.
- Implement only when the user gives an explicit execution instruction (`implement`, `apply`, `proceed`, or equivalent).
- If intent is ambiguous, ask one short clarification question.
- Never infer implementation intent from context alone.
- Silence is not consent to edit code.

## Working Style

- Make minimal, focused diffs.
- Do not modify unrelated files.
- Avoid broad refactors unless requested.

## Project Map

- Library code: `erdantic/`
- Plugins: `erdantic/plugins/`
- CLI: `erdantic/cli.py`
- Tests: `tests/`
- Static test assets: `tests/assets/`
- Asset generators: `tests/scripts/generate_static_assets.py`, `tests/scripts/generate_pydantic_with_defaults_assets.py`

## Commands

- Setup/sync: `just sync`
- Lint: `just lint`
- Format: `just format`
- Typecheck: `just typecheck`
- Tests (default py3.13): `just test`
- Tests (specific Python): `just python=3.12 test`
- Full matrix: `just test-all`
- Test commands accept pytest args, e.g.:
  - `just test tests/test_against_assets.py -k pydantic`
  - `just test-all tests/test_against_assets.py`

## Testing Expectations

- Behavior changes must include or update tests.
- If expected rendered outputs change, ask for user permission before running `just generate-static-assets`.
- Review `tests/assets/` diffs carefully.
- Prefer targeted test runs while iterating, then run the relevant broader suite.

## Notes

- Graphviz/PyGraphviz is required. Pixi activation automatically runs `scripts/fix_graphviz.sh`.
- Python-version differences matter (`3.9` through `3.14`).
- Some tests validate generated artifacts, not just runtime behavior.
