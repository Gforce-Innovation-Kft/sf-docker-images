# sf-devcontainer DX upgrade — design

**Date:** 2026-07-12 · **Status:** skeleton implemented on `feat/devcontainer-dx`, awaiting review
**Sub-project A** of the devcontainer initiative (B: security hardening, C: compose recipes,
D: release pipeline fix — each gets its own spec later).

## Goal

Make `sf-devcontainer` a batteries-included, personalizable Salesforce dev shell:
efficient zsh out of the box, per-developer customization without image rebuilds, and
first-class AI pair development via Claude Code — while keeping the image usable outside
VS Code (plain `docker run`, compose).

## Decisions (agreed 2026-07-12)

| Question | Decision |
|----------|----------|
| Personalization model | **Team defaults baked in + per-dev overlay** (VS Code `dotfiles.repository` + `~/.zshrc.local` hook) |
| Tool delivery | **Approach 1 — bake all CLI tools into the image**; devcontainer.json stays thin |
| Claude Code | **Not baked** — `ghcr.io/anthropics/devcontainer-features/claude-code` feature in the reference devcontainer.json; revisit baking later |
| SF tooling | VS Code extensions (Expanded pack, Apex PMD, Prettier, ESLint, XML) in devcontainer.json; `prettier` + `prettier-plugin-apex` + `eslint` global in the image |
| Rejected | SFDMU, sfdx-hardis (heavy/opinionated), devcontainer features for CLI tools (absent outside VS Code, slow create) |

## Components

### 1. Dockerfile (`sf-devcontainer/Dockerfile`)

- **apt additions** (existing layer): `ripgrep`, `fd-find`, `bat`.
- **GitHub CLI**: official `cli.github.com` apt repo, keyring under `/etc/apt/keyrings`.
- **Pinned GitHub-release tools** (one layer, multi-arch via `TARGETARCH` with
  amd64→x86_64 / arm64→aarch64 mapping where needed, versions as `ARG`s):
  - fzf 0.74.0 (apt's 0.29 lacks `fzf --zsh` shell integration)
  - zoxide 0.10.0 (.deb), git-delta 0.19.2 (.deb)
  - eza 0.23.5, lazygit 0.63.0 (tarballs → `/usr/local/bin`)
- **Symlinks**: `bat` → `batcat`, `fd` → `fdfind` (Ubuntu naming).
- **npm globals**: `prettier`, `prettier-plugin-apex`, `eslint`.
- **System git config**: `core.pager=delta`, `interactive.diffFilter`, `delta.navigate`,
  `merge.conflictStyle=diff3` (pager only engages on a TTY — no CI impact; `zdiff3`
  rejected — needs git ≥ 2.35, Ubuntu 22.04 ships 2.34 and hard-fails every clone).
- No hard size cap on this image (see image-conventions.md); expect roughly +150–250 MB.

### 2. Shell config (`sf-devcontainer/.zshrc`)

- OMZ plugins added: `gh`, `fd`, `ripgrep`, `zoxide` (completions/init);
  `zsh-syntax-highlighting` moved last (OMZ recommendation).
- `source <(fzf --zsh)` — Ctrl-R fuzzy history, Ctrl-T file picker.
- History: 50k entries, dedup; `HISTFILE=/commandhistory/.zsh_history` when that
  directory exists and is writable (persistent-history volume, see devcontainer.json).
- eza aliases (`ls`, `ll`, `la`, `lt`), SF shortcuts (`sfl`, `sfo`, `sfd`, `sfdp`, `sfr`,
  `sft`, `sfdelta()`) + `sfhelp` listing them.
- Welcome banner made static (no `sf version` subprocess — faster shell start).
- **Overlay hook (last line):** `source ~/.zshrc.local` if present. Full personalization
  via VS Code `dotfiles.repository` is documented in the README.

### 3. Reference `.devcontainer/devcontainer.json`

- `features`: claude-code (removable one-liner).
- `mounts`: named volume `sf-devcontainer-history` → `/commandhistory` (ownership fixed
  in `postCreateCommand`); commented bind-mount example for host `~/.claude` auth reuse.
- `extensions`: `salesforce.salesforcedx-vscode-expanded`, `chuckjonas.apex-pmd`,
  `esbenp.prettier-vscode`, `dbaeumer.vscode-eslint`, `redhat.vscode-xml`,
  `redhat.vscode-yaml`, `ms-azuretools.vscode-docker`.
- `settings`: Prettier as default formatter (existing zsh/formatOnSave/telemetry kept).

### 4. Tests (`tests/test_sf_devcontainer.py`)

New assertions: each new tool runs `--version`; `bat`/`fd` symlinks resolve;
`prettier`/`eslint`/`prettier-plugin-apex` global; `git config --system core.pager` is
`delta`; `.zshrc` contains fzf integration, zoxide plugin, SF aliases, `.zshrc.local` hook.

### 5. Docs

- `sf-devcontainer/README.md`: tool list, "Personalize your shell" (dotfiles.repository +
  `~/.zshrc.local`), "AI pair development" (feature + auth mount), updated example.
- `CHANGELOG.md` `[Unreleased]`, `.claude/references/image-conventions.md`,
  root `CLAUDE.md`/`AGENTS.md` tool lists.

## Error handling

- Release-tool downloads: `curl -fsSL` + bash `pipefail` — any 404/network error fails the
  build loudly. Unsupported arch exits explicitly.
- `fzf --zsh` and HISTFILE are guarded (`command -v` / writability) so the shell never
  breaks if a tool or mount is absent.
- Claude Code feature failures don't break the image (feature lives only in
  devcontainer.json and is user-removable).

## Testing / verification

`docker build -t sf-devcontainer:test ./sf-devcontainer` (amd64 **and** arm64 in CI) +
`pytest tests/test_sf_devcontainer.py -v`. Version pins verified against real release
assets during the local build.

## Out of scope (later sub-projects)

Security/base-image bump (B), compose recipes + secrets/org-auth/Windows-parity docs (C),
shared-workflow README-sync hardening + DOCKERHUB_TOKEN rotation (D — token rotation is a
manual step only Gabor can do).
