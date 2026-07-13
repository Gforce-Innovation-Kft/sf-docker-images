# Container recipes for Salesforce teams

Copy-paste recipes for using the [sf-docker-images](../README.md) family
(`sf-devcontainer`, `sf-ci`, `sf-bulk`) with Docker Compose from any sfdx project.

## Setup

Copy into the root of your sfdx project:

- [`docker-compose.yml`](docker-compose.yml)
- [`.env.example`](.env.example) → rename to `.env`, fill in, **add `.env` to `.gitignore`**
- optionally [`scripts/`](scripts/)

## Recipes

### 1. Zero-install dev shell

New teammate, fresh laptop, nothing installed but Docker:

```bash
docker compose run --rm dev
```

Full zsh environment with SF CLI, Node, Java, git — your repo mounted at
`/workspace`, org auth and shell history persisted in named volumes across runs.
(For the full IDE experience use VS Code Dev Containers instead — see
[sf-devcontainer](../sf-devcontainer/README.md).)

### 2. Authorize an org from a container

Safer than juggling tokens on shared machines, and identical to how CI authenticates:

```bash
# .env contains SF_AUTH_URL (see .env.example)
docker compose run --rm dev bash scripts/auth-org.sh
```

The auth URL comes from `sf org display --verbose --json | jq -r '.result.sfdxAuthUrl'`
on any machine already logged in. In pipelines, the same script reads the value from a
CI secret — nothing to change.

### 3. Test pipeline scripts in the real CI image (Windows-parity)

Commands behave differently on Windows (PowerShell/Git-Bash) than in your Linux CI.
Run the script in the **exact image your pipeline uses** before pushing:

```bash
docker compose run --rm ci bash scripts/run-apex-tests.sh
docker compose run --rm ci bash -c 'sf sgd source delta --from origin/main --to HEAD --output-dir delta'
```

If it works here, it works in the `container: gforceinnovation/sf-ci` job.

### 4. Bulk data operations (no Java, small pull)

```bash
docker compose run --rm bulk bash scripts/auth-org.sh
docker compose run --rm bulk sf data export bulk --query "SELECT Id, Name FROM Account" \
  --output-file accounts.csv --wait 10 --target-org target-org
```

## Secrets — the rules

- `.env` is for **local use only** and must be git-ignored; CI uses pipeline secrets.
- Never bake credentials into an image (`ENV`/`ARG`/`COPY`) — they persist in layers.
- Auth URLs grant full API access to the org: treat them like passwords, rotate on leak.
- `docker compose run` passes `.env` values only into that container's process — they
  don't land in your shell history or host environment.
