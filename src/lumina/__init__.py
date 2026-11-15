# x-release-please-version
__version__ = "1.1.0"

import numpy as np
from stl import mesh

from .core.image_service import (
    enhance_contrast,
    normalize_image,
    read_image,
    resize_image,
    to_spiral,
)
from .core.stl_service import image_to_flat_stl


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
    """It processes the image, generates an STL file, and returns its path.

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
        normalize (bool, optional): Normalize image. Defaults to False.
        shape   (str, optional): Mesh shape Defaults to rect.

    Returns:
        mesh.Mesh: Generated STL mesh.
    """
    if width_mm <= 0 or height_mm <= 0:
        raise ValueError("width_mm and height_mm must be positive numbers.")
    if resolution <= 0:
        raise ValueError("resolution must be a positive number.")
    if frame_thick_mm < 0:
        raise ValueError("frame_thick_mm cannot be negative.")
    if min_thickness < 0:
        raise ValueError("min_thickness cannot be negative.")
    if min_thickness >= max_thickness:
        raise ValueError("min_thickness must be less than max_thickness.")
    if frame_thick_mm > 0 and (
        width_mm <= 2 * frame_thick_mm or height_mm <= 2 * frame_thick_mm
    ):
        raise ValueError(
            f"Frame thickness ({frame_thick_mm} mm) is too large for image dimensions "
            f"({width_mm}x{height_mm} mm). Inner area must be greater than zero."
        )

    img = read_image(image_path, is_grayscale=True)

    if normalize:
        img = normalize_image(img)

    if enhance:
        img = enhance_contrast(img)

    if frame_thick_mm > 0:
        width_mm -= 2 * frame_thick_mm
        height_mm -= 2 * frame_thick_mm

    img = resize_image(img=img, width=width_mm, height=height_mm, resolution=resolution)

    stl_mesh = image_to_flat_stl(
        image=img,
        max_th=max_thickness,
        min_th=min_thickness,
        frame_thick_mm=frame_thick_mm,
        frame_height_mm=frame_height_mm,
        resolution=resolution,
        shape=shape,
    )

    return stl_mesh


def generate_spiral_betty_png(
    image_path: str,
    radius_mm: float = 100.0,
    resolution: int = 5,
    lines: int = 30,
    angle_step: float = 0.05,
) -> np.ndarray:
    """Generates a spiral betty from an image.

    Args:
        image_path (str): Path to the input image.
        radius_mm (float, optional): Target radius in mm. Defaults to 100.0.
        resolution (int, optional): Image resolution in pixels per mm. Defaults to 5.
        lines (int, optional): Number of lines. Defaults to 30.
        angle_step (float, optional): Angle step. Defaults to 0.05.

    Returns:
        np.ndarray: Generated spiral betty.
    """
    if radius_mm <= 0:
        raise ValueError("radius_mm must be a positive number.")
    if resolution <= 0:
        raise ValueError("resolution must be a positive number.")
    if lines <= 0:
        raise ValueError("lines must be a positive integer.")
    if angle_step <= 0:
        raise ValueError("angle_step must be a positive number.")

    img = read_image(image_path, is_grayscale=True)

    img = resize_image(
        img=img, width=radius_mm * 2, height=radius_mm * 2, resolution=resolution
    )

    return to_spiral(img, lines=lines, angle_step=angle_step)
