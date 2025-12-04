# Contributing to Salesforce Docker Images

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/gforceinnovation/sf-docker-images.git
   cd sf-docker-images
   ```

2. **Build images locally**
   ```bash
   # Build sf-devcontainer
   docker build -t sf-devcontainer:local ./sf-devcontainer
   
   # Build sf-ci
   docker build -t sf-ci:local ./sf-ci
   ```

3. **Run tests**
   ```bash
   chmod +x tests/*.sh
   ./tests/run-all-tests.sh
   ```

## Making Changes

### Adding New Tools

When adding new tools to either image:

1. Update the Dockerfile
2. Update the relevant README
3. Add tests in the corresponding test script
4. Document the changes

### Image Guidelines

**sf-devcontainer:**
- Full-featured development environment
- Include interactive tools and enhancements
- Prioritize developer experience

**sf-ci:**
- Keep it lightweight and minimal
- Only include tools needed for CI/CD
- Optimize for build speed and size
- No interactive shell enhancements

## Testing

All changes must pass the test suite:

```bash
./tests/run-all-tests.sh
```

Add new tests when:
- Adding new tools or dependencies
- Changing configuration
- Modifying environment variables

## Pull Request Process

1. **Fork the repository** and create a new branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the guidelines above

3. **Test your changes**
   ```bash
   ./tests/run-all-tests.sh
   ```

4. **Commit with clear messages**
   ```bash
   git commit -m "feat: add new tool to sf-ci image"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Commit Message Convention

We follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `chore:` Maintenance tasks
- `refactor:` Code refactoring

## Release Process

Releases are automated via GitHub Actions:

1. Create and push a tag:
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

2. GitHub Actions will:
   - Run tests
   - Build and push images to Docker Hub
   - Create a GitHub release with auto-generated notes

## Questions?

Open an issue or start a discussion on GitHub.
