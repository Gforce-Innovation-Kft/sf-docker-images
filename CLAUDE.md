# CLAUDE.md

Guidance for Claude Code in this repository.

## Project Overview

Builds and publishes three Salesforce-focused Docker images to Docker Hub under
`gforceinnovation`:

| Image | Base | Purpose | Hard rules |
|---|---|---|---|
| **sf-ci** | ubuntu:22.04 | CI/CD runner for SF pipelines | Stay minimal — no editors, no zsh (tests verify absence). Defaults to **`runner` UID 1001, GID 0** since 3.1.0, so a container job needs no `options:` at all. Do **not** tell consumers `--user 1000` — that UID cannot write the runner file commands |
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

No personal access token is used anywhere in this repo. Exactly one thing reaches
outside this repository — the tier-2 dispatch — and it mints a scoped, one-hour
GitHub App installation token via
[`github-app-token`](https://github.com/Gforce-Innovation-Kft/shared-github-actions/blob/main/.github/actions/github-app-token/action.yml)
in `shared-github-actions`:

| Where | Scope minted | Why `GITHUB_TOKEN` is not enough |
|---|---|---|
| `e2e-workflows` | `sf-develop-demo`, `actions: write` + `contents: read` | cannot dispatch into another repository at all |

Credentials are org-level: `vars.GFORCE_CI_APP_ID` + `secrets.GFORCE_CI_APP_PRIVATE_KEY`,
App `gforce-ci-bot`.

**Do not reach for an App token for registry work.** GitHub Packages runs a separate
permission system that accepts classic PATs and largely not App tokens; publishing a
GHCR package needs `PATCH /orgs/{org}/packages/...`, which no App permission satisfies.
That is why the E2E candidate lives on Docker Hub (`gforceinnovation/sf-ci-e2e`, public,
set by hand once) and both registry steps use `secrets.DOCKERHUB_TOKEN`. Full reasoning
in [the reference doc](docs/claude-ci-reference.md).

## GCP-backed secrets — not used here yet, but know where they'd come from

None of this repo's current credentials (`GFORCE_CI_APP_ID`/`GFORCE_CI_APP_PRIVATE_KEY`,
`DOCKERHUB_TOKEN`) are GCP-sourced — they're plain org-level GitHub secrets, unrelated to the
Salesforce JWT system below. If this repo ever needs a Google-Cloud-backed secret,
[`gforce-google-infra`](https://github.com/Gforce-Innovation-Kft/gforce-google-infra) is where it
gets defined (Terraform-managed Secret Manager containers, never this repo) and, if a consumer
still needs it as a GitHub secret rather than reading GCP directly via WIF, mirrored out by its
`modules/gh-secret-sync`. Don't hand-add a Google-related secret here without checking that repo
first.

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

Precedence: **industry → fleet → shared → local, last wins**
(see [`gforce-ai-integration.md`](.claude/references/gforce-ai-integration.md)).

- **Shared: `gforce-github-actions`** + agent `gforce-gha-workflow-author` — this repo has 5 workflows and
  publishes the images the SF pipelines run on.
- **Industry: `platform-docs-get`** — from `forcedotcom/sf-skills`, ratified via
  `gforce-ai/upstream/catalog.json`; any GForce rule beats it.
- **Local override** — [`.claude/references/local-standards.md`](.claude/references/local-standards.md):
  the workflow/release rules specific to this repo. Shared skills read it **last** and it **wins**.
- Not a Salesforce metadata repo: no `gforce-salesforce-developer`, no `gforce-sf-code-reviewer`.

<!-- skills-tooling -->
## Skills & AI tooling

**External skills** (lockfile-managed — update with `npx skills check` / `npx skills update`):
- `devcontainer-setup` — from trailofbits/skills
- `docker-expert` — from sickn33/antigravity-awesome-skills
- `gforce-github-actions` — from Gforce-Innovation-Kft/gforce-ai (shared layer, GForce GHA house standards)
- `multi-stage-dockerfile` — from github/awesome-copilot
- `platform-docs-get` — from forcedotcom/sf-skills (industry layer, ratified in gforce-ai `upstream/catalog.json`)

**Local skills** (hand-written, repo-specific):
- `building-a-docker-image`
- `releasing`
- `testing-images`
- `working-in-the-devcontainer`

**Global tooling available in every session:** rtk (Bash output compression — automatic via hook), lean-ctx (prefer `ctx_*` MCP tools for reads/search — token-compressed), and superpowers process skills.
<!-- /skills-tooling -->
