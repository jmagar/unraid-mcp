# Publishing Guide for unraid-mcp

This guide covers how to publish `unraid-mcp` to PyPI so it can be installed via `uvx` or `pip` from anywhere.

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - [Test PyPI](https://test.pypi.org/account/register/) (for testing)
   - [PyPI](https://pypi.org/account/register/) (for production)

2. **API Tokens**: Generate API tokens for automated publishing:
   - Test PyPI: https://test.pypi.org/manage/account/token/
   - PyPI: https://pypi.org/manage/account/token/

3. **Save Tokens Securely**:
   ```bash
   # Add to ~/.pypirc (never commit this file!)
   cat > ~/.pypirc << 'EOF'
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   username = __token__
   password = pypi-YOUR-API-TOKEN-HERE

   [testpypi]
   username = __token__
   password = pypi-YOUR-TEST-API-TOKEN-HERE
   repository = https://test.pypi.org/legacy/
   EOF

   chmod 600 ~/.pypirc  # Secure the file
   ```

## Version Management

Before publishing, update the version in `pyproject.toml`:

```toml
[project]
version = "0.2.1"  # Follow semantic versioning: MAJOR.MINOR.PATCH
```

**Semantic Versioning Guide:**
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.2.0): New features (backward compatible)
- **PATCH** (0.2.1): Bug fixes (backward compatible)

## Publishing Workflow

### 1. Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf dist/ build/ *.egg-info/
```

### 2. Run Quality Checks

```bash
# Format code
uv run black unraid_mcp/

# Lint code
uv run ruff check unraid_mcp/

# Type check
uv run ty check unraid_mcp/

# Run tests
uv run pytest

# Check coverage
uv run pytest --cov=unraid_mcp --cov-report=html
```

### 3. Build the Package

```bash
# Build both wheel and source distribution
uv run python -m build
```

This creates:
- `dist/unraid_mcp-VERSION-py3-none-any.whl` (wheel)
- `dist/unraid_mcp-VERSION.tar.gz` (source distribution)

### 4. Validate the Package

```bash
# Check that the package meets PyPI requirements
uv run twine check dist/*
```

Expected output: `PASSED` for both files.

### 5. Test on Test PyPI (IMPORTANT!)

Always test on Test PyPI first:

```bash
# Upload to Test PyPI
uv run twine upload --repository testpypi dist/*

# Test installation from Test PyPI
uvx --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ unraid-mcp-server

# Or with pip in a test environment
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ unraid-mcp
```

**Note**: `--extra-index-url https://pypi.org/simple/` is needed because dependencies come from production PyPI.

### 6. Publish to PyPI (Production)

Once testing passes:

```bash
# Upload to production PyPI
uv run twine upload dist/*
```

### 7. Verify Installation

```bash
# Install and run from PyPI using uvx (no installation required!)
uvx unraid-mcp-server --help

# Or install globally
uv tool install unraid-mcp

# Or install in a project
uv add unraid-mcp
```

## Post-Publishing Checklist

- [ ] Create a GitHub Release with the same version tag
- [ ] Update CHANGELOG.md with release notes
- [ ] Test installation on a fresh machine
- [ ] Update documentation if API changed
- [ ] Announce release (if applicable)

## Running from Any Machine with uvx

Once published to PyPI, users can run the server without installing:

```bash
# Run directly with uvx (recommended)
uvx unraid-mcp-server

# Or with custom environment variables
UNRAID_API_URL=https://your-server uvx unraid-mcp-server
```

**Benefits of uvx:**
- No installation required
- Automatic virtual environment management
- Always uses the latest version (or specify version: `uvx unraid-mcp-server@0.2.0`)
- Clean execution environment

## Automation with GitHub Actions (Future)

Consider adding `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - name: Build package
        run: uv run python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: uv run twine upload dist/*
```

## Troubleshooting

### "File already exists" Error

PyPI doesn't allow re-uploading the same version. Options:
1. Increment version number in `pyproject.toml`
2. Delete old dist files and rebuild

### Missing Dependencies

If installation fails due to missing dependencies:
1. Check that all dependencies are in `pyproject.toml` `dependencies` section
2. Ensure dependency version constraints are correct
3. Test in a clean virtual environment

### Import Errors After Installation

If the package installs but imports fail:
1. Verify package structure in wheel: `unzip -l dist/*.whl`
2. Check that `__init__.py` files exist in all package directories
3. Ensure `packages = ["unraid_mcp"]` in `[tool.hatch.build.targets.wheel]`

## Resources

- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Semantic Versioning](https://semver.org/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Twine Documentation](https://twine.readthedocs.io/)
