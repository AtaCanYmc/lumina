# Lumina: 3D Lithophane Generator

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Lumina** is a specialized Python package for makers and 3D printing enthusiasts. it allows you to easily convert 2D images into high-quality 3D lithophane STL files, ready for printing.

## 🚀 Features

- **High-Quality Conversion**: Converts grayscale images into detailed 3D meshes.
- **Multiple Shapes**: Generate lithophanes in different shapes:
    - `Rect` (Standard rectangular)
    - `Circle` (Circular/Cylindrical base)
    - `Heart` (Heart-shaped)
- **Smart Framing**: Automatically adds a smooth, shape-conforming frame around your lithophane.
- **True Mesh Cutting**: Physically cuts the mesh to the desired shape, eliminating unwanted artifacts.
- **Dual Interface**: Use it via the command line (CLI) or as a Python library.
- **Customizable**: Control thickness, dimensions, frame size, and resolution.

## 📦 Installation

To install Lumina, navigate to the project directory and run:

```bash
pip install .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

## 💻 CLI Usage

Lumina comes with a powerful CLI tool called `lumina`.

### Basic Usage
Convert an image to a standard flat lithophane:

```bash
python -m lumina.cli flat my_image.jpg
```

### Advanced Usage
Generate a circular lithophane with a frame:

```bash
python -m lumina.cli flat my_image.jpg --shape circle --width 120 --frame-thick 5
```

For more details on CLI commands, see [CLI Documentation](docs/CLI.md).

## 🐍 Python API Usage

You can also use Lumina in your Python scripts.

```python
from lumina import flat_lithophane

# Generate a heart-shaped lithophane
mesh = flat_lithophane(
    image_path="path/to/image.jpg",
    shape="heart",
    width_mm=100,
    max_thickness=3.0,
    min_thickness=0.5
)

# Save the mesh
mesh.save("my_heart_lithophane.stl")
```

For full API reference, see [API Documentation](docs/API.md).

## 📂 Documentation

- [CLI Reference](docs/CLI.md)
- [Python API Reference](docs/API.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
