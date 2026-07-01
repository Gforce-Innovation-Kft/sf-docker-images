# graphify — knowledge graph for token-efficient navigation

This repo ships a [graphify](https://github.com/) knowledge graph in `graphify-out/`. Use it to
answer codebase questions from a **scoped subgraph** instead of grepping or reading whole files.
That is the point: fewer tokens per question, faster orientation.

## When to use it (before reaching for grep / full-file reads)

- **A codebase question** ("what builds the images?", "where are env vars set?", "how do tests
  find the image?") → `graphify query "<question>"` returns a small relevant subgraph.
- **One concept and its neighbors** → `graphify explain "<node>"`.
- **How two things relate** → `graphify path "<A>" "<B>"`.
- **Broad architecture pass** → read `graphify-out/GRAPH_REPORT.md` (only when you truly need the
  whole picture; it is larger than a scoped query).

Still read raw files when you are **modifying or debugging specific code**, or when the graph
lacks the detail you need.

## Keeping it current

- **After changing code**, run `graphify update .` — AST-only, **no LLM / no API cost**. It
  re-extracts and rewrites `graph.json` + `GRAPH_REPORT.md`.
- The graph currently covers the repo's Dockerfiles, tests, workflow, scripts, and docs
  (~438 nodes / ~411 edges / 32 communities at last build).

## What is committed vs ignored

| Path | Tracked? | Why |
|------|----------|-----|
| `graphify-out/graph.json` | ✅ committed | the graph itself — powers `query`/`explain`/`path` |
| `graphify-out/GRAPH_REPORT.md` | ✅ committed | human/broad architecture read |
| `graphify-out/manifest.json`, `.graphify_labels.json`, `.graphify_root` | ✅ committed | graph metadata |
| `graphify-out/cache/` | ⛔ git-ignored | machine-local AST rebuild cache |
| `graphify-out/graph.html` | ⛔ git-ignored | regenerable visualization (`graphify update .`) |

## Local setup

`scripts/setup.sh` installs the graphify Claude skill (`graphify install --platform claude`) and
builds the graph (`graphify update .`) if the `graphify` CLI is on PATH. Install it from its
distribution if missing; the committed `graph.json` still works for `query`/`explain`/`path`
without a local rebuild.
