# AI Assistant Instructions (Copilot-Optimized)

This file gives concise, high-signal guidance for AI coding assistants working in this repo.

## Project Summary
- Purpose: build and publish Salesforce-focused Docker images.
- Images:
  - `sf-devcontainer`: full-featured dev environment (interactive tools, Zsh, plugins).
  - `sf-ci`: lightweight CI image (minimal tools, non-root user).

## Repo Layout
- `sf-devcontainer/Dockerfile` + `sf-devcontainer/README.md`
- `sf-ci/Dockerfile` + `sf-ci/README.md`
- `tests/` pytest-testinfra tests (`tests/test_sf_devcontainer.py`, `tests/test_sf_ci.py`)
- `README.md`, `CONTRIBUTING.md`, `SETUP.md`
- `.github/workflows/*.yml` for CI/build+push on tag

## Local Commands
- Build dev image: `docker build -t sf-devcontainer:local ./sf-devcontainer`
- Build CI image: `docker build -t sf-ci:local ./sf-ci`
- Tests (preferred): `pytest tests/ -v`
- Test deps: `pip install -r tests/requirements.txt`

## Change Rules (Critical)
- `sf-devcontainer` can be feature-rich and interactive.
- `sf-ci` must stay minimal and non-interactive; avoid editors, shells, or UI tooling.
- When adding/removing tools:
  - Update the relevant Dockerfile.
  - Update the matching image README.
  - Add/adjust tests in `tests/test_sf_*.py`.
  - Update root `README.md` if user-facing features changed.
- Keep non-root users (`vscode`, `ci`) and existing env vars.
- Clean apt caches for small images (see `sf-ci/Dockerfile` pattern).

## Copilot Guidance (How to be "killer")
- Prefer small, reversible changes; keep Dockerfiles readable and ordered.
- Match existing patterns (Ubuntu 22.04 base, Node 20, Java 17, SF CLI).
- If downloading third-party scripts, add integrity checks when possible.
- Avoid editing `.github/workflows` unless explicitly requested.
- Use conventional commits when asked to prepare commit messages.

## Quick Context for Tests
- Tests validate OS, language runtimes, SF CLI, plugins, tools, user config, and env vars.
- If a feature is added, add a corresponding test assertion.
