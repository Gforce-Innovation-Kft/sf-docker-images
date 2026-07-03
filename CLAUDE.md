# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Builds and publishes three Salesforce-focused Docker images to Docker Hub under the `gforceinnovation` organization. sf-ci and sf-devcontainer are based on `ubuntu:22.04` with Node.js 24.x, OpenJDK 17, and Salesforce CLI v2. sf-bulk is Alpine-based with Node.js 24.x (no Java) for a minimal footprint.

## Images

### sf-ci
- **Purpose:** Lightweight CI/CD runner for Salesforce automation pipelines.
- **User:** `ci` (UID 1000, bash shell, non-root).
- **SF CLI plugins:** `sfdx-git-delta`.
- **Tools:** git, jq, xmlstarlet, curl, unzip/zip.
- **Env vars:** `SFDX_CONTAINER_MODE=true`, `SFDX_DISABLE_DNS_CHECK=true`, `SF_AUTOUPDATE_DISABLE=true`, `SF_DISABLE_TELEMETRY=true`, `CI=true`.
- **Design rule:** Must stay minimal. No editors, no zsh, no interactive tools. Tests verify absence of vim/nano/zsh.

### sf-devcontainer
- **Purpose:** Full-featured VS Code devcontainer for Salesforce development.
- **User:** `vscode` (UID 1000, zsh shell, passwordless sudo).
- **SF CLI plugins:** `code-analyzer`, `sfdx-git-delta`, `sfdx-browserforce-plugin`.
- **Tools:** Everything in sf-ci plus vim, nano, wget, htop, tree, less, build-essential, openssl.
- **Shell:** Zsh with Oh My Zsh, Powerlevel10k theme, zsh-autosuggestions, zsh-syntax-highlighting, zsh-completions.

### sf-bulk
- **Purpose:** Ultra-lightweight Alpine-based image for bulk Salesforce org operations (no Java).
- **Base:** `node:24-alpine` with `coreutils` (needed for `env -S` in SF CLI shebang on musl/BusyBox).
- **User:** `ci` (UID 1000, bash shell) — created after removing the pre-existing `node` user from the base image.
- **SF CLI plugins:** `sfdx-git-delta`.
- **Tools:** bash, curl, git, jq, unzip, libc6-compat (gcompat).
- **Env vars:** same set as sf-ci. XDG dirs pinned to `/opt/sf-data` and `/opt/sf-config` (chmod 777).
- **Runtime:** runs as root (bypasses ARC dind UID mismatch, same as sf-ci).
- **Design rule:** No Java, no editors, no interactive tools. Must stay under 600MB uncompressed.

All three images set `WORKDIR /workspace`, include a `HEALTHCHECK` using `sf version --json`, and have `.dockerignore` files.

## Key Commands

```bash
# Build locally
docker build -t sf-ci:local ./sf-ci
docker build -t sf-devcontainer:local ./sf-devcontainer
docker build -t sf-bulk:local ./sf-bulk

# Run container tests (pytest-testinfra)
pip install -r tests/requirements.txt
pytest tests/ -v
pytest tests/test_sf_ci.py -v          # single image
pytest tests/test_sf_devcontainer.py -v # single image
pytest tests/test_sf_bulk.py -v         # single image

# Multi-platform build and push (requires buildx)
docker buildx create --name multiplatform --use
docker buildx build --platform linux/amd64,linux/arm64 --tag gforceinnovation/sf-ci:latest --push ./sf-ci
docker buildx build --platform linux/amd64,linux/arm64 --tag gforceinnovation/sf-devcontainer:latest --push ./sf-devcontainer
docker buildx build --platform linux/amd64,linux/arm64 --tag gforceinnovation/sf-bulk:latest --push ./sf-bulk
```

## CI/CD Workflows

### `.github/workflows/build-and-push.yml` -- Build and Push
- **Triggers:** Push to `main`, PRs to `main`, and version tags (`v*.*.*`).
- **Jobs:** dependency-review -> build (matrix) -> test (pytest-testinfra + Trivy) -> push (Docker Hub on version tags only) -> release (GitHub Release on version tags only).
- Pushes with semver tags (e.g., `1.2.3`, `1.2`, `1`, `latest`). Generates SBOM and provenance attestations.
- Registry is **Docker Hub only** (`gforceinnovation/*`).

### Release Process
```bash
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

## Testing

Tests use **pytest-testinfra** (in `tests/`). Each `tests/test_sf_*.py` builds the image, starts a
container, and verifies: OS version, user/UID/shell, runtimes (Node, Java, SF CLI), plugins, tools,
env vars, and directory structure. sf-ci tests verify vim/nano/zsh are NOT installed; sf-bulk tests
verify Java is NOT installed and the image is under 600 MB.

## Change Rules

- When adding/removing tools: update the Dockerfile, the image's README, and add/adjust tests in `tests/test_sf_*.py`.
- sf-ci must stay minimal; sf-devcontainer can be feature-rich; sf-bulk must stay under 600MB with no Java.
- Alpine images: use `apk add --no-cache` and include `coreutils` (needed for `env -S` in SF CLI shebang).
- Alpine images: `node:24-alpine` ships a `node` user at UID 1000 — run `deluser node` before creating `ci`.
- Ubuntu images: clean apt caches in the same `RUN` layer (`rm -rf /var/lib/apt/lists/*`).
- Commit messages follow conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`).
- A pre-commit hook (`.github/hooks/pre-commit`, activated by `scripts/setup.sh` via
  `core.hooksPath`) runs yamllint on staged YAML files (blocking) and refreshes the graphify graph
  (non-blocking). Config in `.yamllint` (max line length 120, 2-space indent).

## AI Pair-Development Layer

This repo is set up to be developed with Claude Code. The loop is: **CLAUDE.md → references → skills → tests → release.**

- **`.claude/references/`** — read before generating code:
  [`docker-best-practices.md`](.claude/references/docker-best-practices.md),
  [`image-conventions.md`](.claude/references/image-conventions.md) (per-image size budgets +
  allowed/forbidden tools), [`github-actions.md`](.claude/references/github-actions.md),
  [`devops.md`](.claude/references/devops.md).
- **`.claude/skills/`** — repo skills: `building-a-docker-image`, `testing-images`, `releasing`,
  and `working-in-the-devcontainer` (vendored, attributed).
- **`.agents/skills/`** — ecosystem skills vendored via the skills CLI (`npx skills add`), symlinked
  into `.claude/skills/` and pinned in `skills-lock.json`: `docker-expert`
  (sickn33/antigravity-awesome-skills), `multi-stage-dockerfile` (github/awesome-copilot),
  `devcontainer-setup` (trailofbits/skills), `platform-docs-get` (forcedotcom/sf-skills).
  Use `docker-expert` + `multi-stage-dockerfile` when reviewing/changing Dockerfiles,
  `devcontainer-setup` for `.devcontainer/` work, `platform-docs-get` for official Salesforce docs.
- **`.claude/settings.json`** — committed permission allow-list. `settings.local.json` is git-ignored.
- **`scripts/setup.sh`** — one-command bootstrap: verifies Docker + Python + `gh`, installs test
  deps, and prints the recommended external Claude skills to install.

## Knowledge Graph (graphify)

This repo ships a [graphify](https://github.com/) knowledge graph in `graphify-out/` so Claude
answers codebase questions from a **scoped subgraph** instead of grepping/reading whole files —
this is the token-management win. See [`.claude/references/graphify.md`](.claude/references/graphify.md).

- **For codebase questions**, run `graphify query "<question>"` (scoped subgraph, usually much
  smaller than raw grep/reads). Use `graphify explain "<concept>"` for one node + neighbors and
  `graphify path "<A>" "<B>"` for relationships. Read `graphify-out/GRAPH_REPORT.md` only for a
  broad architecture pass.
- **After modifying code**, run `graphify update .` to keep the graph current (AST-only, no API cost).
- `graphify-out/` is a **local build artifact and is git-ignored** — regenerated by
  `scripts/setup.sh` and the pre-commit hook, not committed.
