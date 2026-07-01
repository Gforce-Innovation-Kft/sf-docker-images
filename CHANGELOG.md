# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.0] - 2026-07-01

### Added
- Initial release of sf-devcontainer image
- Initial release of sf-ci image
- Initial release of sf-bulk image (ultralight Alpine, no Java, under 500 MB)
- GitHub Actions workflows for automated building and testing
- Automated GitHub Releases with generated notes + CHANGELOG section on version tags
- Root `.devcontainer/devcontainer.json` for VS Code "Reopen in Container"
- AI pair-development layer: `.claude/references/`, `.claude/skills/`, committed
  `.claude/settings.json`, and `scripts/setup.sh` bootstrap
- Comprehensive pytest-testinfra test suite for all three images
- Docker Hub integration

### sf-devcontainer Features
- Node.js 20.x LTS
- Java 17 (OpenJDK)
- Salesforce CLI with plugins (code-analyzer, sfdx-git-delta, sfdx-browserforce-plugin)
- Oh My Zsh with Powerlevel10k theme
- Zsh plugins (autosuggestions, syntax-highlighting, completions)
- Development tools (vim, nano, git, build-essential)
- Utilities (jq, xmlstarlet, tree, htop)

### sf-ci Features
- Node.js 20.x LTS
- Java 17 (OpenJDK)
- Salesforce CLI with sfdx-git-delta plugin
- CI utilities (jq, xmlstarlet)
- Optimized for CI/CD pipelines
- Non-root `ci` user (runs as root at runtime for ARC dind compatibility)

### sf-bulk Features
- Alpine base (node:20-alpine + coreutils), Node.js 20.x LTS, no Java
- Salesforce CLI with sfdx-git-delta plugin
- Utilities (bash, curl, git, jq, unzip, libc6-compat)
- XDG dirs pinned to /opt/sf-data and /opt/sf-config; runs as root at runtime
- Kept under 500 MB uncompressed (enforced by tests)
