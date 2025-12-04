# SF DevContainer

Full-featured development container for Salesforce development.

## Features

- **Node.js 20.x**: Latest LTS version
- **Java 17**: OpenJDK for Salesforce development
- **Salesforce CLI**: Latest version with plugins:
  - code-analyzer
  - sfdx-git-delta
  - sfdx-browserforce-plugin
- **Oh My Zsh**: Enhanced shell with Powerlevel10k theme
- **Development Tools**: vim, nano, git, build-essential
- **Utilities**: jq, xmlstarlet, tree, htop

## Usage

### With Docker

```bash
docker run -it -v $(pwd):/workspace gforceinnovation/sf-devcontainer:latest
```

### With VS Code Dev Containers

Create `.devcontainer/devcontainer.json`:

```json
{
  "name": "Salesforce Development",
  "image": "gforceinnovation/sf-devcontainer:latest",
  "customizations": {
    "vscode": {
      "extensions": [
        "salesforce.salesforcedx-vscode"
      ]
    }
  }
}
```

## Building Locally

```bash
docker build -t sf-devcontainer:local .
```
