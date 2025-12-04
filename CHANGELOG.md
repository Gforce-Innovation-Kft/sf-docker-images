# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of sf-devcontainer image
- Initial release of sf-ci image
- GitHub Actions workflows for automated building and testing
- Comprehensive test suite for both images
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
- Non-root user for security
