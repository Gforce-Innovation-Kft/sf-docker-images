# GitHub Actions & release conventions (repo rules)

Short repo-specific rules. Full rationale:
[`.github/instructions/github-actions-ci-cd-best-practices.instructions.md`](../../.github/instructions/github-actions-ci-cd-best-practices.instructions.md).

## The one workflow: `.github/workflows/build-and-push.yml` (thin caller)

- **Triggers:** PRs to `main` and version tags `v*.*.*` (pushes to `main` do not build).
- **Job graph:** `images` (matrix: sf-ci, sf-devcontainer, sf-bulk — each invocation calls the
  shared reusable workflow
  `Gforce-Innovation-Kft/shared-github-actions/.github/workflows/docker-build-test-push.yml@v1`,
  which runs build → test → push for that one image) → `release` (tags only, local).
- **PRs build + test but never push or release.** Push/release run **only** on `v*.*.*` tags
  (the caller computes `push: startsWith(github.ref, 'refs/tags/v')`).

## Rules when editing the caller

- Per-image pipeline changes (build/test/push/signing) belong in **shared-github-actions**,
  not here. Do not copy that logic back into this repo.
- The `images` job must grant the reusable workflow its permissions:
  `contents: read`, `checks: write`, `pull-requests: write`, `security-events: write`,
  `id-token: write` (cosign keyless signing).
- Pin the reusable workflow to `@v1` (the shared repo's release process maintains the floating
  major tag). Local actions pin to a major version tag (`@v4`) or SHA — never `@main`/`@latest`.
- Registry is **Docker Hub only** (`gforceinnovation/*`) via the `dockerhub-token` secret
  (`secrets.DOCKERHUB_TOKEN`). Do not add other registries without an explicit decision.
- **Tag scheme:** `{{version}}` + `latest` only. Rolling `{{major}}.{{minor}}`/`{{major}}` tags
  were deliberately dropped (existing ones stay frozen at 1.6.1).
- Images are **cosign-signed** (keyless, GitHub OIDC) on tag pushes. The certificate identity is
  the shared workflow's path — renaming/moving that file in shared-github-actions breaks every
  documented `cosign verify` command.
- Respect `.yamllint` (120-col, 2-space). The `.github/hooks/pre-commit` hook lints staged YAML.

## Release job

On a `v*.*.*` tag, after all three image pipelines succeed, the local `release` job creates a
GitHub Release: generated notes + the matching `CHANGELOG.md` section + per-image tool-version
tables (Node, npm, SF CLI, user plugins) downloaded from the `version-report-*` artifacts the
shared push jobs upload. See [devops.md](./devops.md) for the tag → release flow and the
[releasing skill](../skills/releasing/SKILL.md).
