# TOOLS.md — expert guide to the sf-devcontainer shell

Everything here is pre-installed and pre-wired in the image — no setup needed.
Inside the container, run `devhelp` for the condensed cheatsheet and `sfhelp` for
the Salesforce shortcuts.

Contents: [fzf](#fzf) · [zoxide](#zoxide) · [eza](#eza) · [bat](#bat) ·
[fd + ripgrep](#fd--ripgrep) · [delta](#delta) · [lazygit](#lazygit) · [gh](#gh) ·
[Zsh features](#zsh-features) · [Salesforce shortcuts](#salesforce-shortcuts)

## fzf

Fuzzy finder — the glue between every other tool. The image sources `fzf --zsh`,
so three keybindings work out of the box:

| Keys     | What it does |
|----------|--------------|
| `Ctrl-R` | Fuzzy-search your entire shell history. Type any fragment, in any order (`dep sta` matches `sf project deploy start`). Enter puts it on the command line. |
| `Ctrl-T` | Fuzzy-pick one or more files/dirs and insert the path(s) at the cursor. Multi-select with `Tab`. |
| `Alt-C`  | Fuzzy-pick a subdirectory and `cd` into it. |

**`**<TAB>` completion** — type `**` and hit Tab after almost any command to
fuzzy-complete paths, hosts, or PIDs:

```bash
vim **<TAB>          # fuzzy-pick the file to edit
cd force-app/**<TAB> # fuzzy-pick a subdirectory
kill -9 **<TAB>      # fuzzy-pick the process
ssh **<TAB>          # fuzzy-pick a host from ~/.ssh/config
```

**Pipe anything into it** — fzf turns any list into an interactive picker:

```bash
git branch | fzf | xargs git switch          # switch branch interactively
sf org list --json | jq -r '.result.nonScratchOrgs[].alias' | fzf | xargs sf org open -o
```

**Preview windows** — combine with bat for a file browser:

```bash
fzf --preview 'bat --color=always --style=numbers {}'
```

Inside fzf: `Ctrl-J/K` or arrows to move, `Tab` multi-select, `Esc` cancel.

## zoxide

A `cd` that learns. Every directory you visit is ranked by "frecency"
(frequency + recency); afterwards a fragment is enough:

```bash
z force        # jumps to .../force-app (best match for "force")
z doc images   # multiple fragments: matches .../sf-docker-images/docs
zi force       # interactive: all matches in fzf, pick one
z -            # back to the previous directory
```

`cd` keeps working normally (zoxide is sourced directly in `.zshrc` and adds
`z`/`zi` alongside it). The ranking database is per-container unless you mount
a volume over `~/.local/share/zoxide`.

## eza

Modern `ls` with git awareness. The image aliases:

| Alias | Expands to | Use for |
|-------|-----------|---------|
| `ls`  | `eza` | day-to-day listing |
| `ll`  | `eza -alF --git --group-directories-first` | long list **with a git status column** |
| `la`  | `eza -a` | include dotfiles |
| `l`   | `eza -F` | compact with type suffixes |
| `lt`  | `eza --tree --level=2` | quick tree view |

Worth knowing beyond the aliases:

```bash
eza --tree --level=3 --git-ignore   # tree view that respects .gitignore
eza -l --sort=modified              # newest last (great before a commit)
eza -l --total-size src/            # recursive directory sizes
```

`\ls` or `command ls` bypasses the alias when you need plain POSIX output.

## bat

`cat` with syntax highlighting, line numbers, and git-modification markers.
Ubuntu names the binary `batcat`; the image symlinks it so `bat` just works.

```bash
bat force-app/main/default/classes/MyService.cls   # highlighted, numbered
bat -p script.sh          # plain: no frame/numbers — safe to pipe
bat -A weird-file         # show tabs, CRLF, non-printables (encoding bugs)
bat -r 40:80 Big.cls      # only lines 40–80
curl -s https://api.example.com | bat -l json      # highlight piped content
```

bat auto-detects when output is piped and behaves like plain `cat`, so it's
safe in scripts too.

## fd + ripgrep

The find/grep pair, both **`.gitignore`-aware by default** (they skip
`node_modules`, `.sfdx`, build output — a big deal in sfdx projects).

**fd** — find files:

```bash
fd Controller                 # name contains "Controller" (smart-case regex)
fd -e cls -e trigger          # all Apex classes and triggers
fd -e xml meta                # *meta.xml files
fd -H '^\.env'                # -H includes hidden files
fd -e cls -x wc -l            # -x runs a command per result
```

Ubuntu names it `fdfind`; the image symlinks `fd`.

**ripgrep (rg)** — search file contents:

```bash
rg '@AuraEnabled'             # recursive, fast, respects .gitignore
rg -t js 'import.*lwc'        # -t filters by type (rg --type-list)
rg -g '*.cls' 'SeeAllData'    # -g filters by glob
rg -i -C3 'nullpointer'       # case-insensitive with 3 context lines
rg -l 'TODO'                  # filenames only
rg --files-without-match 'IsTest' -g '*Test.cls'   # test classes w/o @IsTest
```

**Combos** — where the tools multiply each other:

```bash
rg -l 'SOQL' | fzf --preview 'rg --color=always SOQL {}' | xargs code
fd -e cls | fzf --preview 'bat --color=always {}'
```

## delta

Already configured system-wide as git's pager — `git diff`, `git log -p`,
`git show`, and `git stash show -p` all render through it with syntax
highlighting and word-level diffs. Nothing to enable.

- **`n` / `N`** — jump to the next/previous file inside a long diff
  (`delta.navigate` is pre-set; `q` quits as usual).
- **Side-by-side** on demand:

  ```bash
  git -c delta.side-by-side=true diff
  ```

  Make it permanent for yourself with `git config --global delta.side-by-side true`.
- **Merge conflicts** use `zdiff3` style (pre-configured): conflict blocks show
  the *base* version between `|||||||` and `=======`, so you see what both
  sides changed — far easier to resolve than the default two-way markers.
- delta only engages on a TTY, so scripts and CI parsing `git diff` output are
  unaffected.

## lazygit

Full git TUI — stage hunks, rewrite history, and manage branches without
memorizing plumbing. Run `lazygit` inside any repo.

Core keys (press `?` for the full map, arrows/`h`/`l` move between panels):

| Key | Action |
|-----|--------|
| `space` | stage/unstage file (or selected lines in the staging panel) |
| `Enter` on a file | open it hunk-by-hunk — stage individual lines |
| `c` | commit |
| `A` | amend last commit |
| `P` / `p` | push / pull |
| `b` (branches panel) | branch actions; `space` checks out |
| `s` | stash; `g` opens the reset menu |
| `d` | discard changes (asks first) |
| `z` | undo (reflog-based — the panic button) |

The killer feature for tidy PRs: line-level staging (`Enter` → select lines →
`space`) beats `git add -p` in speed once you've used it twice.

## gh

Authenticated GitHub work from the terminal (`gh auth login` once per container,
or mount your host config):

```bash
gh pr create -f               # PR from current branch, title/body from commits
gh pr checkout 42             # review someone's PR locally
gh pr view --web              # open the PR in the browser
gh run watch                  # live-tail the CI run for this branch
gh run rerun --failed         # re-run only failed jobs
gh api repos/{owner}/{repo}/releases/latest -q .tag_name
```

## Zsh features

### Autosuggestions and syntax highlighting

- **zsh-autosuggestions** (apt package, sourced directly — no framework) —
  ghost text after the cursor suggests the rest of the command from your
  history. Accept the whole thing with `→` (or `End`), accept one word with
  `Ctrl-→` (`forward-word`).
- **zsh-syntax-highlighting** (apt package) — the command line is linted as
  you type: red command = typo/not installed, green = resolves; quotes and
  paths get their own colors. If it's red, don't bother pressing Enter. It's
  sourced last of the two plugins — sourcing it earlier silently breaks
  highlighting.
- **SF CLI autocomplete** is baked in too — `sf <TAB>` completes topics,
  commands, and flags, via zsh's own single, cached `compinit`.

### History

50,000 entries, duplicates collapsed, written incrementally (nothing lost on a
crashed shell). With the reference devcontainer.json, history lives in the
`sf-devcontainer-history` volume mounted at `/commandhistory` — it **survives
container rebuilds**. `Ctrl-R` (fzf) searches all of it.

### Prompt (Starship)

Starship renders the current directory (truncated to the repo root), git
branch and status, and a cyan `☁` badge showing the project's Salesforce
target org — read straight from `.sf/config.json` with `jq`, never by calling
`sf` (that would add ~500 ms of Node startup to every prompt). The prompt
character turns red after a command exits non-zero. Configuration is baked
into `starship.toml`; there's no interactive configuration wizard — if you
relied on Oh My Zsh's alias packs (`gst`, `gco`, `extract`,
`colored-man-pages`, and friends) or its prompt theme's setup wizard, recreate
what you need in `~/.zshrc.local`. `mkcd new-dir` (mkdir + cd) ships in the
image and still works the same as always.

### Personalization

- `~/.zshrc.local` — sourced last if present. Drop personal aliases, env vars,
  or theme tweaks there; survives image updates, no rebuild needed.
- VS Code **dotfiles**: set `"dotfiles.repository": "you/dotfiles"` in your VS
  Code settings and every dev container gets your dotfiles automatically.

## Salesforce shortcuts

Run `sfhelp` inside the container. Highlights: `sfl` (org list), `sfo` (org
open), `sfd` (deploy), `sfr` (retrieve), `sft` (run tests with coverage), and
`sfdelta [ref]` — build a delta deployment package from git history via
sfdx-git-delta (defaults to `origin/main..HEAD`).
