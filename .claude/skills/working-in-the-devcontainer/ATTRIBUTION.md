# Attribution

This skill is **adapted** (not a verbatim copy) from:

- **claude-code-docker-skill** — https://github.com/wrsmith108/claude-code-docker-skill
  (template skill that routes dev/build/test commands into a running dev container).
- Sibling reference: **docker-claude-skill** —
  https://github.com/wrsmith108/docker-claude-skill (auto-discovers containers).

The `docker ps --filter ancestor=... | docker exec -w /workspace` routing pattern is taken
from that source and specialised for this repo's `sf-devcontainer` image (Salesforce CLI,
Node 24, Java 17). Credit to **@wrsmith108**.

Please consult the upstream repository for its license terms before redistributing. This
adaptation is provided under this repository's MIT `LICENSE`; the routing concept and
approach originate upstream and are credited here.
