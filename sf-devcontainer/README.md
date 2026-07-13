# sf-devcontainer

> Full-featured VS Code devcontainer for Salesforce development.

[![CI](https://github.com/Gforce-Innovation-Kft/sf-docker-images/actions/workflows/build-and-push.yml/badge.svg)](https://github.com/Gforce-Innovation-Kft/sf-docker-images/actions/workflows/build-and-push.yml)
[![Release](https://img.shields.io/github/v/release/Gforce-Innovation-Kft/sf-docker-images?sort=semver)](https://github.com/Gforce-Innovation-Kft/sf-docker-images/releases)
[![sf-devcontainer size](https://img.shields.io/docker/image-size/gforceinnovation/sf-devcontainer/latest?label=size)](https://hub.docker.com/r/gforceinnovation/sf-devcontainer)
[![sf-devcontainer pulls](https://img.shields.io/docker/pulls/gforceinnovation/sf-devcontainer?label=pulls)](https://hub.docker.com/r/gforceinnovation/sf-devcontainer)
[![License](https://img.shields.io/github/license/Gforce-Innovation-Kft/sf-docker-images)](https://github.com/Gforce-Innovation-Kft/sf-docker-images/blob/main/LICENSE)
[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-D97757?logo=anthropic&logoColor=white)](https://claude.com/claude-code)

Part of [**sf-docker-images**](../README.md). An `ubuntu:24.04` image with everything a
Salesforce developer needs day to day — a productive zsh shell, editors, and extra SF CLI
plugins on top of the [`sf-ci`](../sf-ci/README.md) toolchain.

## Pull

```bash
docker pull gforceinnovation/sf-devcontainer:latest
```

```dockerfile
FROM gforceinnovation/sf-devcontainer:1.7.0
```

Multi-arch: `linux/amd64` + `linux/arm64`. Two tags per release
(see [supported tags](../README.md#supported-tags)): the exact version (`1.7.0`, immutable —
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
- **Shell**: zsh with Oh My Zsh, Powerlevel10k, autosuggestions, syntax-highlighting,
  completions, fzf keybindings (Ctrl-R/Ctrl-T), zoxide (`z`), and Salesforce aliases
  (`sfhelp` lists them).
- **CLI tools**: gh (GitHub CLI), fzf, zoxide, eza, bat, ripgrep, fd, git-delta
  (system git pager), lazygit.
- **Formatters/linters**: prettier + prettier-plugin-apex + eslint (global — work
  without a project `package.json`).
- **Editors & tools**: vim, nano, wget, htop, tree, less, build-essential, openssl.
- **User**: `vscode` (UID 1000) with passwordless sudo.

## Usage

### VS Code Dev Containers

Copy this repo's reference [`.devcontainer/devcontainer.json`](../.devcontainer/devcontainer.json)
into your sfdx project, then run **Dev Containers: Reopen in Container**. It wires up the
Salesforce Extension Pack (Expanded), Apex PMD, Prettier, ESLint, persistent shell
history, and the Claude Code feature. Minimal version:

```json
{
  "name": "Salesforce Development",
  "image": "gforceinnovation/sf-devcontainer:latest",
  "customizations": {
    "vscode": { "extensions": ["salesforce.salesforcedx-vscode-expanded"] }
  }
}
```

### Personalize your shell

The image ships team-wide defaults; layer your own on top — no rebuild needed:

- **`~/.zshrc.local`** — sourced last by the baked-in `.zshrc` if present. Drop extra
  aliases, env vars, or theme tweaks there (e.g. from a `postCreateCommand`).
- **VS Code dotfiles** — set `"dotfiles.repository": "you/dotfiles"` in your VS Code
  user settings and VS Code clones + installs your dotfiles into every dev container
  automatically.
- **Prompt** — run `p10k configure` inside the container for a wizard-driven
  Powerlevel10k setup.

### AI pair development (Claude Code)

The reference devcontainer.json installs [Claude Code](https://claude.com/claude-code)
via the official devcontainer feature:

```json
"features": {
  "ghcr.io/anthropics/devcontainer-features/claude-code:1.0": {}
}
```

To reuse your host login instead of authenticating in every container, uncomment the
`~/.claude` bind mount in the reference file (or set `ANTHROPIC_API_KEY`).

### Docker

```bash
docker run -it --rm -v "$(pwd):/workspace" gforceinnovation/sf-devcontainer:latest
```

## When to use

Use `sf-devcontainer` for local development. It is **not intended as a CI
`container:` image** — it is large and interactive-shell-oriented. For pipelines,
prefer the leaner [`sf-ci`](../sf-ci/README.md); for Java-free bulk data work,
prefer [`sf-bulk`](../sf-bulk/README.md).

## Building locally

```bash
docker build -t sf-devcontainer:local .
```
