import numpy as np
from stl import mesh, Mesh


def add_frame_to_z(z, frame_mm, resolution: float = 5, extra_height_mm: float = 0) -> np.ndarray:
    """Adds a frame around the z matrix.

    Args:x
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
        frame_thick_mm: float = 0.5,
        frame_height_mm: float = 0.0,
        resolution: int = 5,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Function to convert filename to stl with given width.

    Args:
        image (np.ndarray): Path to image file
        max_thick (float, optional): Maximum thickness in mm. Defaults to 3.0.
        min_thick (float, optional): Minimum thickness in mm. Defaults to 0.5.
        frame_thick_mm (float, optional): Frame around image in mm. Defaults to 0.5.
        frame_height_mm (float, optional): Frame height in mm. Defaults to 0.0.
        resolution (int, optional): Image resolution in pixels per mm. Defaults to 10.

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray]: x, y, z matrices
    """

    if len(image.shape) > 2:
        raise RuntimeError(f"Image shape {image.shape} is not supported. "
                           f"Only grayscale images are supported.")

    if resolution <= 0:
        raise ValueError("Resolution must be a positive integer.")

    if min_thick >= max_thick:
        raise ValueError("min_thick must be less than max_thick.")

    # Flip image vertically
    image = np.flipud(image)

    # Invert threshold for z matrix
    image = 1 - np.double(image)

    # Scale z matrix to desired max depth and add base height
    depth_mm = max_thick - min_thick
    offset_mm = min_thick
    z = image * depth_mm + offset_mm

    # Add a frame around the image
    z = add_frame_to_z(
        z=z,
        frame_mm=frame_thick_mm,
        resolution=resolution,
        extra_height_mm=frame_height_mm
    )

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
    Creates a boolean mask for a given shape.

    Args:
        height (int)
        width (int)
        shape (str): "circle" or "heart"

    Returns:
        np.ndarray: boolean mask
    """
    y, x = np.ogrid[:height, :width]

    cx = width / 2
    cy = height / 2

    # normalize coordinates to [-1,1]
    nx = (x - cx) / (width / 2)
    ny = (y - cy) / (height / 2)

    if shape == "circle":
        mask = nx ** 2 + ny ** 2 <= 1

    elif shape == "heart":
        # classic implicit heart equation
        heart = (nx ** 2 + ny ** 2 - 1) ** 3 - nx ** 2 * ny ** 3
        mask = heart <= 0

    else:
        raise ValueError("Unsupported shape")

    return mask


def create_solid_lithophane(x, y, z) -> mesh.Mesh:
    """Creates a solid flat lithophane STL file.

    Args:
        x (np.ndarray): X matrix
        y (np.ndarray): Y matrix
        z (np.ndarray): Z matrix

    Returns:
        mesh.Mesh
    """
    rows, cols = z.shape
    faces = []

    # Vertices: Top and Bottom faces (Z and Z=0)
    vertices = np.vstack([
        np.column_stack([x.flatten(), y.flatten(), z.flatten()]),
        np.column_stack([x.flatten(), y.flatten(), np.zeros_like(z.flatten())])
    ])
    offset = rows * cols

    # FreeCAD logic for face creation
    for r in range(rows - 1):
        for c in range(cols - 1):
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

    # WALLS (Waterproof)
    for r in range(rows - 1):
        # Left Side
        faces.append([r * cols, r * cols + offset, (r + 1) * cols])
        faces.append([(r + 1) * cols, r * cols + offset, (r + 1) * cols + offset])
        # Right side
        faces.append([r * cols + cols - 1, (r + 1) * cols + cols - 1, r * cols + cols - 1 + offset])
        faces.append([(r + 1) * cols + cols - 1, (r + 1) * cols + cols - 1 + offset, r * cols + cols - 1 + offset])

    for c in range(cols - 1):
        # Upper side
        faces.append([c, c + 1, c + offset])
        faces.append([c + 1, c + 1 + offset, c + offset])
        # Lower side
        v = (rows - 1) * cols + c
        faces.append([v, v + offset, v + 1])
        faces.append([v + 1, v + offset, v + 1 + offset])

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
        shape: str = "rect"
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
    x, y, z = jpg_to_stl(
        image=image,
        frame_thick_mm=frame_thick_mm,
        max_thick=max_th,
        min_thick=min_th,
        resolution=resolution,
        frame_height_mm=frame_height_mm
    )

    # Apply shape mask
    apply_shape_to_heightmap(z, shape=shape, min_thickness=min_th)

    stl = create_solid_lithophane(x, y, z)
    return stl


def apply_shape_to_heightmap(heightmap, shape="circle", min_thickness=0.8):
    h, w = heightmap.shape
    mask = shape_mask(h, w, shape)

    shaped = heightmap.copy()
    shaped[~mask] = min_thickness

    return shaped, mask
