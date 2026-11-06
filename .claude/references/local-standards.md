# Local standards — GitHub Actions & release conventions (local layer)

**This is the local override file for this repo** (precedence: industry → fleet → shared →
local, last wins). The `gforce-github-actions` skill reads it
**last** and it **wins** over the fleet standard on any conflict. It is named
`local-standards.md` (not `github-actions.md`) because that is the filename the skill's router
looks for — rename it and the skill stops seeing these rules.

Short repo-specific rules. Full rationale:
[`.github/instructions/github-actions-ci-cd-best-practices.instructions.md`](../../.github/instructions/github-actions-ci-cd-best-practices.instructions.md).

## The two workflows

Both live in this repo — the pipeline is self-contained, with no cross-repo dependency.

| File | Kind | Role |
|---|---|---|
| `.github/workflows/image-sf-ci.yml` | internal | PRs touching sf-ci: build → test → **E2E gate** |
| `.github/workflows/image-sf-devcontainer.yml` | internal | PRs touching sf-devcontainer: build → test |
| `.github/workflows/image-sf-bulk.yml` | internal | PRs touching sf-bulk: build → test |
| `.github/workflows/release.yml` | internal | `v*.*.*` tags: matrix over all images → push → Release |
| `.github/workflows/reusable-docker-image-build.yml` | `workflow_call` | build → test → push for **one** image |

- **One workflow per image.** Path filtering is GitHub's own `on.pull_request.paths`, so a PR
  only starts the workflows for images it touches and a docs-only PR starts nothing. Separate
  workflows are inherently parallel — there is no coordinating job.
- **PRs never push** (`push: false`). `release.yml` is the only publisher, on tags only.
- **Tags build every image** so `latest` stays coherent; that is why the tag path keeps a matrix
  rather than splitting per image.
- **E2E job graph** (sf-ci only): `image` → `publish-candidate` → `e2e-container` (tier 1,
  a real container job on the candidate as `--user 1001`) → `e2e-workflows` (tier 2, dispatched
  downstream pipelines) → `cleanup`.

## Rules when editing these workflows

- Per-image pipeline changes (build/test/push/signing) belong in
  `reusable-docker-image-build.yml`, not in the callers. Keep the callers thin.
- **The image list now lives in two places**, unavoidably: the per-image workflow file and the
  `release.yml` matrix. Adding an image means doing BOTH — copy an `image-*.yml` and add a matrix
  entry. An image with only the first is tested on PRs but **never published**; that failure is
  silent, so check `release.yml` whenever the image set changes.
- Each `image-*.yml` must filter on its own dir, its own `tests/test_<name>.py`, **and** the
  shared inputs (`tests/requirements.txt`, `reusable-docker-image-build.yml`, itself). A new
  shared file (e.g. `tests/conftest.py`) has to be added to **every** image workflow's `paths`,
  or PRs touching it silently build nothing.
- **Adding a critical workflow to the E2E** is one `matrix.target` entry in `image-sf-ci.yml`
  (`name`, `repo`, `workflow`, `ref`, `inputs`). Do not add bespoke job logic per target.
- Tier 1 probes must stay secret-free so they can gate tier 2 cheaply. Anything needing a
  Salesforce org belongs in tier 2.
- The image jobs must grant the reusable workflow its permissions:
  `contents: read`, `checks: write`, `pull-requests: write`, `security-events: write`, plus
  `id-token: write` in `release.yml` (cosign keyless signing).
- The reusable workflow is referenced with a local `./` path, so it is always the version on the
  branch being built.
- **Third-party actions pin to a floating major version tag** (`@v7`, `@v4`) — never `@main`,
  `@latest`, or a commit SHA. Two actions have no floating major tag and must stay exact, so
  leave them alone unless you have checked the upstream tag list:
  - `sigstore/cosign-installer` — publishes only exact tags (`@v4.1.2`).
  - `aquasecurity/trivy-action` — still 0.x, so there is no `v0` tag (`@v0.36.0`).
- **No personal access tokens.** The one thing reaching outside this repository — the tier-2
  dispatch into `sf-develop-demo` — mints a scoped GitHub App token with
  `Gforce-Innovation-Kft/shared-github-actions/.github/actions/github-app-token@v2`
  (`vars.GFORCE_CI_APP_ID` + `secrets.GFORCE_CI_APP_PRIVATE_KEY`, both org-level). Always name
  `repositories:` and the `permission-*` levels — the action refuses to mint otherwise, and that
  refusal is the point: an unscoped installation token is a PAT with a shorter life.
- **Never use an App token for registry or package work.** GitHub Packages has its own
  permission system that accepts classic PATs and largely not App tokens — `PATCH
  /orgs/{org}/packages/...` rejects both `GITHUB_TOKEN` (404) and every App permission, which
  is why the E2E candidate is not on GHCR. Registry steps use `secrets.DOCKERHUB_TOKEN`.
- **`gforceinnovation/sf-ci-e2e` on Docker Hub is public and must stay that way.** Its
  visibility was set by hand and cannot be set from CI. `cleanup` therefore deletes the
  **tag**, never the repository — a recreated repository comes back private and every
  downstream pull fails `denied`.
- Registry is **Docker Hub only** (`gforceinnovation/*`) via the `dockerhub-token` secret
  (`secrets.DOCKERHUB_TOKEN`). Do not add other registries without an explicit decision.
- **Tag scheme:** `{{version}}` + `latest` only. Rolling `{{major}}.{{minor}}`/`{{major}}` tags
  were deliberately dropped (existing ones stay frozen at 1.6.1).
- Images are **cosign-signed** (keyless, GitHub OIDC) on tag pushes. The certificate identity is
  `reusable-docker-image-build.yml`'s own path — renaming or moving that file breaks every
  documented `cosign verify` command. Images published before 2026-08-06 were signed under the
  workflow's previous home in `shared-github-actions` and verify only against that old identity.
- Respect `.yamllint` (120-col, 2-space). The `.github/hooks/pre-commit` hook lints staged YAML.

## Release job

On a `v*.*.*` tag, after all three image pipelines succeed, the local `release` job creates a
GitHub Release: generated notes + the matching `CHANGELOG.md` section + per-image tool-version
tables (Node, npm, SF CLI, user plugins) downloaded from the `version-report-*` artifacts the
shared push jobs upload. See [devops.md](./devops.md) for the tag → release flow and the
[releasing skill](../skills/releasing/SKILL.md).
