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
