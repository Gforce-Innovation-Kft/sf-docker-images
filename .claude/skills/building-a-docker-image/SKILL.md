---
name: building-a-docker-image
description: >-
  Scaffold or modify a Salesforce Docker image in this repo (sf-ci, sf-devcontainer,
  sf-bulk) — the Dockerfile, its README, the pytest-testinfra container tests, and the CI build
  matrix — while honouring the per-image size and tool rules. Use when adding/removing a
  tool or plugin, changing a base image, or creating a new image.
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
- **sf-bulk** — **hard < 500 MB, no Java.** After changes, confirm size with
  `docker image inspect sf-bulk:test --format '{{.Size}}'`.

## New image checklist

- Create `<image>/Dockerfile`, `<image>/README.md`, `<image>/.dockerignore`.
- Add `tests/test_sf_<image>.py` (copy the `host` fixture from an existing test file).
- Add the image to the `build`, `test`, and `push` matrices in
  [`.github/workflows/build-and-push.yml`](../../../.github/workflows/build-and-push.yml).
- Document it in root `README.md`, `CLAUDE.md`, `AGENTS.md`, and `CHANGELOG.md`.

## Verify

```bash
docker build -t sf-<image>:test ./sf-<image>
pytest tests/test_sf_<image>.py -v
```
