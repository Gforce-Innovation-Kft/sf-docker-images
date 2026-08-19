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

   | Repository | Visibility | Purpose |
   |---|---|---|
   | `gforceinnovation/sf-devcontainer` | public | published image |
   | `gforceinnovation/sf-ci` | public | published image |
   | `gforceinnovation/sf-bulk` | public | published image |
   | `gforceinnovation/sf-ci-e2e` | **public** | throwaway E2E candidates (`pr-<N>` tags) |

   `sf-ci-e2e` must exist and be **public** before the sf-ci E2E gate can pass: the
   downstream repo pulls the candidate anonymously. Its visibility is set here by hand and
   cannot be set from CI, which is why `cleanup` deletes the **tag** and never the
   repository — a recreated repository comes back private.

2. **Create an access token:**
   - Docker Hub → Account Settings → Security → Access Tokens
   - Scope: **Read, Write & Delete** — not Read/Write. `docker push` works with Read/Write,
     but two other things silently 403 without Delete: the release job's README sync
     (the v1.7.0 failure) and the E2E cleanup deleting `pr-<N>` tags.
   - Save it securely; Docker Hub shows it once.

### 3. Configure GitHub Secrets

**Repository** secrets (Settings → Secrets and variables → Actions):

- `DOCKERHUB_TOKEN` — the Read/Write/Delete token from above

**Organization** secrets and variables, shared with this repo — these belong to the
`gforce-ci-bot` GitHub App and are used by the sf-ci E2E gate to dispatch into
`sf-develop-demo`. Setup guide:
[`shared-github-actions/docs/github-app-setup.md`](https://github.com/Gforce-Innovation-Kft/shared-github-actions/blob/main/docs/github-app-setup.md).

- `vars.GFORCE_CI_APP_ID` — the App's ID or client ID
- `secrets.GFORCE_CI_APP_PRIVATE_KEY` — the App's PEM private key

The workflow uses `gforceinnovation` as the Docker Hub username by default. If your username is different, update the `dockerhub-username` input default in `.github/workflows/reusable-docker-image-build.yml`.

### 4. Test Locally

Before pushing your first tag, run the image test suite. It is
[pytest-testinfra](https://testinfra.readthedocs.io/): each suite builds the image if it is
not already present, starts a container, and asserts what is in it — and what must not be.

```bash
pip install -r tests/requirements.txt

pytest tests/                    # all three images
pytest tests/test_sf_ci.py -v    # just one
```

Docker must be running. A suite takes a few minutes on the first run because it builds the
image; afterwards it reuses `<image>:test` if present.

### 5. Create Your First Release

Once everything is set up and tested:

```bash
# Create and push a tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

This triggers `release.yml`, which builds **every** image (not only the ones the diff
touched, so `latest` stays coherent across the set) and for each one:
- builds and runs its pytest suite
- pushes multi-platform to Docker Hub, with SBOM and provenance
- signs the manifest with cosign (keyless, GitHub OIDC)
- reads the tool versions back out of the built image into a version report

then creates one GitHub Release: generated notes, the matching `CHANGELOG.md` section, and
a tool-version table per image.

## Verifying the Setup

After pushing a tag, check:

1. **GitHub Actions**: Go to the Actions tab to see the workflow running
2. **Docker Hub**: Verify images are published:
   - https://hub.docker.com/r/gforceinnovation/sf-devcontainer
   - https://hub.docker.com/r/gforceinnovation/sf-ci
   - https://hub.docker.com/r/gforceinnovation/sf-bulk
3. **GitHub Releases**: Check the Releases section for auto-generated notes

## Using the Images

Once published, you can pull the images:

```bash
docker pull gforceinnovation/sf-devcontainer:latest
docker pull gforceinnovation/sf-ci:latest
docker pull gforceinnovation/sf-bulk:latest
```

In CI, pin the exact version instead of `latest` — the image is where the Node, SF CLI and
Java versions come from, so an unpinned tag lets the toolchain change under a green build.

## Troubleshooting

### Workflow fails at Docker login
- Verify `DOCKERHUB_TOKEN` is set correctly
- Check the token scope is **Read, Write & Delete**

### README sync or E2E cleanup 403s, but the push worked
The token is Read/Write, not Read/Write/Delete. Both of those call the Docker Hub REST API,
which needs Delete; `docker push` does not. Regenerate the token with the wider scope.

### Tests fail
- Run them locally to debug: `pytest tests/test_sf_ci.py -v`
- Check Docker is running
- Remember the suite reuses an existing `<image>:test`; `docker rmi sf-ci:test` forces a rebuild
- Verify all dependencies are in the Dockerfiles

### Images not pushed to Docker Hub
- Verify repositories exist on Docker Hub
- Check repository names match in the workflow file
- Ensure you're pushing a tag (not just a commit)
- An image needs BOTH an `image-<name>.yml` and a `release.yml` matrix entry — with only the
  first it is tested on PRs and never published, and nothing reports that

### E2E tier 2 fails with `Error response from daemon: denied`
`gforceinnovation/sf-ci-e2e` is missing or private. It must exist and be public; see step 2.

### E2E tier 2 fails with "No App token was minted"
`vars.GFORCE_CI_APP_ID` / `secrets.GFORCE_CI_APP_PRIVATE_KEY` are not set at the org or not
shared with this repo — an org secret that is not shared arrives as an empty string, which
looks identical to never setting one.

## Next Steps

- Customize the images for your needs
- Add more tests
- Set up branch protection rules
- Configure automated scanning (e.g., Snyk, Trivy)
