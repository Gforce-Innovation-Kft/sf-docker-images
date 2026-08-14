# GForce AI integration — how gforce-ai governs this repo

How the `Gforce-Innovation-Kft/gforce-ai` control plane delivers skills, agents, and
standards into this repository, and what wins when rules conflict.

**This file explains the wiring; it never restates a rule.** The rules live in the skills
and standards it points to — a restated rule is a rule that will drift.

## Precedence: industry → fleet → shared → local, last wins

| Layer | What it is here | Source of truth |
|---|---|---|
| **industry** | `platform-docs-get` (Salesforce docs lookup) | `forcedotcom/sf-skills`, ratified pin in `gforce-ai/upstream/catalog.json` |
| **fleet** | Standards every GForce repo obeys | `gforce-ai/standards/` (`doc-standard`, `skill-scope`, `upstream-policy`) |
| **shared** | `gforce-github-actions` skill + `gha-workflow-author` agent (placed by the `.github/workflows/` marker); `docker-expert`, `multi-stage-dockerfile`, `devcontainer-setup` (placed by `Dockerfile*`) | `gforce-ai` and the vendored upstream repos, hash-pinned in `skills-lock.json` |
| **local** | This repo's own rules — E2E gate tiers, image-list duplication, release/publish and cosign constraints | `.claude/references/local-standards.md` — shared skills read it **last** and it **wins** on conflict |

An industry skill is the floor, never the ceiling: any GForce layer beats it. Local skills
(`building-a-docker-image`, `releasing`, `testing-images`, `working-in-the-devcontainer`)
sit outside the precedence chain — they are repo-owned knowledge, not overrides.

## Delivery

- **Skills** arrive by content hash in `skills-lock.json` — never vendor or edit a copy.
  Every machine and CI run resolves the identical bytes; a mismatched hash is a data
  point, not an auto-upgrade.
- **Industry skills** (`forcedotcom/sf-skills`) additionally go through central
  ratification: `gforce-ai` reviews each upstream change once
  (`upstream-ratification.yml` PR — the fleet's prompt-injection boundary) and advances
  the pin in `upstream/catalog.json`. A skill absent from that catalog is not approved
  here. Policy: `gforce-ai/standards/upstream-policy.md`.
- **Agents** are file-copied into `.claude/agents/` — a known gap (no hash, no drift
  check). Treat the copy as read-only; changes belong in `gforce-ai/agents/` first.

## What happens when Claude opens this repo

1. `CLAUDE.md` loads — purpose, hard rules, pointer here.
2. `.claude/skills/` are discoverable; each fires on its own trigger contract, not on
   install. `.claude/agents/gha-workflow-author.md` becomes available.
3. Editing anything under `.github/workflows/` routes through `gha-workflow-author`,
   which reads the shared skill first and `local-standards.md` last (local wins).

## Updating

**Order is fixed: ratify first, bump second.**

1. For industry skills, an update is only consumable after `gforce-ai` merged its
   ratification PR.
2. Then, **on a dedicated branch**, run `npx skills check` / `npx skills update` and
   review the diff as a real content change — these commands rewrite `SKILL.md` files and
   `skills-lock.json` in place; they are *not* read-only (trap documented in
   `gforce-ai/standards/skill-scope.md`).
3. Commit the lockfile + skill changes via PR.

Urgent fleet-wide fixes arrive as a dispatch *trigger* from `gforce-ai`, never as a push
of content into this repo.

## Conflicts

A shared or industry rule that doesn't fit this repo is never resolved by editing the
skill — add the exception to `.claude/references/local-standards.md` (the filename is
load-bearing; shared skills look for exactly this path). It is read last, wins, and the
exception stays reviewable in one place.
