# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Showcase documentation: rewritten README (badges, comparison table, quick starts, supported
  tags, security, decision diagram), community-health files (CONTRIBUTING refresh,
  CODE_OF_CONDUCT, SECURITY), GitHub issue forms, PR template, and CODEOWNERS
- `docs/` image decision guide with a Mermaid diagram and a devcontainer GIF placeholder

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

[Unreleased]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.5.0...HEAD
[1.5.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.1.0...v1.3.0
[1.1.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Gforce-Innovation-Kft/sf-docker-images/releases/tag/v1.0.0
