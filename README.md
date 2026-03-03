# Salesforce Docker Images

A collection of Docker images optimized for Salesforce development and CI/CD workflows.

## Available Images

### sf-devcontainer

A full-featured development container for Salesforce development with:

- Node.js 20.x
- Java 17 (OpenJDK)
- Salesforce CLI with plugins
- Zsh with Oh My Zsh and Powerlevel10k
- Development tools and utilities

**Docker Hub:** `gforceinnovation/sf-devcontainer`

**Usage:**

```bash
docker pull gforceinnovation/sf-devcontainer:latest
```

### sf-ci

A lightweight CI/CD optimized image for Salesforce automation with:

- Node.js 20.x
- Java 17 (OpenJDK)
- Salesforce CLI with essential plugins
- CI/CD utilities (jq, xmlstarlet)

**Docker Hub:** `gforceinnovation/sf-ci`

**Usage:**

```bash
docker pull gforceinnovation/sf-ci:latest
```

### sf-bulk

An ultra-lightweight Alpine-based image for bulk Salesforce org operations with:

- Node.js 20.x (Alpine base — no Java, ~300MB)
- Salesforce CLI with `sfdx-git-delta` plugin
- Essentials only: bash, curl, git, jq, unzip
- XDG dirs pinned to `/opt/sf-*` for any-UID runner compatibility
- Runs as root at runtime (works with ARC dind runners)

**Docker Hub:** `gforceinnovation/sf-bulk`

**Usage:**

```bash
docker pull gforceinnovation/sf-bulk:latest
```

## Development

### Building Images Locally

**Build for your local platform only (faster):**

```bash
# Build sf-devcontainer
docker build -t sf-devcontainer:local ./sf-devcontainer

# Build sf-ci
docker build -t sf-ci:local ./sf-ci

# Build sf-bulk
docker build -t sf-bulk:local ./sf-bulk
```

**Build for multiple platforms (Mac ARM64 + Intel/AMD64):**

First, create a builder that supports multi-platform builds:

```bash
docker buildx create --name multiplatform --use
docker buildx inspect --bootstrap
```

Then build and push to Docker Hub:

```bash
# Build and push sf-devcontainer for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag gforceinnovation/sf-devcontainer:1.0.1 \
  --tag gforceinnovation/sf-devcontainer:latest \
  --push \
  ./sf-devcontainer

# Build and push sf-ci for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag gforceinnovation/sf-ci:1.5.0 \
  --tag gforceinnovation/sf-ci:latest \
  --push \
  ./sf-ci

# Build and push sf-bulk for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag gforceinnovation/sf-bulk:1.0.0 \
  --tag gforceinnovation/sf-bulk:latest \
  --push \
  ./sf-bulk
```

**Note:** Multi-platform builds require pushing to a registry. You cannot load multi-platform images directly to your local Docker daemon.

### Running Tests

```bash
pip install -r tests/requirements.txt

# Run all tests
pytest tests/ -v

# Run tests for a single image
pytest tests/test_sf_ci.py -v
pytest tests/test_sf_devcontainer.py -v
pytest tests/test_sf_bulk.py -v
```

## CI/CD

Images are automatically built and pushed to Docker Hub when tags are created:

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

This will:

1. Build both Docker images
2. Push to Docker Hub with version tag and `latest`
3. Generate release notes automatically

## License

MIT
