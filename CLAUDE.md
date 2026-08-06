# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Builds and publishes three Salesforce-focused Docker images to Docker Hub under the `gforceinnovation` organization. sf-ci is based on `ubuntu:22.04` and sf-devcontainer on `ubuntu:24.04`, both with Node.js 24.x, OpenJDK 17, and Salesforce CLI v2. sf-bulk is Alpine-based with Node.js 24.x (no Java) for a minimal footprint.

## Images

### sf-ci
- **Purpose:** Lightweight CI/CD runner for Salesforce automation pipelines.
- **User:** `ci` (UID 1000, bash shell). **Runs non-root at runtime** — consumers must run the
  container with UID 1000 (ARC `runAsUser: 1000` / `options: --user 1000`), otherwise
  `/github/home` is unwritable.
- **SF CLI plugins:** `sfdx-git-delta`.
- **Tools:** git, jq, xmlstarlet, curl, unzip/zip.
- **Env vars:** `SFDX_CONTAINER_MODE=true`, `SFDX_DISABLE_DNS_CHECK=true`, `SF_AUTOUPDATE_DISABLE=true`, `SF_DISABLE_TELEMETRY=true`, `CI=true`.
- **Design rule:** Must stay minimal. No editors, no zsh, no interactive tools. Tests verify absence of vim/nano/zsh.

### sf-devcontainer
- **Purpose:** Full-featured VS Code devcontainer for Salesforce development.
- **User:** `vscode` (UID 1000, zsh shell, passwordless sudo).
- **SF CLI plugins:** `code-analyzer`, `sfdx-git-delta`, `sfdx-browserforce-plugin`.
- **Tools:** Everything in sf-ci plus vim, nano, wget, htop, tree, less, build-essential, openssl, gh, fzf, zoxide, eza, bat, ripgrep, fd, git-delta (system git pager), lazygit, and global prettier + prettier-plugin-apex + eslint.
- **Shell:** Zsh with Oh My Zsh, Powerlevel10k theme, zsh-autosuggestions, zsh-syntax-highlighting, zsh-completions, fzf keybindings, zoxide, SF aliases (`sfhelp`); `~/.zshrc.local` sourced last as per-dev overlay.

### sf-bulk
- **Purpose:** Ultra-lightweight Alpine-based image for bulk Salesforce org operations (no Java).
- **Base:** `node:24-alpine` with `coreutils` (needed for `env -S` in SF CLI shebang on musl/BusyBox).
- **User:** `ci` (UID 1000, bash shell) — created after removing the pre-existing `node` user from the base image.
- **SF CLI plugins:** `sfdx-git-delta`.
- **Tools:** bash, curl, git, jq, unzip, libc6-compat (gcompat).
- **Env vars:** same set as sf-ci. XDG dirs pinned to `/opt/sf-data` and `/opt/sf-config` (chmod 777).
- **Runtime:** runs as non-root `ci` (UID 1000), same as sf-ci — same runner-UID requirement.
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

### `.github/workflows/build-and-push.yml` -- Build and Push (thin caller)
- **Triggers:** PRs to `main` and version tags (`v*.*.*`). Pushes to `main` do not build.
- The per-image **build -> test -> push** pipeline lives in this repo's own
  `.github/workflows/reusable-docker-image-build.yml`; `build-and-push.yml` fans out over the
  images with a matrix and keeps the repo-specific `release` job (CHANGELOG section + per-image
  tool-version tables assembled from the `version-report-*` artifacts).
- **Path filtering:** a `changes` job computes the matrix from the PR's changed files, so a PR
  only builds the images it actually touches; a docs-only PR builds nothing. Rules:
  - `sf-<image>/**` or `tests/test_sf_<image>.py` -> that image only.
  - `.github/workflows/**`, `tests/requirements.txt`, or any other `tests/*.py` -> all images.
  - **Version tags always build all images**, so `latest` stays coherent across the set.
  - The image set lives in **one place**: the `IMAGES` JSON map in the `changes` job (key =
    image name = context dir = `tests/test_<name>.py`). Adding an image means editing that map
    only — the matrix, contexts, and Docker Hub descriptions all derive from it.
- On version tags: multi-arch push to Docker Hub with **two tags only** (`1.2.3` + `latest` —
  rolling `1.2`/`1` tags are no longer published), SBOM + provenance attestations, and a
  **keyless cosign signature** (GitHub OIDC; identity = the reusable workflow's path — renaming
  or moving that file invalidates every documented `cosign verify` command).
- Registry is **Docker Hub only** (`gforceinnovation/*`).
- Do not copy per-image pipeline logic into `build-and-push.yml` — change the reusable workflow.

### `e2e` job — critical downstream workflows

- Runs on PRs that touch **sf-ci** (the image the Salesforce pipelines use).
- Takes the **already-built** `sf-ci-image` artifact — no rebuild, so the bits under
  test are the bits the container suite just passed — retags it to a throwaway
  `ghcr.io/<owner>/sf-ci-e2e:pr-<N>`, and dispatches the real
  `weather2gp-release.yml` in `sf-develop-demo` against it, **as `--user 1001`**.
- Waits synchronously (`gh run watch --exit-status`), so a downstream failure fails
  the PR. Correlates via an `e2e-run-id` echoed into the downstream `run-name` —
  "latest run" races when two PRs overlap.
- **Quota-light on purpose:** `run-validate: false` (no scratch org) and
  `skip-validation: true` (500/day pool, not the 6/day validated-create pool).
  Each run still creates one package version and pushes a `pkg/...` provenance tag
  in `sf-develop-demo`.
- **Requires the `E2E_DISPATCH_TOKEN` secret** — a PAT/App token with `actions: write`
  on `sf-develop-demo`. `GITHUB_TOKEN` cannot dispatch cross-repo. Without it the job
  fails with an explicit message rather than silently passing.
- Container tests assert the image is internally correct; this asserts it still works
  *as a GitHub Actions container job*, which is how consumers use it. That distinction
  is why UID regressions survived the test suite before.

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
- `ubuntu:24.04`+ ships a default `ubuntu` user at UID 1000 — run `userdel -r ubuntu` before creating the image user (sf-devcontainer does this; sf-ci is still on 22.04).
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

<!-- skills-tooling -->
## Skills & AI tooling

**External skills** (lockfile-managed — update with `npx skills check` / `npx skills update`):
- `devcontainer-setup` — from trailofbits/skills
- `docker-expert` — from sickn33/antigravity-awesome-skills
- `multi-stage-dockerfile` — from github/awesome-copilot
- `platform-docs-get` — from forcedotcom/sf-skills

**Local skills** (hand-written, repo-specific):
- `building-a-docker-image`
- `releasing`
- `testing-images`
- `working-in-the-devcontainer`

**Global tooling available in every session:** lean-ctx (prefer `ctx_*` MCP tools for reads/search/shell — token-compressed), superpowers process skills, and graphify (knowledge graph present — use `graphify query`).
<!-- /skills-tooling -->
