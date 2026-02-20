# Lumina CLI Documentation

Lumina provides a command-line interface (CLI) for generating lithophanes directly from your terminal.

## Installation

Ensure `lumina` is installed in your environment:

```bash
pip install .
```

## Commands

### `flat`

Generates a flat lithophane STL from an image.

**Usage:**

```bash
python -m lumina.cli flat [OPTIONS] INPUT_PATH
```

**Arguments:**

- `INPUT_PATH`: Path to the source image file (e.g., `image.jpg`, `photo.png`).

**Options:**

| Option | Shorthand | Default | Description |
| :--- | :--- | :--- | :--- |
| `--output` | `-o` | `[input].stl` | Path for the output STL file. |
| `--width` | `-w` | `100.0` | Width of the lithophane in mm. |
| `--height` | `-h` | `150.0` | Height of the lithophane in mm. |
| `--max-thick` | | `3.0` | Maximum thickness (black areas) in mm. |
| `--min-thick` | | `0.5` | Minimum thickness (white areas) in mm. |
| `--frame-thick` | | `1.0` | Thickness of the frame border in mm. |
| `--frame-height` | | `2.0` | Height of the frame border in mm. |
| `--resolution` | `-r` | `5` | Resolution in pixels per mm. Higher values mean more detail but larger files. |
| `--shape` | | `rect` | Shape of the output: `rect`, `circle`, `heart`. |
| `--enhance` | | `False` | Enhance image contrast before processing. |

### Examples

**1. Basic Rectangular Lithophane**

```bash
python -m lumina.cli flat my_photo.jpg
```

**2. Circular Lithophane with Custom Frame**

```bash
python -m lumina.cli flat portrait.jpg --shape circle --width 120 --frame-thick 3 --frame-height 4
```

**3. Heart-Shaped Lithophane for Valentines**

```bash
python -m lumina.cli flat love.jpg --shape heart --enhance
```

---

### `spiral`

Generates a spiral betty art image from a photo.

**Usage:**

```bash
python -m lumina.cli spiral [OPTIONS] INPUT_PATH
```

**Options:**

| Option | Default | Description |
| :--- | :--- | :--- |
| `--output`, `-o` | `[input]_spiral.png` | Output PNG file path. |
| `--radius`, `-r` | `100.0` | Radius in mm. |
| `--resolution` | `5` | Resolution in pixels per mm. |
| `--lines` | `30` | Number of spiral lines. |
| `--angle-step` | `0.05` | Angle step for the spiral. |

**Examples:**

**1. Basic Spiral Art**

```bash
python -m lumina.cli spiral portrait.jpg
```

**2. High-Detail Spiral for Laser Engraving**

```bash
python -m lumina.cli spiral photo.jpg --radius 150 --lines 60 --resolution 10
```
