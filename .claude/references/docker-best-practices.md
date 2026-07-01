# Docker best practices (repo rules)

Read this before creating or modifying any `Dockerfile` in this repo. It is the short,
repo-specific rule set. The exhaustive rationale lives in
[`.github/instructions/containerization-docker-best-practices.instructions.md`](../../.github/instructions/containerization-docker-best-practices.instructions.md).

## Non-negotiable rules here

- **Pin the base image** by tag (`ubuntu:22.04`, `node:20-alpine`). Never `latest`.
- **One `RUN` per concern, clean up in the same layer.**
  - Ubuntu: `apt-get update && apt-get install -y --no-install-recommends ... && rm -rf /var/lib/apt/lists/*`
  - Alpine: `apk add --no-cache ...` (never leave an apk cache).
- **Order layers least- to most-frequently-changed** so the build cache stays warm.
- **`SHELL ["/bin/bash", "-o", "pipefail", "-c"]`** before any `curl ... | bash` so pipe
  failures abort the build (see [`sf-ci/Dockerfile`](../../sf-ci/Dockerfile)).
- **Metadata:** keep the `LABEL org.opencontainers.image.*` block current.
- **`HEALTHCHECK`** using `sf version --json` on every image.
- **`WORKDIR /workspace`** as the final workdir on every image.
- **`.dockerignore`** present in every image directory.
- **Multi-arch:** every image must build clean on `linux/amd64` and `linux/arm64`.
  Avoid arch-specific binaries; if unavoidable, branch on `TARGETARCH`.
- **No secrets in layers.** Nothing sensitive via `COPY`/`ARG`/`ENV`.

## SF CLI plugin install pattern (all images)

Plugins are installed as the `ci`/`vscode` user so they land in
`XDG_DATA_HOME=/opt/sf-data` (world-writable, 777) — this makes them usable regardless of
the runtime UID. See [image-conventions.md](./image-conventions.md) for the per-image
user/runtime rules and why `sf-ci`/`sf-bulk` run as root at runtime.

## Multi-stage builds

Not currently used (SF CLI is an npm global, not a compiled artifact). If you add a build
step that needs compilers, use a multi-stage build and copy only the runtime artifact
into the final stage — never ship build tooling in `sf-ci` or `sf-bulk`.
