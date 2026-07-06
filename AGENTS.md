# AI Assistant Instructions (Copilot-Optimized)

This file gives concise, high-signal guidance for AI coding assistants working in this repo.

## Project Summary
- Purpose: build and publish Salesforce-focused Docker images.
- Images:
  - `sf-devcontainer`: full-featured dev environment (interactive tools, Zsh, plugins).
  - `sf-ci`: lightweight CI image (minimal tools, non-root user, root runtime).
  - `sf-bulk`: ultralight Alpine image (no Java, must stay under 600MB).

## Repo Layout
- `sf-devcontainer/Dockerfile` + `sf-devcontainer/README.md`
- `sf-ci/Dockerfile` + `sf-ci/README.md`
- `sf-bulk/Dockerfile` + `sf-bulk/README.md`
- `tests/` pytest-testinfra container tests (`tests/test_sf_ci.py`, `tests/test_sf_devcontainer.py`, `tests/test_sf_bulk.py`)
- `.claude/references/*` (rules) and `.claude/skills/*` (repo skills)
- `README.md`, `CONTRIBUTING.md`, `SETUP.md`, `CLAUDE.md`
- `.github/workflows/*.yml` for CI/build+test+push+release on tag

## Local Commands
- Build dev image: `docker build -t sf-devcontainer:local ./sf-devcontainer`
- Build CI image: `docker build -t sf-ci:local ./sf-ci`
- Build bulk image: `docker build -t sf-bulk:local ./sf-bulk`
- Tests (preferred): `pytest tests/ -v`
- Test deps: `pip install -r tests/requirements.txt`
- Bootstrap: `scripts/setup.sh`

## Change Rules (Critical)
- `sf-devcontainer` can be feature-rich and interactive.
- `sf-ci` must stay minimal and non-interactive; avoid editors, shells, or UI tooling.
- When adding/removing tools:
  - Update the relevant Dockerfile.
  - Update the matching image README.
  - Add/adjust tests in `tests/test_sf_*.py`.
  - Update root `README.md` if user-facing features changed.
- `sf-bulk` must stay under 600MB with no Java.
- Keep the `vscode`/`ci` users (UID 1000) and existing env vars; `sf-ci`/`sf-bulk` run as root at runtime.
- Clean apt caches for small images (see `sf-ci/Dockerfile` pattern).

## Copilot Guidance (How to be "killer")
- Prefer small, reversible changes; keep Dockerfiles readable and ordered.
- Match existing patterns (Ubuntu 22.04 base, Node 24, Java 17, SF CLI).
- If downloading third-party scripts, add integrity checks when possible.
- Avoid editing `.github/workflows` unless explicitly requested.
- Use conventional commits when asked to prepare commit messages.

## Quick Context for Tests
- Tests validate OS, language runtimes, SF CLI, plugins, tools, user config, and env vars.
- If a feature is added, add a corresponding test assertion.
