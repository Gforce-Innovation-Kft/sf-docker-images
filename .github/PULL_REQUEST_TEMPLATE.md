# Pull Request

## What & why

<!-- What does this change, and why? Link any related issue (e.g. Closes #12). -->

## Type of change

- [ ] `feat` — new capability
- [ ] `fix` — bug fix
- [ ] `docs` — documentation only
- [ ] `test` — tests only
- [ ] `chore` / `refactor` / `ci`

## Affected image(s)

- [ ] sf-ci
- [ ] sf-devcontainer
- [ ] sf-bulk
- [ ] repo tooling / CI only

## Checklist

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] Updated the image's `Dockerfile`, `README.md`, and test file together (if tools changed)
- [ ] Updated `CHANGELOG.md` under `[Unreleased]`
- [ ] Size budget respected (sf-ci minimal; sf-bulk < 600 MB, no Java)
- [ ] Commits follow Conventional Commits
