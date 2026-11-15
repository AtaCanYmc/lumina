# Lumina CLI Documentation

Lumina provides a command-line interface for generating lithophane 3D meshes and Spiral Betty raster patterns directly from the terminal.

## Table of Contents

- [Invocation](#invocation)
- [Interactive Wizard](#interactive-wizard)
- [Commands](#commands)
  - [`lumina flat`](#lumina-flat)
  - [`lumina spiral`](#lumina-spiral)
  - [`lumina interactive`](#interactive-wizard)
- [Command Reference and Options](#command-reference-and-options)
  - [Options for `flat`](#options-for-flat)
  - [Options for `spiral`](#options-for-spiral)
- [Examples](#examples)

## Invocation

After installing `lumina-tools`, execute via the console script:

```bash
lumina --help
```

Running `lumina` without subcommands in an interactive terminal prints the brand banner and available commands.

Alternatively, run the module directly through Python:

```bash
python -m lumina.cli --help
```

---

## Interactive Wizard

For guided configuration without memorizing CLI flags, run the interactive wizard:

```bash
lumina interactive
# or via shorthand alias:
lumina wizard
```

The wizard prompts step-by-step for:
1. Target generation mode (Flat Lithophane STL vs. Spiral Betty PNG).
2. Input source image file.
3. Dimensional parameters, resolution, shape, and frame settings.
4. Output file path (with intelligent pre-filled defaults).
5. Final confirmation prompt before processing.

---

## Commands

### `lumina flat`

Generates a flat or shaped lithophane STL mesh from a source image.

```bash
lumina flat [OPTIONS] INPUT_PATH
```

#### Options for `flat`

| Option | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `--output` | `-o` | `[input].stl` | Path for the destination STL file. |
| `--width` | `-w` | `100.0` | Target width in millimeters. |
| `--height` | `-h` | `150.0` | Target height in millimeters. |
| `--max-thick` | | `3.0` | Maximum thickness in mm for darkest pixels. |
| `--min-thick` | | `0.5` | Minimum thickness in mm for lightest pixels. |
| `--frame-thick` | | `1.0` | Border frame width in millimeters. |
| `--frame-height` | | `2.0` | Border frame height in millimeters. Set to `0` to match maximum image relief. |
| `--resolution` | `-r` | `5` | Grid resolution in pixels per millimeter. |
| `--shape` | | `rect` | Boundary geometry: `rect`, `circle`, `heart`. |
| `--enhance / --no-enhance` | | `False` | Apply contrast enhancement before meshing. |
| `--normalize / --no-normalize` | | `False` | Normalize grayscale levels across dynamic range before processing. |

---

### `lumina spiral`

Generates a Spiral Betty raster pattern from a source image.

```bash
lumina spiral [OPTIONS] INPUT_PATH
```

#### Options for `spiral`

| Option | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `--output` | `-o` | `[input]_spiral.png` | Destination PNG image file path. |
| `--radius` | `-r` | `100.0` | Radius of the spiral boundary in millimeters. |
| `--resolution` | | `5` | Grid resolution in pixels per millimeter. |
| `--lines` | | `30` | Number of concentric spiral rotations. |
| `--angle-step` | | `0.05` | Angular increment in radians per step. |

---

## Examples

### 1. Basic Rectangular Lithophane

```bash
lumina flat landscape.jpg
```

### 2. Circular Lithophane with Reinforced Frame

```bash
lumina flat portrait.jpg --shape circle --width 120.0 --frame-thick 3.0 --frame-height 4.0
```

### 3. Heart-Shaped Lithophane with Contrast Enhancement

```bash
lumina flat photo.jpg --shape heart --enhance --max-thick 3.2 --min-thick 0.6
```

### 4. Standard Spiral Betty Art

```bash
lumina spiral portrait.jpg --radius 80.0 --lines 35
```

### 5. High-Resolution Spiral for Laser Engraving

```bash
lumina spiral sketch.jpg --radius 150.0 --lines 60 --resolution 10 --angle-step 0.02
```
