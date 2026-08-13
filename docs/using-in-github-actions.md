# Using these images in GitHub Actions

The rules for running `sf-ci` (and its siblings) as a **container job**. Every rule
below is derived from a run on a GitHub-hosted runner, not from reasoning about
what ought to work — the evidence is in [Appendix A](#appendix-a--the-evidence).

---

## The four rules

### Rule 1 — from v3.1.0, pass no `options:` at all

```yaml
container: gforceinnovation/sf-ci:3.1.0
```

That is the whole thing. The image defaults to `runner` (UID 1001), which is the
GitHub-hosted runner's own UID, so the container can write everything the runner
owns.

**Why the UID matters at all.** The runner creates the job's *file-command
files* — the ones behind `$GITHUB_OUTPUT`, `$GITHUB_ENV` and
`$GITHUB_STEP_SUMMARY` — as `-rw-r--r-- 1001:1001`, and bind-mounts
`/github/home` owned by 1001. Under any other UID the first step that sets an
output dies with `Permission denied`.

**Version history, so nobody re-litigates it:**

| Version | Default user | What a caller had to write |
|---|---|---|
| `1.x`, `2.0.0` | root | nothing — privileged, and immune to all of this |
| `3.0.0` | `ci` (1000) | `options: --user 1001`, every single time |
| **`3.1.0`+** | **`runner` (1001)** | **nothing** |

`3.0.0` dropped `--user root`, not `--user`. `3.1.0` finishes the job.

> **Trap worth knowing.** Overriding `HOME` (e.g. `HOME=/home/ci`) makes `sf`
> work under UID 1000 and looks like a fix. It is not: the file commands stay
> broken, so the job runs happily until the first step that sets an output.

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
image: gforceinnovation/sf-ci:3.1.0     # ✅
image: gforceinnovation/sf-ci:latest    # ❌ silently changes under you
```

`latest` moves. The whole point of a controlled runtime is that
`git commit + image tag` reproduces a build; a floating tag gives that up.

The tag series is **not** what a casual reader expects, and pinning to an old
one interacts badly with Rule 1:

| Tag | Default user | Needs `--user 1001`? |
|-----|--------------|----------------------|
| `1.x`, `2.0.0` | root | no — and it would fail; 1001 is not registered |
| `3.0.0` | `ci` (1000) | **yes**, or every step output breaks |
| `3.1.0`+ | `runner` (1001) | no |

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
    container: gforceinnovation/sf-ci:3.1.0  # Rule 3; no options needed (Rule 1)
    defaults:
      run:
        shell: bash                           # Rule 4: sh has no -o pipefail
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
| `Permission denied` writing `/__w/_temp/_runner_file_commands/...` | Not running as 1001. On 3.0.0 add `--user 1001`; better, move to 3.1.0 | Rule 1 |
| `mkdir: cannot create directory '/github/home/.sf': Permission denied` | Same — `/github/home` is bind-mounted owned by the runner | Rule 1 |
| `set: Illegal option -o pipefail` | Step ran under `sh` | Rule 4 |
| Works locally, fails in Actions | Local `docker run` has no `/github/home` mount and no runner-owned file commands | Reproduce with the recipe below |

### Reproducing an Actions container job locally

```bash
docker volume create gh-home
docker run --rm --user 0 -v gh-home:/github/home \
  --entrypoint chown gforceinnovation/sf-ci:3.1.0 1001:0 /github/home

docker run --rm --user 1001 -v gh-home:/github/home -e HOME=/github/home \
  --entrypoint bash gforceinnovation/sf-ci:3.1.0 -c 'sf version && mkdir -p $HOME/.sf'
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

### What 3.1.0 changes

Same probe against `3.1.0`, which defaults to `runner` (1001). The runner mount
is simulated with a 1001-owned `/github/home` plus 0644 file-command files owned
by 1001:

| Variant | uid | file commands | `sf` | `$HOME` |
|---------|-----|---------------|------|---------|
| **no `options:` — the goal** | **1001** | **✅** | **✅** | **✅** |
| `--user 1001` | 1001 | ✅ | ✅ | ✅ |
| `--user 1000` | 1000 | ❌ | ❌ | ✅ |

The first and second rows are identical, which is the point: explicit
`--user 1001` still works, so existing callers keep working unchanged while new
ones write nothing.

Local matrix against the same image (no `/github/home` mount):

| `--user` | `sf` runs | Failure |
|----------|-----------|---------|
| none (1000) | ✅ | — |
| 1000 | ✅ | — |
| 1001 | ✅ | — |
| 1234 | ❌ | `uv_os_get_passwd ENOENT` |
| root | ✅ | — (but forbidden by Rule 2) |
