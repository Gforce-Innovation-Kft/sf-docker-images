# sf-ci

> Minimal Docker image for Salesforce CI/CD pipelines.

[![sf-ci](https://github.com/Gforce-Innovation-Kft/sf-docker-images/actions/workflows/image-sf-ci.yml/badge.svg)](https://github.com/Gforce-Innovation-Kft/sf-docker-images/actions/workflows/image-sf-ci.yml)
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
    '^https://github\.com/Gforce-Innovation-Kft/sf-docker-images/\.github/workflows/reusable-docker-image-build\.yml@.+$' \
  gforceinnovation/sf-ci:latest
```

Images published **before 2026-08-06** were signed by the old shared workflow and
verify only against that identity instead:

```text
^https://github\.com/Gforce-Innovation-Kft/shared-github-actions/\.github/workflows/docker-build-test-push\.yml@.+$
```

## What's inside

- **Node.js 24.x** (LTS) and **Java 17** (OpenJDK) — for Apex compile and `code-analyzer`.
- **Salesforce CLI v2** with the `sfdx-git-delta` plugin (delta deployments).
- **CI utilities**: git, jq, xmlstarlet, curl, unzip/zip.
- **Container-mode env**: `SFDX_CONTAINER_MODE`, `SFDX_DISABLE_DNS_CHECK`, `SF_AUTOUPDATE_DISABLE`,
  `SF_DISABLE_TELEMETRY`, `CI`.
- **User**: runs as **non-root `ci` (UID 1000)** at runtime.

> **Run as a UID this image knows: 1000 (`ci`) or 1001 (`runner`).** GitHub Actions bind-mounts
> `/github/home` owned by the runner's UID, and a container under a different UID cannot write
> it. For **GitHub-hosted runners add `options: --user 1001`** to the container job — that is the
> runner's UID. On ARC, set the runner pod's `securityContext.runAsUser` to whichever of the two
> matches.
>
> An *unregistered* UID will not work: `sf` calls Node's `os.userInfo()`, which fails when the
> UID has no `/etc/passwd` entry. Both 1000 and 1001 are baked in for exactly this reason.
> Versions before 3.0.0 ran as root and were immune to all of it.
>
> `--user 1001` is **required, not advisory**. Beyond `/github/home`, the runner creates the
> job's file-command files — `$GITHUB_OUTPUT`, `$GITHUB_ENV`, `$GITHUB_STEP_SUMMARY` — as
> `-rw-r--r-- 1001:1001`, so under any other UID the first step that sets an output fails with
> `Permission denied`. Overriding `HOME` is **not** a workaround: it fixes `sf` and leaves the
> file commands broken, which looks like a working job right up until it isn't.
>
> Container jobs also default to `sh`, which has no `-o pipefail`. Set
> `defaults.run.shell: bash` or every `set -euo pipefail` step dies with `Illegal option`.
>
> Full rules, a failure decoder, and how to reproduce an Actions container job locally:
> **[docs/using-in-github-actions.md](../docs/using-in-github-actions.md)**.

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

- No interactive shell enhancements (bash only — the zsh + Starship setup lives in
  `sf-devcontainer`).
- No text editors (vim, nano) — asserted absent by the tests.
- Only the `sfdx-git-delta` plugin.
- apt caches cleaned in the same layer.

Need Java-free bulk data work? Use [`sf-bulk`](../sf-bulk/README.md). Developing locally in VS
Code? Use [`sf-devcontainer`](../sf-devcontainer/README.md).

## Building locally

```bash
docker build -t sf-ci:local .
```
