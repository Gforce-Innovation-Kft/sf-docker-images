# GitHub Actions & release conventions (repo rules)

Short repo-specific rules. Full rationale:
[`.github/instructions/github-actions-ci-cd-best-practices.instructions.md`](../../.github/instructions/github-actions-ci-cd-best-practices.instructions.md).

## The one workflow: `.github/workflows/build-and-push.yml`

- **Triggers:** push to `main`, PRs to `main`, and version tags `v*.*.*`.
- **Job graph:** `dependency-review` (PR only) → `build` (matrix: sf-ci, sf-devcontainer,
  sf-bulk) → `test` (pytest-testinfra + Trivy) → `push` (tags only) → `release` (tags only).
- **PRs build + test but never push or release.** Push/release run **only** on `v*.*.*` tags.

## Rules when editing the workflow

- Pin actions to a major version tag (`@v4`) or SHA — never `@main`/`@latest`.
- Keep `permissions` least-privilege at the workflow level; the `release` job needs
  `contents: write`, nothing else does.
- The `test` job runs `pytest tests/test_sf_<image>.py` (pytest-testinfra) plus Trivy.
- Keep multi-arch (`linux/amd64,linux/arm64`), `sbom: true`, `provenance: true` on the push job.
- Registry is **Docker Hub only** (`gforceinnovation/*`) via `DOCKERHUB_USERNAME` +
  `secrets.DOCKERHUB_TOKEN`. Do not add other registries without an explicit decision.
- Semver tag expansion (metadata-action): `{{version}}`, `{{major}}.{{minor}}`, `{{major}}`, `latest`.
- Respect `.yamllint` (120-col, 2-space). The `.github/hooks/pre-commit` hook lints staged YAML.

## Release job

On a `v*.*.*` tag, after push succeeds, create a GitHub Release with generated notes
augmented by the matching `CHANGELOG.md` section. See [devops.md](./devops.md) for the tag
→ release flow and the [releasing skill](../skills/releasing/SKILL.md).
