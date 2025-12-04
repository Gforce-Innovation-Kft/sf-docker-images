# Testing Docker Images with pytest-testinfra

This directory contains tests for validating the Docker images using [pytest-testinfra](https://testinfra.readthedocs.io/).

## Setup

### Prerequisites
- Python 3.8 or higher
- Docker installed and running

### Installation

1. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

2. **Install test dependencies:**
   ```bash
   pip install -r tests/requirements.txt
   ```

## Running Tests Locally

The tests automatically build the Docker images before running, so you don't need to build them manually.

### Test sf-devcontainer

```bash
pytest tests/test_sf_devcontainer.py -v
```

### Test sf-ci

```bash
pytest tests/test_sf_ci.py -v
```

### Run All Tests

```bash
pytest tests/ -v
```

The first time you run the tests, it will build the images. Subsequent runs will be faster unless you change the Dockerfiles.

## Test Structure

### test_sf_devcontainer.py
Tests for the full-featured development container:
- ✅ Ubuntu 22.04 base
- ✅ Node.js 20.x & npm
- ✅ Java 17 (OpenJDK)
- ✅ Salesforce CLI with plugins (code-analyzer, sfdx-git-delta, sfdx-browserforce-plugin)
- ✅ Oh My Zsh with Powerlevel10k theme
- ✅ Zsh plugins (autosuggestions, syntax-highlighting, completions)
- ✅ Development tools (git, vim, nano, jq, xmlstarlet)
- ✅ User configuration (vscode user with sudo)
- ✅ Environment variables

### test_sf_ci.py
Tests for the lightweight CI/CD container:
- ✅ Ubuntu 22.04 base
- ✅ Node.js 20.x & npm
- ✅ Java 17 (OpenJDK)
- ✅ Salesforce CLI with sfdx-git-delta plugin
- ✅ CI utilities (git, jq, xmlstarlet)
- ✅ User configuration (ci user, non-root)
- ✅ CI environment variables
- ✅ Minimal footprint (no interactive tools)

## Test Options

### Verbose Output
```bash
pytest tests/ -v
```

### Show Print Statements
```bash
pytest tests/ -s
```

### Run Specific Test
```bash
pytest tests/test_sf_devcontainer.py::test_nodejs_installed -v
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Show Test Coverage
```bash
pytest tests/ --cov
```

## CI Integration

These tests can be integrated into GitHub Actions or other CI systems:

```yaml
- name: Install pytest and pytest-testinfra
  run: pip install -r tests/requirements.txt

- name: Run tests
  run: pytest tests/ -v
```

## Writing New Tests

When adding new tools or configurations to the Docker images, add corresponding tests:

```python
def test_new_tool_installed(host):
    """Test that new tool is installed"""
    result = host.run("new-tool --version")
    assert result.rc == 0
    assert "expected version" in result.stdout
```

## Troubleshooting

### Tests fail with "connection refused"
Make sure Docker is running and you can execute `docker ps`.

### Tests fail with "image not found"
Build the images with the correct tags before running tests.

### Permission errors
Make sure your user has permission to run Docker commands. On Linux, you may need to add your user to the `docker` group.

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-testinfra documentation](https://testinfra.readthedocs.io/)
- [testinfra API reference](https://testinfra.readthedocs.io/en/latest/modules.html)
