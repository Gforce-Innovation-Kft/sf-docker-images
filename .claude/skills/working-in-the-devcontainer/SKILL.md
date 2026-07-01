---
name: working-in-the-devcontainer
description: >-
  Route dev/build/test commands into the running Salesforce dev container instead of the
  host. Use when working inside (or driving) the sf-devcontainer image — running sf CLI,
  Node, git, or tests against the container so the toolchain matches CI. Adapted from
  wrsmith108/claude-code-docker-skill (see ATTRIBUTION.md).
---

# Working in the dev container

The [`sf-devcontainer`](../../../sf-devcontainer/) image is the source of truth for local
Salesforce development. Run tooling **inside it** so versions match CI (Node 24, Java 17,
SF CLI + plugins) instead of relying on whatever is on the host.

## Discover the container

```bash
# The VS Code "Reopen in Container" flow (root .devcontainer/devcontainer.json) starts it.
docker ps --filter "ancestor=gforceinnovation/sf-devcontainer" --format '{{.Names}}'
```

Capture the name once and reuse it:

```bash
DEV=$(docker ps --filter "ancestor=gforceinnovation/sf-devcontainer" --format '{{.Names}}' | head -1)
```

## Route commands into it

```bash
docker exec -w /workspace "$DEV" sf --version
docker exec -w /workspace "$DEV" sf project deploy start
docker exec -w /workspace "$DEV" npm ci
docker exec -w /workspace "$DEV" node --version
```

- Always `-w /workspace` (the container's workdir and the mounted repo).
- Add `-it` only for interactive shells (`docker exec -it "$DEV" zsh`), never in scripts/CI.

## If no container is running

Start one ad hoc with the repo mounted:

```bash
docker run --rm -it -v "$PWD:/workspace" -w /workspace \
  gforceinnovation/sf-devcontainer:latest zsh
```

Or build locally first: `docker build -t sf-devcontainer:local ./sf-devcontainer`.

## Rules

- Don't install Salesforce tooling on the host to "work around" the container — fix the
  image ([`building-a-docker-image`](../building-a-docker-image/SKILL.md)) instead.
- Container image tests are separate — those use `sf-devcontainer:test` and the
  pytest-testinfra suite ([`testing-images`](../testing-images/SKILL.md)), not the running
  dev container.
