#!/usr/bin/env bash
#
# setup.sh — bootstrap sf-docker-images for AI pair-development.
#
# Verifies Docker + Node 20 + gh, checks the vendored Claude skill, and prints the
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

# --- graphify knowledge graph (token-efficient codebase navigation) ----------
info "Setting up graphify knowledge graph"
if command -v graphify >/dev/null 2>&1; then
  ok "graphify: $(graphify --version 2>/dev/null || echo present)"
  # Install the graphify skill into Claude's config (idempotent)
  graphify install --platform claude >/dev/null 2>&1 \
    && ok "graphify skill installed for Claude" \
    || warn "could not install graphify skill (run: graphify install --platform claude)"
  # Build/refresh the graph (AST-only, no API cost)
  graphify update . >/dev/null 2>&1 \
    && ok "graph built/refreshed at graphify-out/graph.json" \
    || warn "could not build graph (run: graphify update .)"
else
  warn "graphify not found — install it, then: graphify install --platform claude && graphify update ."
  warn "the committed graphify-out/graph.json still powers query/explain/path without a local rebuild"
fi

# --- git hooks (yamllint + graphify refresh) ---------------------------------
info "Activating tracked git hooks"
if [ -d "$REPO_ROOT/.git" ]; then
  git -C "$REPO_ROOT" config core.hooksPath .github/hooks \
    && ok "core.hooksPath -> .github/hooks (pre-commit: yamllint + graphify refresh)" \
    || warn "could not set core.hooksPath"
else
  warn "not a git working copy — skipping hook activation"
fi

# --- recommended external Claude skills (manual, opt-in) ---------------------
info "Recommended external Claude skills (run these yourself to install):"
cat <<'EOF'

  # ci-cd — GitHub Actions pipeline design/caching/security
  /plugin marketplace add https://github.com/ahmedasmar/devops-claude-skills
  /plugin install ci-cd@devops-skills

  # github-actions-manager — drive workflows via gh (watch runs, pull logs, rerun)
  #   see https://mcpmarket.com/tools/skills/github-actions-manager

  # forcedotcom/sf-skills — Salesforce dev skills for the devcontainer use case
  npx skills add forcedotcom/sf-skills

EOF

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
  4. Query the graph:    graphify query "how are the images built?"   (token-efficient)
  5. Open in VS Code:    "Reopen in Container" (uses .devcontainer/devcontainer.json)
EOF
ok "Setup complete"
