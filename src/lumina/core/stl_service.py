import cv2
import numpy as np
from stl import Mesh, mesh

from .shapes import ShapeFactory


def add_frame_to_z(
    z, frame_mm, resolution: float = 5, extra_height_mm: float = 0
) -> np.ndarray:
    """Adds a frame around the z matrix.

    Args:
        z (np.ndarray): Z matrix
        frame_mm (float): Frame size in mm
        resolution (int, optional): Image resolution in pixels per mm. Defaults to 5.
        extra_height_mm (int, optional): Extra height to add to frame. Defaults to 0.

    Returns:
        np.ndarray: Z matrix with frame
    """
    if frame_mm <= 0:
        return z

    frame_pxl = int(frame_mm * resolution)
    frame_height = np.max(z) + extra_height_mm
    new_shape = (z.shape[0] + 2 * frame_pxl, z.shape[1] + 2 * frame_pxl)
    z_framed = np.full(new_shape, frame_height)
    z_framed[frame_pxl:-frame_pxl, frame_pxl:-frame_pxl] = z
    return z_framed


def jpg_to_stl(
    image: np.ndarray,
    max_thick: float = 3.0,
    min_thick: float = 0.5,
    resolution: int = 5,
    invert: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Function to convert filename to stl with given width.

    Args:
        image (np.ndarray): Path to image file
        max_thick (float, optional): Maximum thickness in mm. Defaults to 3.0.
        min_thick (float, optional): Minimum thickness in mm. Defaults to 0.5.
        resolution (int, optional): Image resolution in pixels per mm. Defaults to 10.
        invert (bool, optional): Invert image. Defaults to True.

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray]: x, y, z matrices
    """

    # Ensure image is a float array in 0..1 range. Accept either 0..255 uint8 or 0..1 floats.
    image = np.asarray(image)
    if image.dtype == np.uint8 or image.max() > 1.5:
        # likely 0..255
        image = image.astype(np.float64) / 255.0
    else:
        image = image.astype(np.float64)

    if len(image.shape) > 2:
        raise RuntimeError(
            f"Image shape {image.shape} is not supported. "
            f"Only grayscale images are supported."
        )

    if resolution <= 0:
        raise ValueError("Resolution must be a positive integer.")

    if min_thick >= max_thick:
        raise ValueError("min_thick must be less than max_thick.")

    # Flip image vertically
    image = np.flipud(image)

    # Invert threshold for z matrix
    if invert:
        image = 1 - np.double(image)
    else:
        image = np.double(image)

    # Scale z matrix to desired max depth and add base height
    depth_mm = max_thick - min_thick
    offset_mm = min_thick
    z = image * depth_mm + offset_mm

    # Add a thin back plane
    z_with_back = np.zeros([z.shape[0] + 2, z.shape[1] + 2])
    z_with_back[1:-1, 1:-1] = z
    z = z_with_back

    x1 = np.linspace(0, z.shape[1] / resolution, z.shape[1])
    y1 = np.linspace(0, z.shape[0] / resolution, z.shape[0])
    x, y = np.meshgrid(x1, y1)
    x = np.fliplr(x)
    return x, y, z


def shape_mask(height, width, shape="circle"):
    """
    Deprecated: Use ShapeStrategy classes instead.
    Maintained for backward compatibility if needed, using the new strategies.
    """
    strategy = ShapeFactory.get_strategy(shape)
    return strategy.create_mask(height, width)


def create_solid_lithophane(x, y, z, mask=None) -> mesh.Mesh:
    """Creates a solid flat lithophane STL file.

    Args:
        x (np.ndarray): X matrix
        y (np.ndarray): Y matrix
        z (np.ndarray): Z matrix
        mask (np.ndarray, optional): Boolean mask for valid vertices. Defaults to None.

    Returns:
        mesh.Mesh
    """
    # Sanitize Z matrix: replace NaN/inf, ensure finite and within reasonable bounds.
    # This defends against earlier pipeline errors or corrupted inputs that
    # can produce extreme Z spikes (negative/positive).
    # We perform a conservative clamp using a robust estimate of the finite range.
    z = np.asarray(z, dtype=np.float64)
    # Replace NaN with minimum finite value (or 0 if no finite values)
    finite_mask = np.isfinite(z)
    if not np.any(finite_mask):
        # If nothing finite, fallback to zeros
        z[:] = 0.0
    else:
        finite_vals = z[finite_mask]
        finite_min = float(np.min(finite_vals))
        finite_max = float(np.max(finite_vals))
        # Replace non-finite entries
        z[~finite_mask] = finite_min
        # Clamp extremes to a slightly extended finite range
        margin = max(1.0, (finite_max - finite_min) * 0.1)
        z = np.clip(z, finite_min - margin, finite_max + margin)

    rows, cols = z.shape
    faces = []

    # Vertices: Top and Bottom faces (Z and Z=0)
    vertices = np.vstack(
        [
            np.column_stack([x.flatten(), y.flatten(), z.flatten()]),
            np.column_stack([x.flatten(), y.flatten(), np.zeros_like(z.flatten())]),
        ]
    )
    offset = rows * cols

    # Helper to check if a cell (quad) is valid
    # A cell at (r, c) is considered valid if all its 4 corners are inside the mask
    def is_valid_cell(r, c):
        if mask is None:
            return True
        # Check bounds just in case
        if r < 0 or r >= rows - 1 or c < 0 or c >= cols - 1:
            return False
        return mask[r, c] and mask[r, c + 1] and mask[r + 1, c] and mask[r + 1, c + 1]

    # FreeCAD logic for face creation
    for r in range(rows - 1):
        for c in range(cols - 1):
            if not is_valid_cell(r, c):
                continue

            lt = r * cols + c  # Sol-Üst
            rt = lt + 1  # Sağ-Üst
            lb = (r + 1) * cols + c  # Sol-Alt
            rb = lb + 1  # Sağ-Alt

            # Front face (Z+ direction)
            faces.append([lt, lb, rt])
            faces.append([rt, lb, rb])

            # Back face (Z- direction)
            faces.append([lt + offset, rt + offset, lb + offset])
            faces.append([rt + offset, rb + offset, lb + offset])

            # WALLS (Waterproof) - Check 4 neighbors

            # Left Wall (check if neighbor to left is invalid)
            if c == 0 or not is_valid_cell(r, c - 1):
                faces.append([lt, lt + offset, lb])
                faces.append([lb, lt + offset, lb + offset])

            # Right Wall (check if neighbor to right is invalid)
            if c == cols - 2 or not is_valid_cell(r, c + 1):
                faces.append([rt, rb, rt + offset])
                faces.append([rb, rb + offset, rt + offset])

            # Top Wall (check if neighbor above is invalid)
            if r == 0 or not is_valid_cell(r - 1, c):
                faces.append([lt, rt, lt + offset])
                faces.append([rt, rt + offset, lt + offset])

            # Bottom Wall (check if neighbor below is invalid)
            if r == rows - 2 or not is_valid_cell(r + 1, c):
                faces.append([lb, lb + offset, rb])
                faces.append([rb, lb + offset, rb + offset])

    litho_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        litho_mesh.v0[i] = vertices[f[0]]
        litho_mesh.v1[i] = vertices[f[1]]
        litho_mesh.v2[i] = vertices[f[2]]

    return litho_mesh


def image_to_flat_stl(
    image: np.ndarray,
    max_th: float,
    min_th: float,
    frame_thick_mm: float,
    frame_height_mm: float = 0.0,
    resolution: int = 5,
    shape: str = "rect",
) -> Mesh:
    """Converts an image to an STL file path.

    Supported shapes:
        rect
        circle
        heart

    Args:
        image (np.ndarray): Input image
        max_th (float): Maximum thickness in mm
        min_th (float): Minimum thickness in mm
        frame_thick_mm (float): Frame size in mm
        frame_height_mm (float): Frame height in mm
        resolution (int): Image resolution in pixels per mm
        shape (str): Image shape

    Returns:
        Mesh
    """
    # 1. Generate base Z matrix (tight, only backplane border)
    _, _, z = jpg_to_stl(
        image=image,
        max_thick=max_th,
        min_thick=min_th,
        resolution=resolution,
    )

    # 2. Add Frame Padding (Physical Space)
    # We add the frame space to Z. This creates a high-Z border around the image.
    # For Rect shape, this is the final frame.
    # For Shapes, this provides the canvas for the shaped frame, and the corners will be cut.
    z = add_frame_to_z(
        z=z,
        frame_mm=frame_thick_mm,
        resolution=resolution,
        extra_height_mm=frame_height_mm,
    )

    # Sanity clamp: ensure Z values stay within expected physical bounds.
    # This protects against corrupted inputs or earlier bugs that create
    # extremely large/small Z values (seen as long spikes / "sopa").
    # Allow a tiny epsilon margin.
    eps = 1e-6
    z_min_allowed = min_th - eps
    z_max_allowed = max_th + frame_height_mm + eps
    z = np.clip(z, z_min_allowed, z_max_allowed)

    # 3. Regenerate X, Y grids (since Z shape changed)
    x1 = np.linspace(0, z.shape[1] / resolution, z.shape[1])
    y1 = np.linspace(0, z.shape[0] / resolution, z.shape[0])
    x, y = np.meshgrid(x1, y1)
    x = np.fliplr(x)

    # 4. Generate Mask and Fix Z-Levels

    # Calculate dimensions of the inner content (Image + Backplane)
    # The frame padding was added to all sides.
    frame_pxl = int(frame_thick_mm * resolution)

    # Total Z shape is (H_img + 2 + 2*frame_pxl, W_img + 2 + 2*frame_pxl)
    # The "Content" (Image+Backplane) is in the middle.
    h_total, w_total = z.shape
    h_inner = h_total - 2 * frame_pxl
    w_inner = w_total - 2 * frame_pxl

    if shape == "rect":
        # Rect: Valid everywhere.
        mask = np.ones(z.shape, dtype=bool)
    else:
        # Shapes: We need to mask the content and dilate for frame.

        # Inner Mask: covers the Content area.
        # Note: The content itself has a 1px backplane border from jpg_to_stl.
        # We usually want the shape to apply to the IMAGE, essentially cutting the backplane corners too.
        # If we use h_inner, w_inner, we are masking the "Image + Backplane".
        strategy = ShapeFactory.get_strategy(shape)
        # Create mask for the inner content
        inner_content_mask = strategy.create_mask(h_inner, w_inner)

        # Place inner mask into full-size array
        full_mask_uint8 = np.zeros(z.shape, dtype=np.uint8)
        full_mask_uint8[
            frame_pxl : frame_pxl + h_inner, frame_pxl : frame_pxl + w_inner
        ] = inner_content_mask.astype(np.uint8)

        # Dilate to create Frame
        if frame_thick_mm > 0:
            k_size = 2 * frame_pxl + 1
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size, k_size))
            outer_mask = cv2.dilate(full_mask_uint8, kernel)
            mask = outer_mask.astype(bool)

            # Fix Z-levels for the actual shaped frame
            # The frame is the region between the inner mask and the outer mask.
            inner_placed_mask = full_mask_uint8.astype(bool)
            frame_region = mask & (~inner_placed_mask)

            # Force Z to frame_height in the frame region.
            # This handles the case where the shaped frame overlaps the low-Z image corners.
            # Calculate desired frame height: Max Z (which includes the high border from add_frame_to_z)
            # strictly speaking, add_frame_to_z set the border to (max(image) + extra).
            # So np.max(z) is correct.
            frame_height = np.max(z)
            z[frame_region] = frame_height

        else:
            mask = full_mask_uint8.astype(bool)

    stl = create_solid_lithophane(x, y, z, mask=mask)
    return stl


def apply_shape_to_heightmap(heightmap, shape="circle", min_thickness=0.8):
    h, w = heightmap.shape
    # Use Factory/Strategy to get mask
    strategy = ShapeFactory.get_strategy(shape)
    mask = strategy.create_mask(h, w)

    shaped = heightmap.copy()
    shaped[~mask] = min_thickness

    return shaped, mask
