---
name: testing-images
description: >-
  Run and interpret the pytest-testinfra container tests for the Salesforce Docker images.
  Use when asked to test an image, add a new assertion, debug a failing container test, or
  check an image size budget.
---

# Testing the images

Tests use **pytest-testinfra** in `tests/`. Each `tests/test_sf_<image>.py` builds the
image (once, reusing `<image>:test` if present), starts a container, and asserts against it.

## Run

```bash
pip install -r tests/requirements.txt   # first time only
pytest tests/ -v                          # all three images
pytest tests/test_sf_ci.py -v             # one image
pytest tests/test_sf_bulk.py -v
```

The fixture builds `<image>:test` if missing, so rebuild manually after changing a Dockerfile:

```bash
docker build -t sf-ci:test ./sf-ci && pytest tests/test_sf_ci.py -v
```

## How it works

- A module-scoped `host` fixture (`@pytest.fixture(scope="module")`) checks for `<image>:test`
  via `docker image inspect`, builds it if absent, then `docker run -d ... sleep infinity`
  and yields a `testinfra.get_host("docker://<container>")`; it stops the container on teardown.
- Assertions use the testinfra API: `host.run("cmd")` (`.rc`, `.stdout`, `.stderr`),
  `host.user("ci")` (`.uid`, `.shell`), `host.file("/path")` (`.exists`, `.is_directory`,
  `.mode`, `.user`), `host.system_info.distribution`.

Each suite mirrors the image's rules: OS, user/UID/shell, runtimes, `sf version`, plugins,
present tools, **absent** forbidden tools, env vars, `/workspace`, and (sf-bulk) the size cap.

**Some assertions cannot use the `host` fixture.** The fixture runs one long-lived container as
the image's default user, so anything about a *different* user, or about mounts, has to shell
out to `docker run` itself with `subprocess`. That is why
`test_sf_cli_works_as_runner_uid` and `test_github_home_writable_as_runner_uid` are plain
functions with no `host` argument — they run `--user 1001` and mount a volume chowned to 1001
to reproduce what GitHub does to a container job. Follow that pattern for any UID, mount, or
entrypoint behaviour; do not try to bend the fixture to it.

**These tests still cannot see everything.** `docker run` is not a GitHub Actions container job:
it does not bind-mount `/github/home` or the runner file-command dir, and it does not override
the entrypoint. That gap is covered by the E2E tier-1 probes in `image-sf-ci.yml`, not here.
A green suite is necessary, not sufficient.

## Adding an assertion

Add a `def test_<thing>(host):` in the relevant file using `host.run(...)` / `host.file(...)`
and plain `assert`. Keep it aligned with the Dockerfile/README change you made (see the
`building-a-docker-image` skill). Every added/removed tool needs a matching test.

## Interpreting failures

- **sf-bulk size assertion failed** — the image grew past 600 MB; slim the layers, don't
  raise the cap without a decision.
- **`test_no_interactive_tools` / `test_minimal_footprint` (sf-ci)** — an editor/zsh leaked
  in; remove it.
- **plugin/env test failed** — check the `sf plugins install` step and the `ENV` block.
- **build failed inside the fixture** — run the raw `docker build ./sf-<image>` to see the log.
