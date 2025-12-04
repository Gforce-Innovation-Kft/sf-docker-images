# Salesforce Docker Images - Setup Guide

This guide will help you set up the repository and configure Docker Hub integration.

## Prerequisites

- Docker installed locally
- GitHub account
- Docker Hub account

## Initial Setup

### 1. Create GitHub Repository

```bash
cd /Users/gaborbalint.demeter/gforce/sf-docker-images
git init
git add .
git commit -m "feat: initial commit with sf-devcontainer and sf-ci images"
```

Create a new repository on GitHub named `sf-docker-images`, then:

```bash
git remote add origin https://github.com/gforceinnovation/sf-docker-images.git
git branch -M main
git push -u origin main
```

### 2. Set Up Docker Hub

1. **Create repositories on Docker Hub:**
   - `gforceinnovation/sf-devcontainer`
   - `gforceinnovation/sf-ci`

2. **Create an access token:**
   - Go to Docker Hub → Account Settings → Security → Access Tokens
   - Create a new token with Read/Write permissions
   - Save the token securely

### 3. Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

- `DOCKERHUB_TOKEN`: Your Docker Hub access token

The workflow uses `gforceinnovation` as the Docker Hub username by default. If your username is different, update the `DOCKERHUB_USERNAME` in `.github/workflows/build-and-push.yml`.

### 4. Test Locally

Before pushing your first tag, test the images locally:

```bash
# Make test scripts executable
chmod +x tests/*.sh

# Run all tests
./tests/run-all-tests.sh
```

### 5. Create Your First Release

Once everything is set up and tested:

```bash
# Create and push a tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

This will trigger the GitHub Actions workflow to:
- Build both Docker images
- Run all tests
- Push images to Docker Hub
- Create a GitHub release with auto-generated notes

## Verifying the Setup

After pushing a tag, check:

1. **GitHub Actions**: Go to the Actions tab to see the workflow running
2. **Docker Hub**: Verify images are published:
   - https://hub.docker.com/r/gforceinnovation/sf-devcontainer
   - https://hub.docker.com/r/gforceinnovation/sf-ci
3. **GitHub Releases**: Check the Releases section for auto-generated notes

## Using the Images

Once published, you can pull the images:

```bash
docker pull gforceinnovation/sf-devcontainer:latest
docker pull gforceinnovation/sf-ci:latest
```

## Troubleshooting

### Workflow fails at Docker login
- Verify `DOCKERHUB_TOKEN` secret is set correctly
- Check that the token has Read/Write permissions

### Tests fail
- Run tests locally to debug: `./tests/run-all-tests.sh`
- Check Docker is running
- Verify all dependencies are in the Dockerfiles

### Images not pushed to Docker Hub
- Verify repositories exist on Docker Hub
- Check repository names match in the workflow file
- Ensure you're pushing a tag (not just a commit)

## Next Steps

- Customize the images for your needs
- Add more tests
- Set up branch protection rules
- Configure automated scanning (e.g., Snyk, Trivy)
