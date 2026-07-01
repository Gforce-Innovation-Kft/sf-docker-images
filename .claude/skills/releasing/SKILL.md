---
name: releasing
description: >-
  Cut a SemVer release of the Salesforce Docker images — update CHANGELOG, tag, and let CI
  build/push to Docker Hub and publish a GitHub Release. Use when asked to release, cut a
  version, bump the version, or publish images.
---

# Releasing

Registry is **Docker Hub only** (`gforceinnovation/*`). A `v*.*.*` git tag drives the whole
release. Read [`.claude/references/devops.md`](../../references/devops.md) for the SemVer rules.

## Pre-flight

- All changes are on `main` via a merged, green PR.
- Decide the bump (see devops.md): MAJOR = breaking for consumers, MINOR = additive,
  PATCH = fixes/rebuilds.

## Steps

1. **Update `CHANGELOG.md`** — move the `[Unreleased]` entries under a new dated heading:
   ```
   ## [X.Y.Z] - YYYY-MM-DD
   ```
   Leave a fresh empty `## [Unreleased]` above it. Commit:
   `git commit -m "docs: changelog for vX.Y.Z"`.
2. **Tag and push** (only when the user says so — never push tags unprompted):
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```
3. **CI does the rest** ([`build-and-push.yml`](../../../.github/workflows/build-and-push.yml)):
   build (matrix) → pytest-testinfra + Trivy → multi-arch push to Docker Hub with SBOM + provenance
   (tags `X.Y.Z`, `X.Y`, `X`, `latest`) → GitHub Release with generated notes + the CHANGELOG
   section.

## Verify after the run

```bash
gh run watch                    # follow the tag build
gh release view vX.Y.Z          # confirm the release + notes
docker pull gforceinnovation/sf-ci:X.Y.Z
```

## Rules

- **Never force-push**, never delete or re-point a published tag. Fix forward with a new
  PATCH tag.
- Never publish a release without the user's go-ahead.
