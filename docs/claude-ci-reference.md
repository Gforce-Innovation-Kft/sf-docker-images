# CI/CD & build reference (moved from CLAUDE.md)

Relocated from CLAUDE.md on 2026-08-08 to keep always-loaded context lean.
Read this when working on the workflows, the E2E gate, or local builds.

## Local build & test commands

```bash
# Build locally
docker build -t sf-ci:local ./sf-ci
docker build -t sf-devcontainer:local ./sf-devcontainer
docker build -t sf-bulk:local ./sf-bulk

# Run container tests (pytest-testinfra)
pip install -r tests/requirements.txt
pytest tests/ -v
pytest tests/test_sf_ci.py -v           # single image
pytest tests/test_sf_devcontainer.py -v # single image
pytest tests/test_sf_bulk.py -v         # single image

# Multi-platform build and push (requires buildx)
docker buildx create --name multiplatform --use
docker buildx build --platform linux/amd64,linux/arm64 --tag gforceinnovation/sf-ci:latest --push ./sf-ci
docker buildx build --platform linux/amd64,linux/arm64 --tag gforceinnovation/sf-devcontainer:latest --push ./sf-devcontainer
docker buildx build --platform linux/amd64,linux/arm64 --tag gforceinnovation/sf-bulk:latest --push ./sf-bulk
```

## Per-image details

### sf-ci
- **Purpose:** Lightweight CI/CD runner for Salesforce automation pipelines.
- **User:** `ci` (UID 1000, bash shell). **Runs non-root at runtime** — consumers must run the container with UID 1000 (ARC `runAsUser: 1000` / `options: --user 1000`), otherwise `/github/home` is unwritable.
- **SF CLI plugins:** `sfdx-git-delta`.
- **Tools:** git, jq, xmlstarlet, curl, unzip/zip.
- **Env vars:** `SFDX_CONTAINER_MODE=true`, `SFDX_DISABLE_DNS_CHECK=true`, `SF_AUTOUPDATE_DISABLE=true`, `SF_DISABLE_TELEMETRY=true`, `CI=true`.

### sf-devcontainer
- **Purpose:** Full-featured VS Code devcontainer for Salesforce development.
- **User:** `vscode` (UID 1000, zsh shell, passwordless sudo).
- **SF CLI plugins:** `code-analyzer`, `sfdx-git-delta`, `sfdx-browserforce-plugin`.
- **Tools:** Everything in sf-ci plus vim, nano, wget, htop, tree, less, build-essential, openssl, gh, fzf, zoxide, eza, bat, ripgrep, fd, git-delta (system git pager), lazygit, and global prettier + prettier-plugin-apex + eslint.
- **Shell:** Zsh with Starship, zsh-autosuggestions and zsh-syntax-highlighting, no framework, fzf keybindings, zoxide, SF aliases (`sfhelp`); `~/.zshrc.local` sourced last as per-dev overlay. The prompt shows the project's Salesforce target org, read from `.sf/config.json` with `jq` (never by calling `sf`, which would add ~500 ms of Node startup per prompt).

### sf-bulk
- **Purpose:** Ultra-lightweight Alpine-based image for bulk Salesforce org operations (no Java).
- **Base:** `node:24-alpine` with `coreutils` (needed for `env -S` in SF CLI shebang on musl/BusyBox).
- **User:** `ci` (UID 1000, bash shell) — created after removing the pre-existing `node` user from the base image.
- **SF CLI plugins:** `sfdx-git-delta`.
- **Tools:** bash, curl, git, jq, unzip, libc6-compat (gcompat).
- **Env vars:** same set as sf-ci. XDG dirs pinned to `/opt/sf-data` and `/opt/sf-config` (chmod 777).
- **Runtime:** runs as non-root `ci` (UID 1000) — same runner-UID requirement as sf-ci.

All three images set `WORKDIR /workspace`, include a `HEALTHCHECK` using `sf version --json`, and have `.dockerignore` files.

## CI/CD workflow details

- **Path filtering is GitHub's own** (`on.pull_request.paths`), not a `changes` job. A PR only starts the workflows for images it touches; a docs-only PR starts nothing. Separate workflows are inherently parallel.
- Each image workflow filters on its own dir, its own `tests/test_<name>.py`, **and** the shared inputs (`tests/requirements.txt`, the reusable workflow, itself).
- **Tags build every image**, so `latest` stays coherent — which is why the tag path keeps a matrix instead of splitting per image. That duplication of the image list is the deliberate cost of the split.
- PRs never push (`push: false`); `release.yml` is the only publisher.
- On version tags: multi-arch push to Docker Hub with **two tags only** (`1.2.3` + `latest` — rolling `1.2`/`1` tags are no longer published), SBOM + provenance attestations, and a **keyless cosign signature** (GitHub OIDC; identity = the reusable workflow's path — renaming or moving that file invalidates every documented `cosign verify` command).
- Registry is **Docker Hub only** (`gforceinnovation/*`); GHCR is used solely for throwaway E2E candidates.

## E2E gate — two tiers, both blocking (`image-sf-ci.yml`)

Only sf-ci carries it: it is the image the Salesforce pipelines run in.

```
image -> publish-candidate -> e2e-container -> e2e-workflows -> cleanup
```

- **`publish-candidate`** takes the **already-built** `sf-ci-image` artifact — no rebuild, so the bits under test are the bits the container suite just passed — and pushes it to a throwaway `ghcr.io/<owner>/sf-ci-e2e:pr-<N>`. Everything downstream needs to *pull* it: a container job takes a registry reference, not a loaded image.
- **Tier 1 `e2e-container`** is a real GitHub Actions container job on that image, **`--user 1001`**. Probes the runner file-command paths, `$HOME`, `sf version`/`plugins`, and `sfdx-git-delta` (the `sf-source-delta` code path) — no secrets, no org, no quota. `tests/` runs `docker run`, so it cannot see what GitHub does to a container job: bind-mounting `/github/home` and the file-command dir owned by the runner's UID. **Every regression this image has actually shipped lived in that gap.**
- **Tier 2 `e2e-workflows`** dispatches real downstream pipelines against the candidate and blocks on them (`gh run watch --exit-status`), so a downstream failure fails the PR. Correlates via an `e2e-run-id` echoed into the downstream `run-name` — "latest run" races when two PRs overlap. **Add a critical workflow by adding a `matrix.target` entry**; nothing else changes.
- Tier 1 gates tier 2, so a container that cannot run `sf` fails in ~1 minute instead of spending a package-version create.
- **Quota-light on purpose:** `run-validate: false` (no scratch org) and `skip-validation: true` (500/day pool, not the 6/day validated-create pool). Each run still creates one package version and pushes a `pkg/...` provenance tag in `sf-develop-demo`.
- **Requires the `E2E_DISPATCH_TOKEN` secret** — a PAT/App token with `actions: write` on `sf-develop-demo`. `GITHUB_TOKEN` cannot dispatch cross-repo. Without it the job fails with an explicit message rather than silently passing.
- `cleanup` deletes the throwaway GHCR tag on `always()`, whichever tier failed.

## Release process

```bash
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

## AI pair-development layer details

- **`.claude/references/`** — read before generating code: `docker-best-practices.md`, `image-conventions.md` (per-image size budgets + allowed/forbidden tools), `github-actions.md`, `devops.md`.
- **`.claude/skills/`** — repo skills: `building-a-docker-image`, `testing-images`, `releasing`, `working-in-the-devcontainer`.
- **`.agents/skills/`** — ecosystem skills vendored via the skills CLI, symlinked into `.claude/skills/`, pinned in `skills-lock.json`.
- **`.claude/settings.json`** — committed permission allow-list. `settings.local.json` is git-ignored.
- **`scripts/setup.sh`** — one-command bootstrap: verifies Docker + Python + `gh`, installs test deps, prints recommended external skills.
- **graphify:** `graphify-out/` is a local, git-ignored build artifact regenerated by `scripts/setup.sh` and the pre-commit hook. `graphify query "<question>"` for codebase questions; `graphify update .` after code changes. See `.claude/references/graphify.md`.
