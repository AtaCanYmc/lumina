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
- [`lumina.open_viewer`](#luminaopen_viewer)
  - [Function Signature](#function-signature-2)
  - [Parameters](#parameters-2)
  - [Returns](#returns-2)
  - [Example](#example-2)
- [`lumina.generate_viewer_html`](#luminagenerate_viewer_html)
  - [Function Signature](#function-signature-3)
  - [Parameters](#parameters-3)
  - [Returns](#returns-3)
- [`lumina.get_mesh_stats`](#luminaget_mesh_stats)
  - [Function Signature](#function-signature-4)
  - [Parameters](#parameters-4)
  - [Returns](#returns-4)

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

---

## `lumina.open_viewer`

Generates an interactive WebGL 3D viewer for an STL lithophane file and optionally opens it in the default system web browser.

### Function Signature

```python
from lumina import open_viewer

def open_viewer(
    stl_path: str,
    output_html: str | None = None,
    open_browser: bool = True,
) -> str:
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `stl_path` | `str` | *required* | Path to the source `.stl` file. |
| `output_html` | `str \| None` | `None` | Destination path to save the standalone HTML file. If `None`, creates a temporary file. |
| `open_browser` | `bool` | `True` | Whether to automatically launch the default browser with the generated page. |

### Returns

- `str`: Absolute file path to the generated HTML viewer document.

### Example

```python
from lumina import open_viewer

# Render and open interactive 3D simulation
html_path = open_viewer("lithophane.stl")
print(f"Viewport launched: {html_path}")
```

---

## `lumina.generate_viewer_html`

Generates the self-contained HTML string embedding the 3D STL geometry, Three.js runtime, OrbitControls, and physical backlight transmission shader.

### Function Signature

```python
from typing import Any
from lumina import generate_viewer_html

def generate_viewer_html(
    stl_path_or_bytes: str | bytes,
    title: str = "Lumina 3D Lithophane Viewer",
    mesh_stats: dict[str, Any] | None = None,
) -> str:
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `stl_path_or_bytes` | `str \| bytes` | *required* | File path or raw binary byte buffer of the STL mesh. |
| `title` | `str` | `"Lumina 3D Lithophane Viewer"` | Page title string. |
| `mesh_stats` | `dict[str, Any] \| None` | `None` | Precomputed geometric statistics dictionary. |

### Returns

- `str`: Self-contained HTML document string.

---

## `lumina.get_mesh_stats`

Computes dimensional bounds, triangle count, volumetric displacement, and estimated physical PLA filament weight for a given mesh.

### Function Signature

```python
from typing import Any
from stl import mesh
from lumina import get_mesh_stats

def get_mesh_stats(
    mesh_obj: mesh.Mesh,
    density_g_cm3: float = 1.24,
) -> dict[str, Any]:
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `mesh_obj` | `stl.mesh.Mesh` | *required* | Input `numpy-stl` mesh object. |
| `density_g_cm3` | `float` | `1.24` | Material density in $\text{g/cm}^3$ (default: $1.24$ for standard PLA). |

### Returns

- `dict[str, Any]`: Dictionary with keys `facets`, `width_mm`, `height_mm`, `depth_mm`, `volume_cm3`, and `weight_grams`.

