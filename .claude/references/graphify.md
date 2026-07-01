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

## Not committed — a local build artifact

The whole **`graphify-out/` directory is git-ignored**, like `node_modules/` or `venv/`. It is a
generated artifact: `scripts/setup.sh` and the pre-commit hook rebuild it locally with
`graphify update .` (AST-only, no API cost). If it is missing, generate it with `graphify update .`;
`query`/`explain`/`path` read it from disk.

## Local setup

`scripts/setup.sh` installs the graphify Claude skill (`graphify install --platform claude`),
builds the graph (`graphify update .`), and activates the git hooks (`core.hooksPath` →
`.github/hooks`) if the `graphify` CLI is on PATH. Install it from its distribution if missing,
then run `graphify update .` to build `graphify-out/` locally.

The `.github/hooks/pre-commit` hook re-runs `graphify update .` on every commit so the local
`graphify-out/graph.json` never drifts from the code (nothing is staged — the dir is ignored). It
is **non-blocking**: if `graphify` is missing or errors, the commit still proceeds.
