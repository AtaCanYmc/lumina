# 🌟 Lumina

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-24%20passed-brightgreen.svg)]()

**Lumina** is a powerful Python toolkit for makers, artists, and 3D printing enthusiasts. Transform your images into stunning physical art pieces.

## ✨ What Can You Create?

| Feature | Description | Output |
|---------|-------------|--------|
| 🖼️ **Lithophanes** | 3D-printable light art | `.stl` mesh |
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

### Create Spiral Art

```python
from lumina import generate_spiral_betty_png
import cv2

spiral = generate_spiral_betty_png("portrait.jpg", radius_mm=50)
cv2.imwrite("spiral_art.png", spiral)
```

### Spiral then Lithophane (chain example)

You can chain the spiral generator and the lithophane generator: first produce a Spiral Betty PNG, then feed that PNG to `flat_lithophane` to create an STL.

```python
from lumina import generate_spiral_betty_png, flat_lithophane
import cv2

# 1) Generate a spiral PNG from an input image
input_photo = "portrait.jpg"  # your source image
spiral_png = "portrait_spiral.png"
spiral_img = generate_spiral_betty_png(image_path=input_photo, radius_mm=50)
cv2.imwrite(spiral_png, spiral_img)

# 2) Create a lithophane from the generated spiral PNG
mesh = flat_lithophane(
    image_path=spiral_png,
    shape="rect",
    width_mm=100,
    max_thickness=3.0,
    min_thickness=0.5,
)
mesh.save("portrait_spiral_lithophane.stl")
```

## 💻 CLI Usage

```bash
# Lithophane
python -m lumina.cli flat photo.jpg --shape circle --width 120

# Spiral art
python -m lumina.cli spiral portrait.jpg --radius 100 --lines 40
```

## 🎨 Features

- **Multiple Shapes**: Rectangle, Circle, Heart
- **Smart Framing**: Auto-generated shape-conforming frames
- **True Mesh Cutting**: Clean edges without artifacts
- **Flexible Output**: STL meshes, C-arrays, PNG images
- **CLI & Python API**: Use from terminal or integrate into your projects

## 🧪 Continuous Integration (CI) & Local Checks (updated)

This repository includes GitHub Actions workflows and `pre-commit` hooks to keep code quality high and releases reproducible. Below is the current, recommended workflow for local development and what CI enforces.

What CI does now

- Installs runtime dependencies and the package itself (editable) so tests can import `lumina`:
  - `pip install -r requirements.txt` then `pip install -e .`
- Runs style checks in *check-only* mode (so CI does not mutate files):
  - `isort --check-only .`
  - `black --check .`
  - `ruff check .`
- Runs `pytest` with coverage and uploads the generated `coverage.xml` artifact. The artifact name is generated per matrix job/run (to avoid 409 conflicts) and CI uploads to Codecov if configured.

Why this matters

- CI no longer runs `pre-commit run --all-files` in a way that modifies files; instead it enforces that the repository is already formatted. Developers must run formatting locally and commit the results to avoid CI failures.
- The workflow installs the package under test so tests won't fail with `ModuleNotFoundError: No module named 'lumina'`.

Quick local setup (recommended)

1. Create and activate a virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies and the package in editable mode:

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

3. Install and use pre-commit hooks (one-time):

```bash
pip install pre-commit
pre-commit install
# Apply hooks & auto-fixes locally
pre-commit run --all-files
# Stage and commit the changes made by hooks
git add -A
git commit -m "Apply pre-commit formatting"
```

4. Run tests & coverage locally:

```bash
pip install pytest pytest-cov
pytest -q --cov=lumina --cov-report=xml:coverage.xml
```

Publishing to PyPI

- To publish, create a git tag (`git tag vX.Y.Z && git push --tags`) and ensure repository secret `PYPI_API_TOKEN` is set (token created on PyPI).
- The `publish.yml` workflow builds sdist and wheel and publishes to PyPI.

Secrets for CI

- `PYPI_API_TOKEN`: required for automatic PyPI publishing.
- `CODECOV_TOKEN` (optional): set this if you want Codecov upload to use a token (for private repos); for public repos Codecov may work without it.

Notes & recommendations

- Run `pre-commit run --all-files` locally before pushing; CI will reject pushes that aren’t formatted.
- If you prefer CI to be less strict about formatting, we can remove `--fix` from the `ruff` pre-commit hook or make lint checks non-blocking in CI. I can apply that change if you want.
- Artifact uploads in CI are named uniquely per matrix job and set to `overwrite: true` to avoid `409 Conflict` when re-running or retrying jobs.

If you want, I can also add a short `CONTRIBUTING.md` section that enforces pre-commit + explains required commit hooks for contributors.

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
