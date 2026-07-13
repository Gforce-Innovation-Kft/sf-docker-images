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

`cd` keeps working normally (the Oh My Zsh plugin adds `z`/`zi` alongside it).
The ranking database is per-container unless you mount a volume over
`~/.local/share/zoxide`.

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

### Autosuggestions, syntax highlighting, completions

- **zsh-autosuggestions** — ghost text after the cursor suggests the rest of
  the command from your history. Accept the whole thing with `→` (or `End`),
  accept one word with `Ctrl-→` (`forward-word`).
- **zsh-syntax-highlighting** — the command line is linted as you type: red
  command = typo/not installed, green = resolves; quotes and paths get their
  own colors. If it's red, don't bother pressing Enter.
- **zsh-completions** — extra completion definitions for hundreds of tools on
  top of zsh's own. `Tab` through everything; menu-select is enabled by
  Oh My Zsh.
- **SF CLI autocomplete** is baked in too — `sf <TAB>` completes topics,
  commands, and flags.

### History

50,000 entries, duplicates collapsed, written incrementally (nothing lost on a
crashed shell). With the reference devcontainer.json, history lives in the
`sf-devcontainer-history` volume mounted at `/commandhistory` — it **survives
container rebuilds**. `Ctrl-R` (fzf) searches all of it.

### Oh My Zsh plugin gems

The image enables these plugins — the highest-value bits:

- **git** — the famous alias pack: `gst` (status), `gco` (checkout), `gcb`
  (create branch), `gp` (push), `gl` (pull), `gd` (diff), `ga`/`gaa` (add),
  `gcmsg "..."` (commit -m), `glola` (decorated graph log), `grbi` (rebase -i),
  `gwip` (quick WIP commit) / `gunwip` (undo it). Run `alias | grep '^g'` to
  see them all.
- **extract** — `extract anything.tar.gz|zip|7z|rar|...` — one verb for every
  archive format.
- **copyfile / copypath** — `copyfile notes.md` copies the file's contents,
  `copypath` copies the cwd (or a given path) to the clipboard.
- **colored-man-pages** — man pages with section headers and highlights.
- **command-not-found** — typo a command and Ubuntu tells you which package
  provides it.
- **docker / docker-compose / node / npm / gh / vscode** — completions and
  small alias packs for each (e.g. `dps` for `docker ps` in newer OMZ
  versions; check `alias | grep <tool>`).
- **take** (built into OMZ) — `take new-dir` = mkdir + cd. The image also
  ships a `mkcd` function that does the same.

### Prompt (Powerlevel10k)

The prompt shows git state (branch, dirty/staged counts), exit status, and
command duration. Reconfigure it interactively with `p10k configure`; your
answers land in `~/.p10k.zsh`.

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
