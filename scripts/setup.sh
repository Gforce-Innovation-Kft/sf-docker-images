#!/usr/bin/env bash
#
# setup.sh — bootstrap sf-docker-images for AI pair-development.
#
# Verifies Docker + Python + gh, checks the vendored Claude skill, and prints the
# recommended external Claude skills to install. Idempotent and safe to re-run.
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# --- pretty output -----------------------------------------------------------
info()  { printf '\033[0;34m==>\033[0m %s\n' "$*"; }
ok()    { printf '\033[0;32m ok\033[0m %s\n' "$*"; }
warn()  { printf '\033[0;33m  !\033[0m %s\n' "$*"; }
fail()  { printf '\033[0;31m  x\033[0m %s\n' "$*" >&2; }

MISSING=0

# --- prerequisites -----------------------------------------------------------
info "Checking prerequisites"

if command -v docker >/dev/null 2>&1; then
  ok "docker: $(docker --version)"
  if docker info >/dev/null 2>&1; then
    ok "docker daemon reachable"
  else
    warn "docker installed but daemon not reachable (start Docker Desktop)"
  fi
else
  fail "docker not found — install Docker: https://docs.docker.com/get-docker/"
  MISSING=1
fi

if command -v python3 >/dev/null 2>&1; then
  ok "python3: $(python3 --version)"
else
  fail "python3 not found — the pytest-testinfra tests need Python 3.8+"
  MISSING=1
fi

if command -v gh >/dev/null 2>&1; then
  ok "gh: $(gh --version | head -1)"
else
  warn "gh (GitHub CLI) not found — needed for releases: https://cli.github.com/"
fi

# --- install container test dependencies -------------------------------------
info "Installing container test dependencies (pytest-testinfra)"
if command -v python3 >/dev/null 2>&1; then
  if python3 -m pip install -r "$REPO_ROOT/tests/requirements.txt" >/dev/null 2>&1; then
    ok "installed tests/requirements.txt"
  else
    warn "could not install test deps automatically — run: pip install -r tests/requirements.txt"
  fi
fi

# --- vendored Claude skill ---------------------------------------------------
info "Checking vendored Claude skill"
if [ -f ".claude/skills/working-in-the-devcontainer/SKILL.md" ]; then
  ok "working-in-the-devcontainer skill present (see its ATTRIBUTION.md)"
else
  warn "vendored devcontainer skill missing at .claude/skills/working-in-the-devcontainer/"
fi

# --- git hooks (yamllint) ----------------------------------------------------
info "Activating tracked git hooks"
if [ -d "$REPO_ROOT/.git" ]; then
  git -C "$REPO_ROOT" config core.hooksPath .github/hooks \
    && ok "core.hooksPath -> .github/hooks (pre-commit: yamllint)" \
    || warn "could not set core.hooksPath"
else
  warn "not a git working copy — skipping hook activation"
fi

# --- shared AI layer (lockfile-managed) --------------------------------------
info "Syncing shared skills from skills-lock.json"
if [ -f "$REPO_ROOT/skills-lock.json" ]; then
  if npx --yes skills check >/dev/null 2>&1; then
    ok "skills in sync with skills-lock.json"
  else
    warn "could not sync skills — run: npx skills check"
  fi
else
  warn "no skills-lock.json — the shared AI layer is not installed in this repo"
fi

# --- summary -----------------------------------------------------------------
if [ "$MISSING" -ne 0 ]; then
  fail "Some prerequisites are missing — install them and re-run scripts/setup.sh"
  exit 1
fi

info "Next steps"
cat <<EOF
  1. Build the images:   docker build -t sf-ci:test ./sf-ci   (and sf-devcontainer, sf-bulk)
  2. Run the tests:      pytest tests/ -v
  3. Read the rules:     .claude/references/  and  .claude/skills/
                         (.claude/references/local-standards.md is the L3 override —
                          the gforce-github-actions skill reads it last and it wins)
  4. Open in VS Code:    "Reopen in Container" (uses .devcontainer/devcontainer.json)
EOF
ok "Setup complete"
