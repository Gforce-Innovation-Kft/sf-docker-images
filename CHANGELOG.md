# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-07-13

### Added
- sf-devcontainer: baked-in CLI productivity tools — GitHub CLI (`gh`), fzf 0.74,
  zoxide 0.10, eza 0.23, bat, ripgrep, fd, git-delta 0.19 (system git pager),
  lazygit 0.63; `bat`/`fd` symlinked from Ubuntu's `batcat`/`fdfind`
- sf-devcontainer: global `prettier` + `prettier-plugin-apex` + `eslint`
- sf-devcontainer: zsh upgrades — fzf keybindings, zoxide/gh OMZ plugins,
  50k deduplicated history (persistent via optional `/commandhistory` volume),
  Salesforce aliases (`sfhelp`), and a `~/.zshrc.local` per-developer overlay hook
- sf-devcontainer: `devhelp` in-shell cheatsheet (baked at
  `/usr/local/share/sf-devcontainer/cheatsheet.md`, rendered with bat) and
  `TOOLS.md` expert guide to the CLI tools + zsh features, linked from the README
- Reference `.devcontainer/devcontainer.json`: Claude Code devcontainer feature,
  Salesforce Extension Pack (Expanded) + Apex PMD + Prettier + ESLint extensions,
  persistent-history volume mount
- Design doc: `docs/devcontainer-dx-design.md`

### Changed
- sf-devcontainer: welcome banner is now static (no `sf version` subprocess) for a
  faster shell start
- **sf-devcontainer: base bumped `ubuntu:22.04` → `ubuntu:24.04`** — jammy standard
  support ends 2027-04 (noble: 2029), and noble brings git 2.43 (zdiff3), gcc 13,
  python 3.12. Note: `linux-libc-dev` CVE noise persists on noble (6 CRITICAL /
  166 HIGH, all `fixed: none` — kernel headers, not exploitable in a container);
  eliminating it from the dashboard needs a scan-policy change (e.g. Trivy
  `--ignore-unfixed`) in the shared workflow. Noble's default `ubuntu` user
  (UID 1000) is removed before creating `vscode`. sf-ci stays on 22.04 for
  CI-consumer stability
- This repo's `.devcontainer/devcontainer.json` now **builds from
  `../sf-devcontainer`** instead of pulling `:latest`, so the devcontainer always
  matches the checked-out branch (consumers copying the file into their own
  project should swap the `build` block for the `image:` form shown in the README)

### Fixed
- sf-devcontainer: removed `fd`/`ripgrep` from the OMZ plugins list — Oh My Zsh
  deleted these completion-only plugins upstream, causing `plugin not found`
  warnings on every shell start (the tools ship their own completions)
- Per-image `.dockerignore` files are now tracked in git — the repo `.gitignore`
  was ignoring them, so CI built every image with an unfiltered context while
  local builds filtered

### Added (examples)
- `examples/` — Docker Compose recipes for sfdx projects: zero-install dev shell,
  org auth from a container via `SF_AUTH_URL` (`scripts/auth-org.sh`), CI-parity
  script testing in sf-ci (Windows-friendly), bulk data ops; `.env.example` +
  secrets guidance

## [1.7.0] - 2026-07-12

### Added
- Explicit `docker pull` / `FROM` snippets and tag/architecture sections in the root and
  per-image READMEs
- `sf-bulk/.dockerignore` (previously missing; sf-ci and sf-devcontainer already had one)
- CI: Docker Hub README/description sync on release (`peter-evans/dockerhub-description`)
- CI: **keyless cosign signing** (GitHub OIDC) of every pushed image; verification commands
  documented in the root and per-image READMEs
- Release notes now include per-image tool-version tables (Node, npm, SF CLI, user plugins)
  read from the built images

### Changed
- GitHub repo metadata: description, topics, and Docker Hub homepage link set
- CI: dropped the unused `packages: write` permission (images push to Docker Hub, not GHCR)
- CI: the per-image build → test → push pipeline moved to the shared
  `docker-build-test-push` reusable workflow in `shared-github-actions`;
  `build-and-push.yml` is now a thin matrix caller with a local release job
- **Docker tag scheme: releases publish `X.Y.Z` + `latest` only** — rolling `:1` / `:1.6`
  tags are no longer pushed (existing ones stay frozen at 1.6.1); pin an exact version or
  track `latest`

### Security
- All Dockerfiles: base images now pinned by tag **plus multi-arch index digest**
  (`ubuntu:22.04@sha256:…`, `node:24-alpine@sha256:…`) for reproducible, tamper-evident
  builds; refresh command documented above each `FROM`

### Fixed
- All Dockerfiles: `org.opencontainers.image.source` now points to the real repo org
  (`Gforce-Innovation-Kft`, was `gforceinnovation`)
- Docs: remaining stale "under 500 MB" sf-bulk claims corrected to the 600 MB budget
  (root/sf-bulk READMEs, CONTRIBUTING, PR template, tests/README, repo skills, AGENTS.md)
- Docs: removed stale "dependency review runs on PRs" claims (README, SECURITY.md) and the
  stale "push to main builds" trigger description (CLAUDE.md, references)
- CHANGELOG: added the missing `[1.6.1]` compare link; `[Unreleased]` now compares from
  `v1.6.1`

## [1.6.1] - 2026-07-03

### Fixed
- `sf-ci`: removed the `--allow-unauthenticated` / `--allow-insecure-repositories` apt
  workaround — GPG signature verification passes cleanly on arm64 again

### Changed
- `sf-devcontainer`: config files are now copied with `COPY --chown` instead of a recursive
  root `chown -R /home/vscode`, and the zsh setup (Oh My Zsh, Powerlevel10k, plugins) is
  consolidated into one layer — image shrinks from ~2.67 GB to ~2.01 GB
- All images: deprecated `LABEL maintainer` replaced with `org.opencontainers.image.authors`
- Docs: `CLAUDE.md` and `.claude/references/image-conventions.md` now record the 600 MB
  sf-bulk budget (raised in 1.6.0) instead of the stale 500 MB figure

### Added
- Ecosystem skills vendored via the skills CLI into `.agents/skills/` (pinned in
  `skills-lock.json`): `docker-expert`, `multi-stage-dockerfile`, `devcontainer-setup`
  (Trail of Bits), `platform-docs-get` (Salesforce official)

## [1.6.0] - 2026-07-01

### Added
- Showcase documentation: rewritten README (badges, comparison table, quick starts, supported
  tags, security, decision diagram), community-health files (CONTRIBUTING refresh,
  CODE_OF_CONDUCT, SECURITY), GitHub issue forms, PR template, and CODEOWNERS
- `docs/` image decision guide with a Mermaid diagram and a devcontainer GIF placeholder
- graphify knowledge graph tooling for token-efficient Claude navigation
  (`.claude/references/graphify.md`, `scripts/setup.sh` bootstrap, pre-commit refresh hook);
  `graphify-out/` is a git-ignored local build artifact

### Changed
- Bumped the Node.js runtime from 20 to **24 (Active LTS)** across all three images
  (`sf-ci`, `sf-devcontainer`, `sf-bulk`); Node 20 reaches end-of-life in 2026
- Raised the `sf-bulk` image-size budget to 600 MB (Node 24-alpine is larger than Node 20)
- CI builds only on version tags and pull requests (no redundant run on pushes to `main`)

### Removed
- `dependency-review` job (required the repo's Dependency Graph feature; non-functional without it)

## [1.5.0] - 2026-07-01

### Added
- `sf-bulk` — ultra-light Alpine image (Node 20, no Java) for bulk Salesforce org operations,
  kept under 500 MB and added to the build/test/push matrix
- Root `.devcontainer/devcontainer.json` for VS Code "Reopen in Container"
- AI pair-development layer: `.claude/references/`, `.claude/skills/`, committed
  `.claude/settings.json`, and `scripts/setup.sh` bootstrap
- Automated GitHub Releases with generated notes plus the matching `CHANGELOG.md` section
- Built-with-Claude badge and AI-Assisted Development section in the README

### Changed
- `dependency-review` job made non-blocking; test matrix `fail-fast` disabled

### Fixed
- `sf-ci` UID mismatch on ARC dind runners; XDG data directories pinned
- Trivy action version pin corrected

## [1.4.0] - 2026-02-12

### Changed
- Improved Docker images, CI/CD pipeline, and test reliability
- Added `CLAUDE.md` for Claude Code guidance

### Fixed
- Removed the Hadolint CI job; quoted shell variables in the `sf-devcontainer` Dockerfile
- Added Hadolint config to ignore `DL3008` (apt version pinning)

## [1.3.0] - 2026-02-03

### Added
- Pre-commit hook for YAML linting

### Changed
- Optimized Dockerfiles and workflows

## [1.1.0] - 2026-02-03

### Added
- Comprehensive pytest-testinfra testing framework for all images, with a dedicated CI test job
- Dependency review and Trivy vulnerability scanning in the CI workflows
- GitHub Actions CI/CD best-practice and AI-assistant instruction docs
- Python-related entries in `.gitignore`

### Changed
- Enhanced `.zshrc` configuration in `sf-devcontainer`

### Fixed
- Missing permissions for the CI test job
- Test-file naming convention in the CI workflow

## [1.0.0] - 2025-12-04

### Added
- Initial release of `sf-ci` and `sf-devcontainer` images
- Multi-platform build support (`linux/amd64` + `linux/arm64`)
- GitHub Actions workflow for building and pushing to Docker Hub

[Unreleased]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.7.0...HEAD
[1.7.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.6.1...v1.7.0
[1.6.1]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.6.0...v1.6.1
[1.6.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.1.0...v1.3.0
[1.1.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/releases/tag/v1.0.0
