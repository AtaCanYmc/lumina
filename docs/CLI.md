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

### `bitmap`

Generates a monochrome bitmap for embedded displays (OLED, LCD, etc.).

**Usage:**

```bash
python -m lumina.cli bitmap [OPTIONS] INPUT_PATH
```

**Options:**

| Option | Default | Description |
| :--- | :--- | :--- |
| `--width` | `128` | Target width in pixels. |
| `--height` | `64` | Target height in pixels. |
| `--threshold` | `128` | Binarization threshold (0-255). |
| `--output-format` | `c_array` | Output format: `c_array` (for C/C++ headers) or `hex` (raw hex string). |

**Examples:**

**1. Generate 128x64 Bitmap for SSD1306**

```bash
python -m lumina.cli bitmap logo.png > logo_data.h
```

**2. Generate Hex String for Custom Protocol**

```bash
python -m lumina.cli bitmap icon.jpg --width 32 --height 32 --output-format hex
```
