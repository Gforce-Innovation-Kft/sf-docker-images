# Contributing

Thanks for your interest in improving **sf-docker-images**. This guide covers local setup, how to
change an image, testing, and the release flow.

## Development setup

```bash
git clone https://github.com/Gforce-Innovation-Kft/sf-docker-images.git
cd sf-docker-images
./scripts/setup.sh          # verifies Docker + Python + gh, installs test deps
```

Build any image for your local platform:

```bash
docker build -t sf-ci:local ./sf-ci
docker build -t sf-devcontainer:local ./sf-devcontainer
docker build -t sf-bulk:local ./sf-bulk
```

## Adding or modifying an image

When you add or remove a tool, or change configuration, update **all** of the following in the
same PR:

1. The image's **`Dockerfile`**.
2. The image's **`README.md`**.
3. The matching **test file** in `tests/` (`test_sf_ci.py`, `test_sf_devcontainer.py`,
   `test_sf_bulk.py`).
4. **`CHANGELOG.md`** — add an entry under `[Unreleased]`.

Respect each image's role and budget:

| Image | Rule |
|-------|------|
| `sf-ci` | Stay minimal. No editors, no zsh, no interactive tools (tests assert vim/nano/zsh are absent). |
| `sf-devcontainer` | May be feature-rich; optimise for developer experience. |
| `sf-bulk` | Stay **under 500 MB**, **no Java** (both enforced by tests). |

Dockerfile conventions:

- Ubuntu images: clean apt caches in the same `RUN` layer (`rm -rf /var/lib/apt/lists/*`).
- Alpine images: `apk add --no-cache`, include `coreutils` (needed for `env -S` in the SF CLI
  shebang), and `deluser node` before creating the `ci` user (base ships `node` at UID 1000).

## Testing

```bash
pip install -r tests/requirements.txt

pytest tests/ -v                     # all images
pytest tests/test_sf_ci.py -v        # a single image
```

Each test builds the image, starts a container, and verifies OS, user/UID/shell, runtimes,
plugins, tools, env vars, and directory structure (plus size and no-Java checks for `sf-bulk`).
All tests must pass before a PR is merged; the same suite runs in CI along with a Trivy scan.

A pre-commit hook runs `yamllint` on staged YAML (config in [`.yamllint`](.yamllint)).

## Commit & PR conventions

We use [Conventional Commits](https://www.conventionalcommits.org/) — lowercase, atomic:

`feat:` · `fix:` · `docs:` · `test:` · `chore:` · `refactor:` · `ci:`

To open a PR:

```bash
git checkout -b feat/short-description
# make changes, update README + tests + CHANGELOG
git commit -m "feat: add <tool> to sf-ci"
git push origin feat/short-description
```

Then open a pull request against `main` and fill in the PR template checklist. Never force-push
shared branches.

## Release process

Releases are automated by [`.github/workflows/build-and-push.yml`](.github/workflows/build-and-push.yml)
on a version tag:

```bash
git tag -a v1.5.0 -m "Release v1.5.0"
git push origin v1.5.0
```

CI then builds all three images multi-arch, runs the tests + Trivy scan, pushes to Docker Hub
with semver tags plus SBOM and provenance, and opens a GitHub Release with notes from the
matching `CHANGELOG.md` section. Move the `[Unreleased]` entries into a dated version section
before tagging.

## Questions

Open an [issue](https://github.com/Gforce-Innovation-Kft/sf-docker-images/issues) or a
discussion. Please follow our [Code of Conduct](CODE_OF_CONDUCT.md).
