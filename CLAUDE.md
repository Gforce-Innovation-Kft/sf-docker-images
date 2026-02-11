# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Builds and publishes two Salesforce-focused Docker images to Docker Hub under the `gforceinnovation` organization. Both are based on `ubuntu:22.04` with Node.js 20.x, OpenJDK 17, and Salesforce CLI v2.

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

Both images set `WORKDIR /workspace`, include a `HEALTHCHECK` using `sf version --json`, and have `.dockerignore` files.

## Key Commands

```bash
# Build locally
docker build -t sf-ci:local ./sf-ci
docker build -t sf-devcontainer:local ./sf-devcontainer

# Run tests (pytest-testinfra)
pip install -r tests/requirements.txt
pytest tests/ -v
pytest tests/test_sf_ci.py -v          # single image
pytest tests/test_sf_devcontainer.py -v # single image

# Multi-platform build and push (requires buildx)
docker buildx create --name multiplatform --use
docker buildx build --platform linux/amd64,linux/arm64 --tag gforceinnovation/sf-ci:latest --push ./sf-ci
docker buildx build --platform linux/amd64,linux/arm64 --tag gforceinnovation/sf-devcontainer:latest --push ./sf-devcontainer
```

## CI/CD Workflows

### `.github/workflows/build-and-push.yml` -- Build and Push
- **Triggers:** Push to `main`, PRs to `main`, and version tags (`v*.*.*`).
- **Jobs:** dependency-review -> build (matrix) -> test (pytest-testinfra + Trivy) -> push (Docker Hub on version tags only).
- Pushes with semver tags (e.g., `1.2.3`, `1.2`, `1`, `latest`). Generates SBOM and provenance attestations.

### Release Process
```bash
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

## Testing

Tests use **pytest-testinfra** (in `tests/`). Each test file builds the image, starts a container, and verifies: OS version, user/UID/shell, runtimes (Node, Java, SF CLI), plugins, tools, env vars, directory structure. sf-ci tests verify vim/nano/zsh are NOT installed.

## Change Rules

- When adding/removing tools: update the Dockerfile, the image's README, and add/adjust tests in `tests/test_sf_*.py`.
- sf-ci must stay minimal; sf-devcontainer can be feature-rich.
- Clean apt caches in the same `RUN` layer (`rm -rf /var/lib/apt/lists/*`).
- Commit messages follow conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`).
- A pre-commit hook runs yamllint on staged YAML files. Config in `.yamllint` (max line length 120, 2-space indent).
