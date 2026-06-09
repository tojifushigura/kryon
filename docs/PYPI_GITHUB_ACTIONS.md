# GitHub Actions PyPI workflow examples

The repository includes a package build check workflow. For actual publishing, create one of the workflows below after configuring Trusted Publishing on TestPyPI/PyPI.

## TestPyPI workflow

File: `.github/workflows/publish-testpypi.yml`

```yaml
name: Publish to TestPyPI

on:
  workflow_dispatch:

permissions:
  contents: read
  id-token: write

jobs:
  publish-testpypi:
    runs-on: ubuntu-latest
    environment:
      name: testpypi
      url: https://test.pypi.org/project/kryon/
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Build package
        run: |
          python -m pip install --upgrade pip build twine
          python -m build
          python -m twine check dist/*
      - name: Publish package
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/
          print-hash: true
```

## PyPI workflow

File: `.github/workflows/publish-pypi.yml`

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

permissions:
  contents: read
  id-token: write

jobs:
  publish-pypi:
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/project/kryon/
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Build package
        run: |
          python -m pip install --upgrade pip build twine
          python -m build
          python -m twine check dist/*
      - name: Publish package
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          print-hash: true
```
