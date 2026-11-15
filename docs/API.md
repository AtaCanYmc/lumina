# Lumina Python API Documentation

Lumina provides programmatic interfaces to generate 3D lithophane meshes and Spiral Betty raster patterns.

## Table of Contents

- [`lumina.flat_lithophane`](#luminaflat_lithophane)
  - [Function Signature](#function-signature)
  - [Parameters](#parameters)
  - [Returns](#returns)
  - [Example](#example)
- [`lumina.generate_spiral_betty_png`](#luminagenerate_spiral_betty_png)
  - [Function Signature](#function-signature-1)
  - [Parameters](#parameters-1)
  - [Returns](#returns-1)
  - [Example](#example-1)

---

## `lumina.flat_lithophane`

Generates a flat or shaped 3D-printable lithophane STL mesh from an input image.

### Function Signature

```python
from stl import mesh
from lumina import flat_lithophane

def flat_lithophane(
    image_path: str,
    width_mm: float = 100.0,
    height_mm: float = 150.0,
    max_thickness: float = 3.0,
    min_thickness: float = 0.5,
    frame_thick_mm: float = 1.0,
    frame_height_mm: float = 2.0,
    resolution: int = 5,
    enhance: bool = False,
    normalize: bool = False,
    shape: str = "rect",
) -> mesh.Mesh:
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `image_path` | `str` | *required* | Path to the source image file (`.jpg`, `.png`). |
| `width_mm` | `float` | `100.0` | Target width of the lithophane in millimeters. |
| `height_mm` | `float` | `150.0` | Target height of the lithophane in millimeters. |
| `max_thickness` | `float` | `3.0` | Maximum thickness in millimeters, mapped to black pixels. |
| `min_thickness` | `float` | `0.5` | Minimum thickness in millimeters, mapped to white pixels. |
| `frame_thick_mm` | `float` | `1.0` | Width of the boundary frame border in millimeters. |
| `frame_height_mm`| `float` | `2.0` | Height of the frame border in millimeters. If `0`, matches maximum relief height. |
| `resolution` | `int` | `5` | Grid resolution in pixels per millimeter. |
| `enhance` | `bool` | `False` | Apply contrast enhancement before meshing. |
| `normalize` | `bool` | `False` | Normalize grayscale dynamic range before processing. |
| `shape` | `str` | `"rect"` | Boundary geometry: `"rect"`, `"circle"`, `"heart"`. |

### Returns

- `stl.mesh.Mesh`: A `numpy-stl` mesh object representing the generated 3D geometry.

### Example

```python
from lumina import flat_lithophane

# Generate a heart-shaped lithophane
mesh_obj = flat_lithophane(
    image_path="portrait.jpg",
    shape="heart",
    width_mm=120.0,
    max_thickness=3.0,
    min_thickness=0.5,
    enhance=True,
)

# Save binary STL file
mesh_obj.save("portrait_heart.stl")
```

---

## `lumina.generate_spiral_betty_png`

Generates an Archimedean spiral art raster image where stroke width varies inversely with image brightness.

### Function Signature

```python
import numpy as np
from lumina import generate_spiral_betty_png

def generate_spiral_betty_png(
    image_path: str,
    radius_mm: float = 100.0,
    resolution: int = 5,
    lines: int = 30,
    angle_step: float = 0.05,
) -> np.ndarray:
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `image_path` | `str` | *required* | Path to the input image file (`.jpg`, `.png`). |
| `radius_mm` | `float` | `100.0` | Target radius in millimeters. |
| `resolution` | `int` | `5` | Resolution in pixels per millimeter. |
| `lines` | `int` | `30` | Number of spiral rotations from center to radius. |
| `angle_step` | `float` | `0.05` | Angular sampling increment in radians. |

### Returns

- `np.ndarray`: Grayscale NumPy array (`uint8`) containing the rendered spiral art pattern.

### Example

```python
import cv2
from lumina import generate_spiral_betty_png

# Generate a Spiral Betty pattern
spiral_image = generate_spiral_betty_png(
    image_path="portrait.jpg",
    radius_mm=75.0,
    lines=45,
    angle_step=0.03,
)

# Save result as PNG
cv2.imwrite("portrait_spiral.png", spiral_image)
```
