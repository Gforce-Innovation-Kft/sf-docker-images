# CLAUDE.md

Guidance for Claude Code in this repository.

## Project Overview

Builds and publishes three Salesforce-focused Docker images to Docker Hub under
`gforceinnovation`:

| Image | Base | Purpose | Hard rules |
|---|---|---|---|
| **sf-ci** | ubuntu:22.04 | CI/CD runner for SF pipelines | Stay minimal — no editors, no zsh (tests verify absence). Non-root `ci` UID 1000; consumers must run `--user 1000` or `/github/home` is unwritable |
| **sf-devcontainer** | ubuntu:24.04 | Full VS Code devcontainer | Feature-rich is fine. `vscode` UID 1000, zsh + Starship; prompt reads target org from `.sf/config.json` via `jq`, never `sf` (~500 ms) |
| **sf-bulk** | node:24-alpine | Bulk org ops, no Java | Under 600MB uncompressed, no Java (tests verify). `ci` UID 1000 |

All: Node 24.x, SF CLI v2 (+ OpenJDK 17 on the Ubuntu pair), `WORKDIR /workspace`,
`HEALTHCHECK` via `sf version --json`.

**Details** (full tool/env/plugin lists, build commands, CI walkthrough, E2E gate):
[`docs/claude-ci-reference.md`](docs/claude-ci-reference.md) — **read it before
touching any workflow or Dockerfile.**

## CI/CD shape (invariants)

One workflow per image + `release.yml`; the build→test→push pipeline lives in
`reusable-docker-image-build.yml`, everything else is a thin caller.

- **Do not copy pipeline logic into the callers** — change the reusable workflow.
- **Adding an image = copy one `image-*.yml` + add a `release.yml` matrix entry.**
  Forgetting the release half means tested-but-never-published.
- PRs never push; `release.yml` is the only publisher (Docker Hub only; GHCR is for
  throwaway E2E candidates).
- Only sf-ci carries the two-tier **E2E gate** (real container job at `--user 1001`
  → dispatched downstream pipelines). Cross-repo dispatch and the org-level package
  calls authenticate as the **`gforce-ci-bot` GitHub App**, not a PAT — see below.
  Details + rationale in the reference doc — the container-job gap it covers is
  where every shipped regression has lived.

## Credentials

No personal access token is used anywhere in this repo. Anything that reaches
outside this repository mints a scoped, one-hour GitHub App installation token via
[`github-app-token`](https://github.com/Gforce-Innovation-Kft/shared-github-actions/blob/main/.github/actions/github-app-token/action.yml)
in `shared-github-actions`. Three places need one, for two different reasons:

| Where | Scope minted | Why `GITHUB_TOKEN` is not enough |
|---|---|---|
| `e2e-workflows` | `sf-develop-demo`, `actions: write` + `contents: read` | cannot dispatch into another repository at all |
| `publish-candidate` | `sf-docker-images`, `organization-packages: write` | package *visibility* is an org endpoint |
| `cleanup` | `sf-docker-images`, `organization-packages: write` | deleting a package version is an org endpoint |

`packages` and `organization-packages` are different permissions — `packages` covers
pulling and pushing only. Credentials are org-level: `vars.GFORCE_CI_APP_ID` and
`secrets.GFORCE_CI_APP_PRIVATE_KEY`.

## Testing

**pytest-testinfra** in `tests/` — each `test_sf_*.py` builds the image, starts a
container, verifies OS/user/runtimes/plugins/tools/env/dirs, and asserts the
*absence* rules (sf-ci: no vim/nano/zsh; sf-bulk: no Java, <600MB).

## Change Rules

- Adding/removing tools: update the Dockerfile, the image's README, AND
  `tests/test_sf_*.py`.
- Alpine: `apk add --no-cache`; include `coreutils` (`env -S` in SF CLI shebang);
  `deluser node` before creating `ci` (base ships `node` at UID 1000).
- `ubuntu:24.04`+: `userdel -r ubuntu` before creating the image user.
- Ubuntu: clean apt caches in the same `RUN` layer.
- Commits: conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`).
- Pre-commit hook (via `scripts/setup.sh`, `core.hooksPath`): yamllint on staged YAML
  (blocking). `.yamllint`: 120 cols, 2-space indent.

## AI layer

`.claude/references/` (read before generating code) · repo + vendored skills (see
below) · `scripts/setup.sh` bootstrap. Details in the reference doc.

- **L2 `gforce-github-actions`** + agent `gha-workflow-author` — this repo has 5 workflows and
  publishes the images the SF pipelines run on.
- **L3 override** — [`.claude/references/local-standards.md`](.claude/references/local-standards.md):
  the workflow/release rules specific to this repo. The skill reads it **last** and it **wins**.
- Not a Salesforce repo: no `salesforce-developer`, no `sf-code-reviewer`.

<!-- skills-tooling -->
## Skills & AI tooling

**External skills** (lockfile-managed — update with `npx skills check` / `npx skills update`):
- `devcontainer-setup` — from trailofbits/skills
- `docker-expert` — from sickn33/antigravity-awesome-skills
- `gforce-github-actions` — from Gforce-Innovation-Kft/gforce-ai (L2, GForce GHA house standards)
- `multi-stage-dockerfile` — from github/awesome-copilot
- `platform-docs-get` — from forcedotcom/sf-skills

**Local skills** (hand-written, repo-specific):
- `building-a-docker-image`
- `releasing`
- `testing-images`
- `working-in-the-devcontainer`

**Global tooling available in every session:** rtk (Bash output compression — automatic via hook), lean-ctx (prefer `ctx_*` MCP tools for reads/search — token-compressed), and superpowers process skills.
<!-- /skills-tooling -->
