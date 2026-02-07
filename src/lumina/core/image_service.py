import os
from typing import Any

import cv2
import numpy as np
from numpy import ndarray

from src.lumina.utils.common_utils import generate_uuid_filename


def bytes_to_image(image_bytes: bytes, is_grayscale: bool) -> np.ndarray:
    """Converts image bytes to a color numpy array.

    Args:
        image_bytes (bytes): Image in bytes.
        is_grayscale (bool): Whether to load the image in grayscale.

    Returns:
        np.ndarray: Image as a numpy array.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    color = cv2.IMREAD_GRAYSCALE if is_grayscale else cv2.IMREAD_COLOR
    img = cv2.imdecode(nparr, color)
    if img is None:
        raise ValueError("Image could not be decoded.")
    return img


def read_image(path: str, is_grayscale: bool) -> np.ndarray:
    """
    Reads the image at the given path and returns it as a numpy array.

    Args:
        path (str): Path to the image.
        is_grayscale (bool): Whether to load the image in grayscale.

    Returns:
        np.ndarray: Image as a numpy array.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")

    color_mode = cv2.IMREAD_GRAYSCALE if is_grayscale else cv2.IMREAD_COLOR
    img = cv2.imread(path, color_mode)

    if img is None:
        raise ValueError(f"The image file is corrupted or in an unsupported format.: {path}")

    return img


def crop_to_mask(image: np.ndarray, mask) -> tuple[ndarray[tuple[Any, ...], Any], Any]:
    coords = np.argwhere(mask)

    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1

    return image[y0:y1, x0:x1], mask[y0:y1, x0:x1]


def normalize_image(image: np.ndarray) -> np.ndarray:
    """ Normalizes the image
        Args:
            image (np.ndarray): Image

        Returns:
            np.ndarray: Normalized image
    """
    max_val = np.max(image)
    if max_val == 0:
        raise ValueError("Image is completely black or invalid.")
    return image / max_val


def resize_image(
        img: np.ndarray,
        width: float,
        height: float,
        resolution: int = 10
) -> np.ndarray:
    """
    Resizes the image to the specified width and height in mm.

    Args:
        img (np.ndarray): Input image.
        width (float): Target width in mm.
        height (float): Target height in mm.
        resolution (int): Pixels per mm resolution.

    Returns:
        np.ndarray: Resized image.
    """
    target_w = int(width * resolution)
    target_h = int(height * resolution)
    z_dim = img.shape[2] if len(img.shape) == 3 else 1
    new_shape = (target_w, target_h, z_dim) if z_dim > 1 \
        else (target_w, target_h)
    img = cv2.resize(img, new_shape)
    return img


def scale_image(img: np.ndarray, width_mm: int = 100, resolution: int = 10) -> np.ndarray:
    """
    Scales image to given width in mm with given resolution in pixel/mm.

    Args:
        img (np.ndarray): Image to scale
        width_mm (int, optional): Width of image in mm. Defaults to 100.
        resolution (int, optional): Resolution in pixels per mm. Defaults to 10.

    Returns:
        np.ndarray: Scaled image
    """
    y_dim = img.shape[0]
    x_dim = img.shape[1]
    z_dim = img.shape[2] if len(img.shape) == 3 else 1
    scale = width_mm * resolution / x_dim
    new_shape = (int(y_dim * scale), int(x_dim * scale), z_dim) if z_dim > 1 \
        else (int(y_dim * scale), int(x_dim * scale))
    img = cv2.resize(img, new_shape)
    return img


def enhance_contrast(img: np.ndarray) -> np.ndarray:
    """Enhances the contrast of a grayscale image using CLAHE.
    Args:
        img (np.ndarray): Grayscale input image.
    Returns:
        np.ndarray: Contrast-enhanced image.
    """
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(img)


def rotate_image(img: np.ndarray, angle: float) -> np.ndarray:
    """Rotates the image by the specified angle.

    Args:
        img (np.ndarray): Input image.
        angle (float): Angle in degrees.

    Returns:
        np.ndarray: Rotated image.
    """
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, rotation_matrix, (w, h))
    return rotated


def show_image_window(window_name: str, img: np.ndarray) -> None:
    """Displays the image in a window for debugging purposes.

    Args:
        window_name (str): Name of the window.
        img (np.ndarray): Image to display.
    """
    cv2.imshow(window_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def save_image_to_file(img: np.ndarray, path: str, extension: str) -> str:
    """Saves the image to a file.

    Args:
        img (np.ndarray): Image to save.
        path (str): Directory path to save the image.
        extension (str): File extension (e.g., 'jpg', 'png').

    Returns:
        str: Path to the saved image file.
    """
    file_path = generate_uuid_filename(path, extension)
    cv2.imwrite(file_path, img)
    return file_path


def remove_background(img: np.ndarray, threshold: int = 250) -> np.ndarray:
    """Removes white background from the image.

    Args:
        img (np.ndarray): Input image.
        threshold (int): Threshold value to consider as background.

    Returns:
        np.ndarray: Image with background removed.
    """
    if len(img.shape) == 3 and img.shape[2] == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    result = cv2.bitwise_and(img, img, mask=mask)
    return result
