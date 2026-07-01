---
name: testing-images
description: >-
  Run and interpret the Node.js container tests for the Salesforce Docker images. Use when
  asked to test an image, add a new assertion, debug a failing container test, or check an
  image size budget. Tests use the built-in node:test runner (Node 20+) — no deps to install.
---

# Testing the images

## Run

```bash
node --test tests/                          # all three images
node --test tests/sf-ci.test.mjs            # one image
node --test tests/sf-bulk.test.mjs
```

Node 20+ only. There are **no dependencies to install** — tests use `node:test` and
`node:child_process`. The first run of each suite builds `<image>:test` if it is missing
(via `tests/helpers/docker.mjs`); later runs reuse it, so rebuild manually after changing a
Dockerfile:

```bash
docker build -t sf-ci:test ./sf-ci && node --test tests/sf-ci.test.mjs
```

## How it works

`tests/helpers/docker.mjs` exposes:

- `ensureImage(name, contextDir)` — build `<name>:test` once if absent.
- `run(image, cmd)` — `docker run --rm <image>:test bash -c "<cmd>"`, returns trimmed stdout.
- `inspect(image, format)` — wraps `docker image inspect` (WORKDIR, Healthcheck, env).
- `sizeBytes(image)` — image size for the budget assertions.

Each `tests/sf-*.test.mjs` mirrors the image's rules: OS, user/UID/shell, runtimes,
`sf version --json`, plugins, present tools, **absent** forbidden tools, env vars, WORKDIR,
HEALTHCHECK, and size budget.

## Adding an assertion

Add a `test('...', () => { ... })` in the relevant suite using `run(...)`/`inspect(...)` and
`node:assert/strict`. Keep it aligned with the change you made to the Dockerfile and README
(see the `building-a-docker-image` skill). Every added/removed tool needs a matching test.

## Interpreting failures

- **Size budget failed** — the image grew past its cap (sf-bulk < 500 MB). Slim the layers;
  do not raise the cap without a decision.
- **"forbidden tool present" (sf-ci)** — an editor/zsh/interactive tool leaked in; remove it.
- **plugin/env missing** — check the `sf plugins install` step and the `ENV` block.
- **build failed** — run the raw `docker build` to see the full log.
