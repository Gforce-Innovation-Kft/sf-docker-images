# sf-devcontainer CLI cheatsheet

Quick reference — the expert guide lives in `sf-devcontainer/TOOLS.md` in the repo.
Run `sfhelp` for the Salesforce shortcuts.

## fzf — fuzzy finder

| Keys        | Action                                                    |
|-------------|-----------------------------------------------------------|
| `Ctrl-R`    | fuzzy-search shell history                                |
| `Ctrl-T`    | fuzzy-pick files/dirs into the current command line       |
| `Alt-C`     | fuzzy-cd into a subdirectory                              |
| `cmd **<TAB>` | fuzzy path completion (`vim **<TAB>`, `cd **<TAB>`)     |

Pipe anything into it: `git branch | fzf | xargs git switch`

## zoxide — smarter cd

- `z proj` — jump to the best-ranked dir matching "proj" (learns from every `cd`)
- `zi proj` — interactive pick via fzf
- `z -` — back to the previous dir

## eza — modern ls (pre-aliased)

`ls` → eza · `ll` long + git status · `la` all · `l` classify · `lt` tree (2 levels)

## bat — better cat

- `bat MyClass.cls` — syntax highlighting + line numbers
- `bat -p file` — plain output (pipe-friendly) · `bat -A file` — show invisibles

## fd — better find

- `fd Controller` — find by name, regex, .gitignore-aware
- `fd -e cls -e trigger` — by extension · `fd -H pattern` — include hidden

## rg — ripgrep

- `rg '@AuraEnabled'` — recursive grep, .gitignore-aware
- `rg -t js foo` — filter by type · `rg -g '*.cls' foo` — filter by glob
- `rg -l TODO | fzf --preview 'bat --color=always {}'`

## delta — git pager (already wired up)

- `git diff` / `git log -p` / `git show` render through delta automatically
- `n` / `N` — jump to next / previous file inside a large diff
- `git -c delta.side-by-side=true diff` — two-column view

## lazygit — git TUI

Run `lazygit` in any repo: `space` stage · `c` commit · `P` push · `p` pull ·
`b` branches · `s` stash · `d` discard · `?` all keybindings

## gh — GitHub CLI

`gh pr create -f` · `gh pr checkout 42` · `gh pr view --web` · `gh run watch`

## zsh niceties

- Ghost text after the cursor = autosuggestion from history — accept with `→`
- Command typed in red = not found; green = valid (syntax highlighting)
- `extract archive.tar.gz` — one command for any archive format
- `take dir` or `mkcd dir` — mkdir + cd in one step
- git plugin aliases: `gst` status · `gco` checkout · `gcb` new branch · `glola` graph log
- History: 50k entries, deduplicated, persists in the `/commandhistory` volume
- Prompt wizard: `p10k configure` · personal overrides: `~/.zshrc.local`
