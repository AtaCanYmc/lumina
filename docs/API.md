# Lumina Python API Documentation

Lumina can be used as a Python library to programmatically generate lithophanes.

## `lumina.flat_lithophane`

The main function for generating flat (and shaped) lithophanes.

```python
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
    shape: str = "rect"
) -> mesh.Mesh:
```

### Parameters

- **`image_path`** (`str`): Path to the input image file.
- **`width_mm`** (`float`, default `100.0`): Target width of the lithophane in millimeters.
- **`height_mm`** (`float`, default `150.0`): Target height of the lithophane in millimeters.
- **`max_thickness`** (`float`, default `3.0`): Maximum thickness in mm, corresponding to the blackest parts of the image.
- **`min_thickness`** (`float`, default `0.5`): Minimum thickness in mm, corresponding to the whitest parts of the image.
- **`frame_thick_mm`** (`float`, default `1.0`): The thickness (width) of the frame border in mm.
- **`frame_height_mm`** (`float`, default `2.0`): The height of the frame border in mm. If `0`, it matches the maximum height of the image.
- **`resolution`** (`int`, default `5`): Resolution in pixels per mm. Determines the detail level.
- **`enhance`** (`bool`, default `False`): If `True`, applies contrast enhancement to the image before processing.
- **`shape`** (`str`, default `"rect"`): The shape of the lithophane. Supported values:
    - `"rect"`: Standard rectangular shape.
    - `"circle"`: Circular shape.
    - `"heart"`: Heart shape.

### Returns

- **`mesh.Mesh`**: A `numpy-stl` mesh object representing the generated 3D model.

### Example

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

---

## `lumina.generate_bitmap`

Generates a monochrome bitmap from an image, suitable for embedded displays.

```python
from lumina import generate_bitmap

def generate_bitmap(
    image_path: str,
    width: int = 128,
    height: int = 64,
    threshold: int = 128,
    enhance: bool = False
) -> np.ndarray:
```

### Parameters

- **`image_path`** (`str`): Path to the input image file.
- **`width`** (`int`, default `128`): Target width in pixels.
- **`height`** (`int`, default `64`): Target height in pixels.
- **`threshold`** (`int`, default `128`): Binarization threshold (0-255).
- **`enhance`** (`bool`, default `False`): Apply contrast enhancement before processing.

### Returns

- **`np.ndarray`**: A 2D NumPy array of 0s and 1s representing the bitmap.

### Example

```python
from lumina import generate_bitmap
from lumina.core.bitmap_service import export_to_c_array

# Generate a 128x64 bitmap
bitmap = generate_bitmap("path/to/logo.png", width=128, height=64)

# Export as C array for Arduino/ESP32
c_code = export_to_c_array(bitmap, var_name="logo_data")
print(c_code)
```

---

## `lumina.generate_spiral_betty_png`

Generates a spiral betty (spiral art) image from an input image.

```python
from lumina import generate_spiral_betty_png

def generate_spiral_betty_png(
    image_path: str,
    radius_mm: float = 100.0,
    resolution: int = 5,
    enhance: bool = False
) -> np.ndarray:
```

### Parameters

- **`image_path`** (`str`): Path to the input image file.
- **`radius_mm`** (`float`, default `100.0`): Target radius in mm.
- **`resolution`** (`int`, default `5`): Resolution in pixels per mm.
- **`enhance`** (`bool`, default `False`): Apply contrast enhancement before processing.

### Returns

- **`np.ndarray`**: A grayscale image with the spiral art pattern.

### Example

```python
from lumina import generate_spiral_betty_png
import cv2

# Generate a spiral betty
spiral = generate_spiral_betty_png("path/to/portrait.jpg", radius_mm=50)

# Save the result
cv2.imwrite("spiral_output.png", spiral)
```
