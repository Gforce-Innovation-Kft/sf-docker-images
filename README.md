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

## Development

### Building Images Locally

```bash
# Build sf-devcontainer
docker build -t sf-devcontainer:local ./sf-devcontainer

# Build sf-ci
docker build -t sf-ci:local ./sf-ci
```

### Running Tests

```bash
# Test sf-devcontainer
./tests/test-sf-devcontainer.sh

# Test sf-ci
./tests/test-sf-ci.sh
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
