# sf-ci

> Minimal Docker image for Salesforce CI/CD pipelines.

[![CI](https://github.com/Gforce-Innovation-Kft/sf-docker-images/actions/workflows/build-and-push.yml/badge.svg)](https://github.com/Gforce-Innovation-Kft/sf-docker-images/actions/workflows/build-and-push.yml)
[![Release](https://img.shields.io/github/v/release/Gforce-Innovation-Kft/sf-docker-images?sort=semver)](https://github.com/Gforce-Innovation-Kft/sf-docker-images/releases)
[![sf-ci size](https://img.shields.io/docker/image-size/gforceinnovation/sf-ci/latest?label=size)](https://hub.docker.com/r/gforceinnovation/sf-ci)
[![sf-ci pulls](https://img.shields.io/docker/pulls/gforceinnovation/sf-ci?label=pulls)](https://hub.docker.com/r/gforceinnovation/sf-ci)
[![License](https://img.shields.io/github/license/Gforce-Innovation-Kft/sf-docker-images)](https://github.com/Gforce-Innovation-Kft/sf-docker-images/blob/main/LICENSE)
[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-D97757?logo=anthropic&logoColor=white)](https://claude.com/claude-code)

Part of [**sf-docker-images**](../README.md). A lean `ubuntu:22.04` runner with Node.js, Java,
and the Salesforce CLI — nothing else. Kept deliberately small (~840 MB); the test suite fails
the build if editors or interactive shells sneak in.

## Pull

```bash
docker pull gforceinnovation/sf-ci:latest
```

```dockerfile
FROM gforceinnovation/sf-ci:1.7.0
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
  gforceinnovation/sf-ci:latest
```

## What's inside

- **Node.js 24.x** (LTS) and **Java 17** (OpenJDK) — for Apex compile and `code-analyzer`.
- **Salesforce CLI v2** with the `sfdx-git-delta` plugin (delta deployments).
- **CI utilities**: git, jq, xmlstarlet, curl, unzip/zip.
- **Container-mode env**: `SFDX_CONTAINER_MODE`, `SFDX_DISABLE_DNS_CHECK`, `SF_AUTOUPDATE_DISABLE`,
  `SF_DISABLE_TELEMETRY`, `CI`.
- **User**: non-root `ci` (UID 1000) created at build time. Runs as **root at runtime** to avoid
  UID mismatches on ARC dind self-hosted runners.

## Usage

### GitHub Actions

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    container: gforceinnovation/sf-ci:latest
    steps:
      - uses: actions/checkout@v4
      - name: Authenticate to Salesforce
        run: |
          echo "${{ secrets.SF_AUTH_URL }}" > authfile
          sf org login sfdx-url --sfdx-url-file authfile
      - name: Deploy to Salesforce
        run: sf project deploy start
```

### GitHub Actions — delta validation on pull requests

The bundled `sfdx-git-delta` plugin turns a git diff into a deploy manifest, so PRs
validate only what changed:

```yaml
jobs:
  validate:
    runs-on: ubuntu-latest
    container: gforceinnovation/sf-ci:latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # sfdx-git-delta diffs git history
      - name: Authenticate to Salesforce
        run: |
          echo "${{ secrets.SF_AUTH_URL }}" > authfile
          sf org login sfdx-url --sfdx-url-file authfile --set-default
      - name: Generate delta package
        run: |
          mkdir -p delta
          sf sgd source delta --from "origin/${{ github.base_ref }}" --to HEAD --output-dir delta
      - name: Validate delta (check-only)
        run: |
          sf project deploy start --manifest delta/package/package.xml \
            --dry-run --test-level RunLocalTests
```

### GitHub Actions — matrix over orgs

One job definition, one environment per org (each GitHub Environment holds its own
`SF_AUTH_URL` secret — add required reviewers on the environment to gate promotion):

```yaml
jobs:
  deploy:
    strategy:
      matrix:
        org: [qa, uat]
    runs-on: ubuntu-latest
    container: gforceinnovation/sf-ci:latest
    environment: ${{ matrix.org }}
    steps:
      - uses: actions/checkout@v4
      - name: Authenticate to ${{ matrix.org }}
        run: |
          echo "${{ secrets.SF_AUTH_URL }}" > authfile
          sf org login sfdx-url --sfdx-url-file authfile --set-default
      - name: Deploy
        run: sf project deploy start
```

### GitLab CI

```yaml
deploy:
  image: gforceinnovation/sf-ci:latest
  script:
    - echo "$SF_AUTH_URL" > authfile
    - sf org login sfdx-url --sfdx-url-file authfile
    - sf project deploy start
```

### Docker

```bash
docker run --rm -v "$(pwd):/workspace" gforceinnovation/sf-ci:latest sf org list
```

## Why it's small

- No interactive shell enhancements (zsh, Oh My Zsh, Powerlevel10k).
- No text editors (vim, nano) — asserted absent by the tests.
- Only the `sfdx-git-delta` plugin.
- apt caches cleaned in the same layer.

Need Java-free bulk data work? Use [`sf-bulk`](../sf-bulk/README.md). Developing locally in VS
Code? Use [`sf-devcontainer`](../sf-devcontainer/README.md).

## Building locally

```bash
docker build -t sf-ci:local .
```
