# Design: devcontainer CLI tools — stale-image fix, zshrc bug, expert docs

**Date:** 2026-07-13 · **Status:** Approved (implemented same day on `feat/devcontainer-dx`)

## Problem

Testing the devcontainer, the baked-in CLI tools (fzf, zoxide, eza, delta,
lazygit, bat, fd, rg) appeared missing. Investigation showed the Dockerfile
install block is correct; the failure was upstream of it:

1. **Stale image**: `.devcontainer/devcontainer.json` pulled
   `gforceinnovation/sf-devcontainer:latest` = v1.7.0, cut from main *before*
   the tools commit (`b0f51dd`, only on `feat/devcontainer-dx`). All 8 tools
   verified missing in that image and verified working (as `vscode`) in the
   local feat-branch build.
2. **Dead OMZ plugins**: `.zshrc` listed `fd` and `ripgrep` in `plugins=(...)`;
   Oh My Zsh removed those completion-only plugins upstream, producing
   `[oh-my-zsh] plugin '...' not found` warnings on every shell start.

Additionally, the tools had no usage documentation.

## Decisions

- **Devcontainer builds from source** — `"build": {"context": "../sf-devcontainer",
  "dockerfile": "../sf-devcontainer/Dockerfile"}` replaces `"image":` in this
  repo's `.devcontainer/devcontainer.json`, so the devcontainer always matches
  the checked-out branch. Consumers of the published image keep using `"image":`
  (README example unchanged). Alternatives rejected: local tag override (manual,
  still stale-prone), releasing v1.8.0 immediately (publishes before review).
- **Drop `fd`/`ripgrep` from the OMZ plugins list** — the tools ship their own
  completions.
- **Docs in two layers** — `sf-devcontainer/TOOLS.md` (expert guide: per-tool
  workflows + zsh features) linked from the README, plus a compact
  `cheatsheet.md` baked into the image at `/usr/local/share/sf-devcontainer/`
  rendered by a new `devhelp` zsh function (mirrors the `sfhelp` pattern).
  Alternative rejected: README-only section (README gets long, not
  discoverable in-shell).
- **`.dockerignore`** needs `!cheatsheet.md` after `*.md` or the COPY fails.

## Components

| Piece | Change |
|-------|--------|
| `.devcontainer/devcontainer.json` | build from `../sf-devcontainer` |
| `sf-devcontainer/.zshrc` | remove dead plugins; add `devhelp`; banner mentions it |
| `sf-devcontainer/cheatsheet.md` | new; compact quick-reference, baked into image |
| `sf-devcontainer/Dockerfile` | `COPY cheatsheet.md /usr/local/share/sf-devcontainer/` |
| `sf-devcontainer/.dockerignore` | `!cheatsheet.md` negation |
| `sf-devcontainer/TOOLS.md` | new; expert guide (tools, combos, zsh features) |
| `sf-devcontainer/README.md` | link TOOLS.md + mention `devhelp` |
| `tests/test_sf_devcontainer.py` | cheatsheet exists; `zsh -ic` emits no `[oh-my-zsh] plugin` warnings; `devhelp` token in .zshrc |

## Testing

pytest-testinfra suite (30 tests) green; manual smoke:
`docker run --rm -t sf-devcontainer:test zsh -ic 'devhelp'` renders the
cheatsheet with no startup warnings.
