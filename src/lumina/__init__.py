from stl import mesh

from src.lumina.core.image_service import *
from src.lumina.core.stl_service import *


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
    """ It processes the image, generates an STL file, and returns its path.

    Supported shapes:
        rect
        circle
        heart

    Args:
        image_path (str): Path to the input image.
        width_mm (float, optional): Target width in mm. Defaults to 100.0.
        height_mm (float, optional): Target height in mm. Defaults to 150.0.
        max_thickness (float, optional): Maximum thickness in mm (black areas). Defaults to 3.0.
        min_thickness (float, optional): Minimum thickness in mm (white areas). Defaults to 0.5.
        frame_thick_mm (float, optional): Frame thickness in mm. Defaults to 1.0.
        frame_height_mm (float, optional): Frame height in mm (0 for same height as images max point). Defaults to 2.0.
        resolution (int, optional): Image resolution in pixels per mm. Defaults to 5.
        enhance (bool, optional): Enhance image. Defaults to False.

    Returns:
        mesh.Mesh: Generated STL mesh.
    """
    img = read_image(image_path, is_grayscale=True)
    img = normalize_image(img)

    if enhance:
        img = enhance_contrast(img)

    if frame_thick_mm > 0:
        width_mm -= 2 * frame_thick_mm
        height_mm -= 2 * frame_thick_mm

    img = resize_image(
        img=img,
        width=width_mm,
        height=height_mm,
        resolution=resolution
    )

    stl_mesh = image_to_flat_stl(
        image=img,
        max_th=max_thickness,
        min_th=min_thickness,
        frame_thick_mm=frame_thick_mm,
        frame_height_mm=frame_height_mm,
        resolution=resolution,
        shape=shape
    )

    return stl_mesh


def shaped_lithophane(
        image_path: str,
        shape: str = "rect",
        size_mm: float = 100.0,
        max_thickness: float = 3.0,
        min_thickness: float = 0.5,
        resolution: int = 5,
        enhance: bool = False,
) -> mesh.Mesh:
    """
    Generates a shaped lithophane mesh.

    Supported shapes:
        rect
        circle
        heart
    """

    img = read_image(image_path, is_grayscale=True)

    if enhance:
        img = enhance_contrast(img)

    # Square base for shapes
    img = resize_image(
        img=img,
        width=size_mm,
        height=size_mm,
        resolution=resolution
    )

    # Generate base lithophane matrices
    x, y, z = jpg_to_stl(
        image=img,
        max_thick=max_thickness,
        min_thick=min_thickness,
        frame_thick_mm=0.0,
        resolution=resolution
    )


    # Create mesh
    stl_mesh = create_solid_lithophane(x, y, z)
    return stl_mesh
