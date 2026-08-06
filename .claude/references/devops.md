# DevOps: versioning, tagging, rollback

## SemVer

Images are versioned with [SemVer](https://semver.org). A `v*.*.*` git tag drives everything.

- **MAJOR** — breaking change for consumers (base OS bump, removed tool/plugin, user/UID
  change, env var removal).
- **MINOR** — backward-compatible addition (new tool, new plugin, new image).
- **PATCH** — fixes, security patches, rebuilds with no interface change.

Docker Hub receives **exactly two tags** per release: the immutable `{{version}}` (e.g. `3.0.0`)
and the moving `latest`. Rolling `{{major}}.{{minor}}` and `{{major}}` tags are **no longer
published** — the ones from the v1 era are frozen where they are. Do not reintroduce them
without also updating every README's "supported tags" section.

**Worked example of MAJOR:** 3.0.0 changes the runtime user from root to non-root `ci`.
Consumers must run the container as UID 1000 or 1001, so it is breaking even though nothing
was removed.

## Release flow (see the `releasing` skill for the checklist)

1. Land all changes on `main` via PR (green CI).
2. Move `CHANGELOG.md` `[Unreleased]` entries under a new `[X.Y.Z] - YYYY-MM-DD` heading.
3. `git tag -a vX.Y.Z -m "Release vX.Y.Z" && git push origin vX.Y.Z`.
4. CI builds multi-arch, tests, pushes to Docker Hub (with SBOM + provenance), and opens a
   GitHub Release with generated notes + the CHANGELOG section.

## Rollback

- Images are immutable per tag. To roll back a consumer, pin an older tag
  (`gforceinnovation/sf-ci:1.2.3` instead of `latest`).
- A bad release is fixed forward with a new PATCH tag — **never** re-point or delete a
  published tag, and **never force-push** tags or branches.
- Downstream workflows should pin the **exact version** (`sf-ci:3.0.0`) rather than `latest`
  for reproducible CI. There is no rolling minor tag to pin to.
