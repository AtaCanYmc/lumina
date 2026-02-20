# 🌟 Lumina

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-14%20passed-brightgreen.svg)]()

**Lumina** is a powerful Python toolkit for makers, artists, and 3D printing enthusiasts. Transform your images into stunning physical art pieces.

## ✨ What Can You Create?

| Feature | Description | Output |
|---------|-------------|--------|
| 🖼️ **Lithophanes** | 3D-printable light art | `.stl` mesh |
| 🔲 **Bitmaps** | Monochrome images for OLED/LCD displays | C-array / Hex |
| 🌀 **Spiral Betty** | Spiral art for laser/CNC engraving | `.png` image |

## 🚀 Quick Start

### Installation

```bash
pip install lumina-tools
```

Or from source:

```bash
git clone https://github.com/AtaCanYmc/lumina.git
cd lumina
pip install -e .
```

### Create a Lithophane

```python
from lumina import flat_lithophane

mesh = flat_lithophane(
    "photo.jpg",
    shape="heart",      # rect, circle, heart
    width_mm=100,
    max_thickness=3.0
)
mesh.save("lithophane.stl")
```

### Generate Bitmap for OLED

```python
from lumina import generate_bitmap
from lumina.core.bitmap_service import export_to_c_array

bitmap = generate_bitmap("logo.png", width=128, height=64)
print(export_to_c_array(bitmap, "logo_data"))
```

### Create Spiral Art

```python
from lumina import generate_spiral_betty_png
import cv2

spiral = generate_spiral_betty_png("portrait.jpg", radius_mm=50)
cv2.imwrite("spiral_art.png", spiral)
```

## 💻 CLI Usage

```bash
# Lithophane
python -m lumina.cli flat photo.jpg --shape circle --width 120

# Bitmap for embedded displays
python -m lumina.cli bitmap logo.png --width 128 --height 64

# Spiral art
python -m lumina.cli spiral portrait.jpg --radius 100 --lines 40
```

## 🎨 Features

- **Multiple Shapes**: Rectangle, Circle, Heart
- **Smart Framing**: Auto-generated shape-conforming frames
- **True Mesh Cutting**: Clean edges without artifacts
- **Flexible Output**: STL meshes, C-arrays, PNG images
- **CLI & Python API**: Use from terminal or integrate into your projects

## 📖 Documentation

- [CLI Reference](docs/CLI.md)
- [Python API](docs/API.md)
- [Contributing](docs/CONTRIBUTING.md)

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

Made with ❤️ for the maker community

## 🧪 Continuous Integration (CI) & Local Checks

This repository includes GitHub Actions workflows and pre-commit hooks to keep code quality high and releases reproducible.

- CI workflow: `.github/workflows/python-ci.yml`
  - Runs on pushes and PRs to `main`/`master`.
  - Matrix: Python 3.10, 3.11, 3.12.
  - Installs dependencies from `requirements.txt`, runs `ruff` (lint), runs `pytest` with coverage and uploads `coverage.xml` to Codecov if `CODECOV_TOKEN` secret is set.

- Publish workflow: `.github/workflows/publish.yml`
  - Triggers on tags like `vX.Y.Z` and publishes wheels and sdist to PyPI using `PYPI_API_TOKEN` secret.

- pre-commit config: `.pre-commit-config.yaml`
  - Includes `black`, `ruff`, `isort` and common pre-commit hooks.

Quick local setup

1. Create and activate a virtualenv (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install project dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Install pre-commit hooks (one-time):

```bash
pip install pre-commit
pre-commit install
# To run on all files once
pre-commit run --all-files
```

4. Run tests and coverage locally:

```bash
pip install pytest pytest-cov
pytest -q --cov=src --cov-report=xml:coverage.xml
```

Publishing to PyPI

- To publish, create a git tag (`git tag vX.Y.Z && git push --tags`) and ensure repository secret `PYPI_API_TOKEN` is set (token created on PyPI).
- The `publish.yml` workflow will build and publish the package.

Secrets for CI

- `PYPI_API_TOKEN`: required for automatic PyPI publishing.
- `CODECOV_TOKEN` (optional): set this if you want Codecov upload to use a token (for private repos); for public repos Codecov sometimes works without it.

If you want, I can also:
- Add a Codecov badge to the top of the README once Codecov is configured.
- Make `ruff` non-blocking in CI (current config fails CI on lint errors) if you'd prefer warnings instead.
