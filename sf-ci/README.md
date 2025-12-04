# SF CI

Lightweight Docker image optimized for Salesforce CI/CD pipelines.

## Features

- **Node.js 20.x**: Latest LTS version
- **Java 17**: OpenJDK for Salesforce operations
- **Salesforce CLI**: Latest version with essential plugins:
  - sfdx-git-delta (for delta deployments)
- **CI Utilities**: jq, xmlstarlet for pipeline processing
- **Minimal footprint**: Only essential tools included
- **Non-root user**: Runs as `ci` user for security

## Usage

### GitHub Actions

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    container:
      image: gforceinnovation/sf-ci:latest
    steps:
      - uses: actions/checkout@v3
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
docker run -v $(pwd):/workspace gforceinnovation/sf-ci:latest sf org list
```

## Image Size

This image is optimized for CI/CD and is significantly smaller than the full devcontainer image:
- No interactive shell enhancements (Zsh, Oh My Zsh, Powerlevel10k)
- No text editors (vim, nano)
- Minimal CLI plugins
- Cleaned apt cache

## Building Locally

```bash
docker build -t sf-ci:local .
```
