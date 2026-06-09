# Publishing Kryon

This document describes the release path for Kryon on TestPyPI and PyPI.

## 1. Local build check

Run from the repository root:

```bash
python -m pip install --upgrade pip build twine
python -m build
python -m twine check dist/*
```

Expected output:

```text
PASSED
```

## 2. TestPyPI upload

Create or log in to a TestPyPI account and verify the email address.

Recommended flow:

1. Configure a Trusted Publisher for this repository on TestPyPI.
2. Use GitHub Actions to build and publish the package.
3. Install from TestPyPI in a clean virtual environment.

Manual token-based fallback:

```bash
python -m twine upload --repository testpypi dist/*
```

Then test:

```bash
python -m venv .venv-testpypi
. .venv-testpypi/bin/activate
python -m pip install --upgrade pip
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps kryon
kryon --version
kryon --self-test
```

On Windows PowerShell:

```powershell
python -m venv .venv-testpypi
.\.venv-testpypi\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps kryon
kryon --version
kryon --self-test
```

## 3. PyPI upload

After TestPyPI succeeds, publish the same version to PyPI.

Recommended flow:

1. Configure a Trusted Publisher for this repository on PyPI.
2. Build from a clean release tag.
3. Publish the package.
4. Install from PyPI in a clean virtual environment.

Manual token-based fallback:

```bash
python -m twine upload dist/*
```

Final check:

```bash
python -m venv .venv-pypi
. .venv-pypi/bin/activate
python -m pip install --upgrade pip
python -m pip install kryon
kryon --version
kryon --self-test
kryon "abc"
```

## 4. Version rules

- Never upload the same version twice. PyPI does not allow replacing files for an existing version.
- For packaging fixes, use a patch version, for example `1.0.1`.
- Update `pyproject.toml`, `CHANGELOG.md`, and the GitHub release tag together.
