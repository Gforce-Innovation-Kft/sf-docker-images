---
name: building-a-docker-image
description: >-
  Scaffold or modify a Salesforce Docker image in this repo (sf-ci, sf-devcontainer,
  sf-bulk) — the Dockerfile, its README, the pytest-testinfra container tests, and its CI
  workflow — while honouring the per-image size, user, and tool rules. Use when adding/removing
  a tool or plugin, changing a base image, or creating a new image.
---

# Building / modifying a Docker image

## Before you touch anything

1. Read [`.claude/references/image-conventions.md`](../../references/image-conventions.md) —
   the per-image allowed/forbidden tools, users, and size budgets are **enforced by tests**.
2. Read [`.claude/references/docker-best-practices.md`](../../references/docker-best-practices.md)
   for the layer/cleanup/multi-arch rules.

## The change is not done until you update all four

For any tool/plugin/base change to `sf-ci`, `sf-devcontainer`, or `sf-bulk`:

1. **Dockerfile** — `<image>/Dockerfile`. Keep layers ordered least→most volatile; clean
   caches in the same `RUN` (`rm -rf /var/lib/apt/lists/*` on Ubuntu, `apk --no-cache` on
   Alpine). Keep `WORKDIR /workspace`, the `HEALTHCHECK`, and the `LABEL` block.
2. **Image README** — `<image>/README.md`. Update the feature list.
3. **pytest test** — `tests/test_sf_<image>.py`. Add/adjust an assertion (present tool,
   absent forbidden tool, plugin, env var, size). See the `testing-images` skill.
4. **Root docs if user-facing** — `README.md`, `CHANGELOG.md` `[Unreleased]`.

## Guardrails per image

- **sf-ci** — must stay thin. Never add editors (vim/nano), zsh, or interactive/UI tools;
  tests assert their absence.
- **sf-devcontainer** — may be feature-rich; keep the `vscode` user + zsh setup intact.
- **sf-bulk** — **hard < 600 MB, no Java.** After changes, confirm size with
  `docker image inspect sf-bulk:test --format '{{.Size}}'`.

## New image checklist

- Create `<image>/Dockerfile`, `<image>/README.md`, `<image>/.dockerignore`.
- **Create both runtime accounts**: the image user at UID 1000 (`ci`/`vscode`) *and* `runner` at
  UID 1001 with GID 0. GitHub Actions container jobs run as the runner's UID, and `sf` crashes
  on a UID with no `/etc/passwd` entry. Make writable paths group-0 writable
  (`chgrp -R 0 … && chmod -R g=u …`). End on the non-root user — never `USER root`.
- Add `tests/test_sf_<image>.py` (copy the `host` fixture from an existing test file), including
  the non-root and UID-1001 assertions.
- **Two CI files, not one:** a new `.github/workflows/image-<name>.yml` (copy an existing one;
  change the name, context, and `paths`) **and** a matrix entry in
  [`.github/workflows/release.yml`](../../../.github/workflows/release.yml). An image with only
  the first is built and tested on PRs but **never published** — and nothing warns you.
- Document it in root `README.md`, `CLAUDE.md`, `AGENTS.md`, and `CHANGELOG.md`.

## Verify

```bash
docker build -t sf-<image>:test ./sf-<image>
pytest tests/test_sf_<image>.py -v
```
