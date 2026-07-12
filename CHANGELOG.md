# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Explicit `docker pull` / `FROM` snippets and tag/architecture sections in the root and
  per-image READMEs
- `sf-bulk/.dockerignore` (previously missing; sf-ci and sf-devcontainer already had one)
- CI: Docker Hub README/description sync on release (`peter-evans/dockerhub-description`)

### Changed
- GitHub repo metadata: description, topics, and Docker Hub homepage link set
- CI: dropped the unused `packages: write` permission (images push to Docker Hub, not GHCR)

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

[Unreleased]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.6.1...HEAD
[1.6.1]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.6.0...v1.6.1
[1.6.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.1.0...v1.3.0
[1.1.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/releases/tag/v1.0.0
