# sf-ci

> Minimal Docker image for Salesforce CI/CD pipelines.

[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-D97757?logo=anthropic&logoColor=white)](https://claude.com/claude-code)

Part of [**sf-docker-images**](../README.md). A lean `ubuntu:22.04` runner with Node.js, Java,
and the Salesforce CLI — nothing else. Kept deliberately small (~840 MB); the test suite fails
the build if editors or interactive shells sneak in.

## Pull

```bash
docker pull gforceinnovation/sf-ci:latest
```

```dockerfile
FROM gforceinnovation/sf-ci:1.6.1
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
