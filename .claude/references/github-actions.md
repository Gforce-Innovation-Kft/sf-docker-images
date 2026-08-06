# GitHub Actions & release conventions (repo rules)

Short repo-specific rules. Full rationale:
[`.github/instructions/github-actions-ci-cd-best-practices.instructions.md`](../../.github/instructions/github-actions-ci-cd-best-practices.instructions.md).

## The two workflows

Both live in this repo — the pipeline is self-contained, with no cross-repo dependency.

| File | Kind | Role |
|---|---|---|
| `.github/workflows/build-and-push.yml` | internal | thin matrix caller + the local `release` job |
| `.github/workflows/reusable-docker-image-build.yml` | `workflow_call` | build → test → push for **one** image |

- **Triggers:** PRs to `main` and version tags `v*.*.*` (pushes to `main` do not build).
- **Job graph:** `changes` (computes the matrix from the PR diff) → `images` (matrix — each
  invocation calls `./.github/workflows/reusable-docker-image-build.yml`) → `release`
  (tags only, local).
- **PRs build + test but never push or release.** Push/release run **only** on `v*.*.*` tags
  (the caller computes `push: startsWith(github.ref, 'refs/tags/v')`).
- **Path filtering (`changes` job):** on a PR the matrix contains only the images whose files
  changed — `sf-<image>/**` or `tests/test_sf_<image>.py` selects one image;
  `.github/workflows/**`, `tests/requirements.txt`, or any other `tests/*.py` selects all;
  anything else selects none and `images` is skipped via `has-images`. Tags always select all
  so `latest` stays coherent. The job lists its decision in the run summary.

## Rules when editing the caller

- Per-image pipeline changes (build/test/push/signing) belong in
  `reusable-docker-image-build.yml`, not in the caller. Keep `build-and-push.yml` thin: the
  `changes` job, the matrix, the permissions, and the release job.
- **The image set is defined once**, in the `IMAGES` JSON map of the `changes` job. The key is
  simultaneously the image name, the build-context directory (`./<key>`), and the test-file stem
  (`tests/test_<key with underscores>.py`); the value is the Docker Hub short description. Add or
  remove an image there and nothing else in the caller needs to change — do not reintroduce a
  hard-coded matrix.
- A new **shared** test helper (e.g. `tests/conftest.py`) is already treated as affecting every
  image. A new non-shared file type that should trigger builds needs a rule added to the
  `changes` job, or PRs touching it will silently build nothing.
- The `images` job must grant the reusable workflow its permissions:
  `contents: read`, `checks: write`, `pull-requests: write`, `security-events: write`,
  `id-token: write` (cosign keyless signing).
- The reusable workflow is referenced with a local `./` path, so it is always the version on the
  branch being built. Local third-party actions pin to a major version tag (`@v4`) or SHA —
  never `@main`/`@latest`.
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
