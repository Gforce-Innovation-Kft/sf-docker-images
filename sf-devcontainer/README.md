# sf-devcontainer

> Full-featured VS Code devcontainer for Salesforce development.

[![sf-devcontainer size](https://img.shields.io/docker/image-size/gforceinnovation/sf-devcontainer/latest?label=size)](https://hub.docker.com/r/gforceinnovation/sf-devcontainer)
[![sf-devcontainer pulls](https://img.shields.io/docker/pulls/gforceinnovation/sf-devcontainer?label=pulls)](https://hub.docker.com/r/gforceinnovation/sf-devcontainer)
[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-D97757?logo=anthropic&logoColor=white)](https://claude.com/claude-code)

Part of [**sf-docker-images**](../README.md). An `ubuntu:22.04` image with everything a
Salesforce developer needs day to day — a productive zsh shell, editors, and extra SF CLI
plugins on top of the [`sf-ci`](../sf-ci/README.md) toolchain.

## Pull

```bash
docker pull gforceinnovation/sf-devcontainer:latest
```

```dockerfile
FROM gforceinnovation/sf-devcontainer:1.6.1
```

Multi-arch: `linux/amd64` + `linux/arm64`. Two tags per release
(see [supported tags](../README.md#supported-tags)): the exact version (`1.6.1`, immutable —
pin this in production) and `latest` (moving).

### Verify the signature

Every published image is signed with cosign (keyless, GitHub OIDC):

```bash
cosign verify \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity-regexp \
    '^https://github\.com/Gforce-Innovation-Kft/shared-github-actions/\.github/workflows/docker-build-test-push\.yml@.+$' \
  gforceinnovation/sf-devcontainer:latest
```

## What's inside

- **Node.js 24.x** (LTS) and **Java 17** (OpenJDK).
- **Salesforce CLI v2** with plugins: `code-analyzer`, `sfdx-git-delta`, `sfdx-browserforce-plugin`.
- **Shell**: zsh with Oh My Zsh, Powerlevel10k, autosuggestions, syntax-highlighting, completions.
- **Editors & tools**: vim, nano, wget, htop, tree, less, build-essential, openssl.
- **User**: `vscode` (UID 1000) with passwordless sudo.

## Usage

### VS Code Dev Containers

Add `.devcontainer/devcontainer.json`, then run **Dev Containers: Reopen in Container**:

```json
{
  "name": "Salesforce Development",
  "image": "gforceinnovation/sf-devcontainer:latest",
  "customizations": {
    "vscode": { "extensions": ["salesforce.salesforcedx-vscode"] }
  }
}
```

### Docker

```bash
docker run -it --rm -v "$(pwd):/workspace" gforceinnovation/sf-devcontainer:latest
```

## When to use

Use `sf-devcontainer` for local development. For pipelines, prefer the leaner
[`sf-ci`](../sf-ci/README.md); for Java-free bulk data work, prefer
[`sf-bulk`](../sf-bulk/README.md).

## Building locally

```bash
docker build -t sf-devcontainer:local .
```
