# Using these images in GitHub Actions

The rules for running `sf-ci` (and its siblings) as a **container job**. Every rule
below is derived from a run on a GitHub-hosted runner, not from reasoning about
what ought to work — the evidence is in [Appendix A](#appendix-a--the-evidence).

---

## The four rules

### Rule 1 — always pass `options: --user 1001`

```yaml
container:
  image: gforceinnovation/sf-ci:3.0.0
  options: --user 1001
```

This is not optional and it is not a leftover. The runner creates the job's
**file-command files** — the ones behind `$GITHUB_OUTPUT`, `$GITHUB_ENV` and
`$GITHUB_STEP_SUMMARY` — as `-rw-r--r-- 1001:1001`. A container running under any
other UID gets `Permission denied` the moment a step writes a step output.

Since v3.0.0 the image's *default* user is `ci` (1000), so **omitting `--user`
silently breaks every step that sets an output.**

> **What v3.0.0 changed:** it dropped `--user root`, not `--user`. Registering
> `runner` (1001) statically is what made unprivileged container jobs possible.
> The goal was *unprivileged*, not *unspecified*.

### Rule 2 — never `--user root`, and never an unregistered UID

Only two UIDs are baked into `/etc/passwd`:

| UID | Account | Use it for |
|-----|---------|-----------|
| 1000 | `ci` | local `docker run`, self-hosted runners whose runner UID is 1000 |
| 1001 | `runner` | **GitHub-hosted container jobs** |

An unregistered UID cannot work, and no image change can fix it: `sf` (oclif)
calls Node's `os.userInfo()`, which throws
`uv_os_get_passwd returned ENOENT` when the UID has no passwd entry. The usual
remedy — an entrypoint that appends a passwd line — never runs, because GitHub
Actions container jobs override `ENTRYPOINT` with `--entrypoint tail`.

On ARC, set the runner pod's `securityContext.runAsUser` to 1000 or 1001 to match.

### Rule 3 — pin an exact version, never `latest`

```yaml
image: gforceinnovation/sf-ci:3.0.0     # ✅
image: gforceinnovation/sf-ci:latest    # ❌ silently changes under you
```

`latest` moves. The whole point of a controlled runtime is that
`git commit + image tag` reproduces a build; a floating tag gives that up.

Beware that the tag series is **not** what a casual reader expects: the current
release is `3.0.0`, and everything **before 3.0.0 ran as root** — so a workflow
pinned to `1.7.0` or `2.0.0` and passing `--user 1001` fails outright, because
those images never registered UID 1001.

| Tag | Runs as | `--user 1001` works? |
|-----|---------|----------------------|
| `1.x`, `2.0.0` | root | ❌ no 1001 in `/etc/passwd` |
| `3.0.0`, `latest` | `ci` (1000) | ✅ |

### Rule 4 — set `defaults.run.shell: bash`

```yaml
defaults:
  run:
    shell: bash
```

Container jobs default to `sh`, which has no `-o pipefail`. Without this, every
step beginning `set -euo pipefail` dies with `Illegal option -o pipefail` — and
it fails at the *shell* level, so the error names the option rather than
anything you wrote.

Composite actions are unaffected when their steps declare `shell: bash`
individually, which is why an action can look fine while the workflow calling it
does not.

---

## The canonical job

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    container:
      image: gforceinnovation/sf-ci:3.0.0   # Rule 3: exact version
      options: --user 1001                  # Rule 1: the runner's UID
    defaults:
      run:
        shell: bash                         # Rule 4: sh has no pipefail
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        run: |
          set -euo pipefail
          sf project deploy start --target-org "$ORG"
```

---

## Failure decoder

When a container job breaks, the message rarely names the real cause. This table
maps what you see to what is wrong.

| Symptom | Cause | Fix |
|---------|-------|-----|
| `uv_os_get_passwd returned ENOENT` at `os.userInfo` | Running as a UID with no passwd entry — usually `--user 1001` against a pre-3.0.0 tag | Rule 3, then Rule 1 |
| `Permission denied` writing `/__w/_temp/_runner_file_commands/...` | Not running as 1001; the file commands are owned by 1001 | Rule 1 |
| `mkdir: cannot create directory '/github/home/.sf': Permission denied` | Same — `/github/home` is bind-mounted owned by the runner | Rule 1 |
| `set: Illegal option -o pipefail` | Step ran under `sh` | Rule 4 |
| Works locally, fails in Actions | Local `docker run` has no `/github/home` mount and defaults to `ci` (1000) | Reproduce with the recipe below |

### Reproducing an Actions container job locally

```bash
docker volume create gh-home
docker run --rm --user 0 -v gh-home:/github/home \
  --entrypoint chown gforceinnovation/sf-ci:3.0.0 1001:0 /github/home

docker run --rm --user 1001 -v gh-home:/github/home -e HOME=/github/home \
  --entrypoint bash gforceinnovation/sf-ci:3.0.0 -c 'sf version && mkdir -p $HOME/.sf'
```

Omitting the `--user` and the `/github/home` mount is why a broken workflow can
look perfectly healthy on a laptop.

---

## Appendix A — the evidence

Run on `ubuntu-24.04`, runner 2.336.0, image `gforceinnovation/sf-ci:3.0.0`.
File-command dir listing from inside the container:

```
-rw-r--r-- 1 1001 1001 0 add_path_c9b15df2-...
-rw-r--r-- 1 1001 1001 0 artifacts_c9b15df2-...
```

| Variant | uid/gid | `$GITHUB_OUTPUT` | `sf version` | `mkdir $HOME/.sf` |
|---------|---------|------------------|--------------|-------------------|
| no `--user`, runner `HOME` | 1000 / 1000 `ci` | ❌ denied | ❌ rc=1 | ❌ denied |
| no `--user`, `HOME=/home/ci` | 1000 / 1000 `ci` | ❌ denied | ✅ rc=0 | ✅ rc=0 |
| `--user 1001` | 1001 / 0 `runner` | ✅ rc=0 | ✅ rc=0 | ✅ rc=0 |

The middle row is the trap: overriding `HOME` makes `sf` work, so the job looks
fixed — right up to the first step that sets an output. Since every composite
action writes `$GITHUB_OUTPUT`, that is immediate in practice.

Local matrix against the same image (no `/github/home` mount):

| `--user` | `sf` runs | Failure |
|----------|-----------|---------|
| none (1000) | ✅ | — |
| 1000 | ✅ | — |
| 1001 | ✅ | — |
| 1234 | ❌ | `uv_os_get_passwd ENOENT` |
| root | ✅ | — (but forbidden by Rule 2) |
