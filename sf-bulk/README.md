# sf-bulk

> Ultra-light Alpine image for bulk Salesforce org operations — no Java.

[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-D97757?logo=anthropic&logoColor=white)](https://claude.com/claude-code)

Part of [**sf-docker-images**](../README.md). An Alpine-based image for bulk Salesforce org
operations. No Java, minimal footprint — kept **under 500 MB** uncompressed (~410 MB).

## Features

- **Alpine base** (`node:20-alpine` + `coreutils`): tiny image, `env -S` support for the SF CLI shebang
- **Node.js 20.x**: Latest LTS version (no Java)
- **Salesforce CLI**: Latest v2 with the `sfdx-git-delta` plugin
- **Utilities**: bash, curl, git, jq, unzip, libc6-compat
- **Container-mode env**: `SFDX_CONTAINER_MODE`, `SFDX_DISABLE_DNS_CHECK`, `SF_AUTOUPDATE_DISABLE`,
  `SF_DISABLE_TELEMETRY`, `CI` — XDG dirs pinned to `/opt/sf-data` and `/opt/sf-config`
- **Runs as root** at runtime (bypasses ARC dind UID mismatch, same as `sf-ci`)

## When to use

Use `sf-bulk` for lightweight, high-volume org operations that do **not** need Java — data
loads, `sf data` bulk API jobs, org queries, and delta calculations — where pull time and
footprint matter. For Apex compilation / scanning use `sf-ci` (has Java 17).

## Usage

### GitHub Actions

```yaml
jobs:
  bulk-load:
    runs-on: ubuntu-latest
    container:
      image: gforceinnovation/sf-bulk:latest
    steps:
      - uses: actions/checkout@v4
      - name: Authenticate to Salesforce
        run: |
          echo "${{ secrets.SF_AUTH_URL }}" > authfile
          sf org login sfdx-url --sfdx-url-file authfile
      - name: Bulk upsert
        run: sf data upsert bulk --sobject Account --file data/accounts.csv --external-id Id
```

### Docker

```bash
docker run -v "$(pwd):/workspace" gforceinnovation/sf-bulk:latest sf org list
```

## Image size

Kept under 500 MB by design:

- Alpine base instead of Ubuntu
- **No Java** (no JRE/JDK)
- Only the `sfdx-git-delta` plugin
- No editors or interactive tooling

`tests/test_sf_bulk.py` fails the build if the image exceeds 500 MB or if Java is present.

## Building locally

```bash
docker build -t sf-bulk:local .
```
