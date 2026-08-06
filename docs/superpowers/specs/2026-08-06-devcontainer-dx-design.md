# Design: devcontainer DX — host-matching shell and inherited org auth

**Date:** 2026-08-06 · **Status:** Approved, not yet implemented
**Scope:** two repos — `sf-docker-images` (the image) and `sf-develop-demo` (the consumer)

## Problem

Three things make the Salesforce devcontainer worse than it should be.

**The container shell is the setup the developer deliberately abandoned.** On 2026-08-02 the
host migrated off Oh My Zsh + Powerlevel10k to Starship with no framework and a single cached
`compinit`, cutting shell startup from 1370 ms to 61 ms. `sf-devcontainer` still ships OMZ +
p10k with 13 plugins, an 89 KB `.p10k.zsh`, and the instant-prompt cache hack. Entering the
container means dropping into a slower shell with a different prompt and different keybindings.

**`sf-develop-demo/.devcontainer/` contains dead code that misinforms.** Its `devcontainer.json`
sets `"image": "gforceinnovation/sf-devcontainer:latest"`, so the sibling `Dockerfile` is never
built — yet that Dockerfile installs **Node 20** where the real image has 24, plus its own OMZ,
p10k, `.zshrc` and `.p10k.zsh`. Anyone reading it forms false beliefs about their environment.
The `git` and `github-cli` devcontainer features are redundant; the image already ships both.

**Opening the devcontainer does not give you a usable org.** Credentials live in the host's
`~/.sf`, which is not shared with the container, so every rebuild starts unauthenticated.

## Decisions

| Question | Decision |
|---|---|
| Credential source | **Bind-mount the host `~/.sf`** into the container |
| Container shell | **Match the host** — Starship, no framework |
| Sequencing | Shell folds into the pending **v3.0.0**; the `sf-develop-demo` config lands immediately |

Rejected, with reasons: a gitignored `SFDX_AUTH_URL` file (long-lived refresh token in
plaintext, needs rotation); host env passthrough (breaks silently when the export is forgotten);
scratch-org-on-create (still needs Dev Hub auth, and spends already-tight quota).

## Part A — sf-devcontainer shell (ships in v3.0.0)

### Changes

| Remove | Add |
|---|---|
| Oh My Zsh install | `starship` (single pinned binary) |
| Powerlevel10k clone + `sf-devcontainer/.p10k.zsh` (89 KB) | `sf-devcontainer/starship.toml` |
| 3 git-cloned zsh plugins | `zsh-autosuggestions`, `zsh-syntax-highlighting` from apt |
| 13-entry OMZ `plugins=(...)` | direct `source` of each plugin, syntax-highlighting **last** |
| p10k instant-prompt block | — |

`sf-devcontainer/.zshrc` is rewritten to mirror the host's structure: all `fpath` additions
before a **single cached `compinit`**, then plugin sourcing, then `starship init`.

Everything that earns its place is kept verbatim: the SF aliases and `sfhelp`, `devhelp`,
`sfdelta`, the 50 000-entry deduplicated history on the `/commandhistory` volume, fzf
keybindings, zoxide, `sf autocomplete`, and the `~/.zshrc.local` per-developer overlay.

### Target-org prompt module

`starship.toml` gains a custom module showing the repo's current target org, read directly from
`.sf/config.json` with `jq`:

```toml
[custom.sf_org]
command = "jq -r '.\"target-org\" // empty' .sf/config.json 2>/dev/null"
when = "test -f .sf/config.json"
symbol = "☁ "
```

**It must not call `sf config get`** — that pays Node startup (~500 ms) on every prompt, which
would reintroduce exactly the latency this change removes.

### Package availability — checked, not assumed

Verified against `ubuntu:24.04` on 2026-08-06 (`apt-cache policy`):

| Package | Result | Consequence |
|---|---|---|
| `zsh-autosuggestions` | **0.7.0-1** | install from apt |
| `zsh-syntax-highlighting` | **0.7.1-2** | install from apt |
| `zsh-completions` | **not packaged** | **drop it** — do not reintroduce a git clone; the two sourced plugins plus `compinit` cover the need |
| `starship` | **not packaged** | install the release binary, **pinned to an explicit version** and fetched over HTTPS, not `curl \| sh` unpinned |

Sourced paths for the apt plugins are
`/usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh` and
`/usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh`; confirm at build time and fail
the build if either is missing rather than silently producing a shell with no plugins.

### Collateral

- `tests/test_sf_devcontainer.py`: assert `starship` present; assert `~/.oh-my-zsh` and
  `~/.p10k.zsh` **absent** (the same shape as sf-ci's "forbidden tool" assertions).
- `sf-devcontainer/README.md`, `TOOLS.md`, `cheatsheet.md`: every OMZ/p10k reference.
- `CHANGELOG.md` `[Unreleased]`, alongside the non-root entry.
- Size is roughly neutral — the Starship binary (~10 MB) offsets the removed framework — but
  record the before/after so the claim is not guessed.

## Part B — sf-develop-demo devcontainer (lands immediately)

**Delete** `.devcontainer/Dockerfile`, `.devcontainer/.zshrc`, `.devcontainer/.p10k.zsh`.

**`devcontainer.json`:**

```jsonc
"mounts": [
  "source=${localEnv:HOME}/.sf,target=/home/vscode/.sf,type=bind",
  "source=${localEnv:HOME}/.sfdx,target=/home/vscode/.sfdx,type=bind"
],
"postCreateCommand": "npm install && .devcontainer/post-create.sh"
```

Remove the `git` and `github-cli` features.

**New `.devcontainer/post-create.sh`** — resolves and reports the org, and fails loudly:

1. Confirm `~/.sf` is mounted and readable; if not, say the mount is missing and stop.
2. Resolve `target-org` from the repo's local `.sf/config.json`.
3. If unset (fresh clone — `.sf/` is gitignored), set it from a committed default alias carried
   in `devcontainer.json` as `containerEnv.SF_DEFAULT_ORG_ALIAS`. **Its value is `github1`**, the
   alias this repo's local config already points at; committing it in `devcontainer.json` is what
   makes the default survive a fresh clone, since `.sf/` never reaches git.
4. Run `sf org display --target-org "$alias"`. On failure, print the **exact** login command and
   exit non-zero.

The script must never leave the developer in a shell that silently cannot deploy.

## What this explicitly does not do

**A bind mount shares credentials; it cannot create them.** At design time the host has **no
authorized orgs** — `~/.sf` holds only `config.json` and caches, `sf org list` is empty, and the
repo's `target-org: github1` is a dangling pointer. A one-time `sf org login web` on the host is
a prerequisite. After that, every container start inherits it, and logins performed inside the
container persist back to the host.

Two accepted trade-offs:

- **The container can use every org you have authorized, including production.** That is the
  cost of the convenience; anything running inside inherits full access.
- **The mount relies on Docker Desktop's UID remapping.** On a Linux host, container `vscode`
  (UID 1000) against the host user's UID would mismatch and need a different approach.

## Verification — on `sf-develop-demo`

Both parts are verified in the real consumer repo, not in the abstract.

**Prerequisite (one time, on the host):** `sf org login web` — nothing below can pass without a
credential to inherit.

**Testing Part A before any release.** The published image will not carry the new shell until
v3.0.0. To verify first, build locally and point the consumer at it temporarily:

```bash
docker build -t sf-devcontainer:local ./sf-devcontainer      # in sf-docker-images
# in sf-develop-demo/.devcontainer/devcontainer.json, temporarily:
#   "image": "sf-devcontainer:local"
```

Revert that line before committing.

**Then, with the devcontainer reopened in `sf-develop-demo`:**

| # | Check | Pass condition |
|---|---|---|
| 1 | `sf org list` | lists the host's orgs — the mount works |
| 2 | `sf config get target-org` | resolves to the repo's org |
| 3 | `sf org display` | succeeds without any login step |
| 4 | prompt | shows the target org via the Starship module |
| 5 | `command -v starship`, `ls ~/.oh-my-zsh` | starship present, OMZ **absent** |
| 6 | `time zsh -i -c exit` | materially faster than the OMZ baseline; record both numbers |
| 7 | `sf org login web` **inside** the container, then `sf org list` on the **host** | the new org appears — the mount is read-write and shared |
| 8 | `sf project deploy start --dry-run` | reaches the org, proving auth is genuinely usable |

**Negative test — the failure mode that matters most:** temporarily point `target-org` at an
unauthorized alias and re-run `post-create.sh`. It must exit non-zero and print the exact login
command, not fail silently or drop into a working-looking shell.

**Regression:** `pytest tests/test_sf_devcontainer.py -v` in `sf-docker-images`.

## Out of scope

- `sf-ci` and `sf-bulk` shells — they are non-interactive CI images and must stay minimal.
- Linux-host UID mapping for the bind mount; documented as a limitation, not solved.
- Any change to how credentials are obtained (JWT, auth URL) — deliberately rejected above.
