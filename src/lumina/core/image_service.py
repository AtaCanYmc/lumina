import os
import math

import cv2
import numpy as np

from ..utils.common_utils import generate_uuid_filename


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

    When `is_grayscale=True`, this function will read PNGs with
    IMREAD_UNCHANGED to detect an alpha channel. If present, fully-transparent
    pixels (alpha==0) are treated as white (255) in the returned grayscale
    image. This prevents transparent black from being interpreted as black and
    producing a full/solid lithophane plate.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")

    if is_grayscale:
        # Read unchanged so we can detect alpha channel for PNGs
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError(f"The image file is corrupted or in an unsupported format: {path}")

        # If PNG has alpha channel (BGRA)
        if img.ndim == 3 and img.shape[2] == 4:
            bgr = img[:, :, :3]
            alpha = img[:, :, 3]
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            gray = gray.astype(np.uint8)
            # Treat fully transparent pixels as white (minimum thickness)
            gray[alpha == 0] = 255
            return gray

        # Regular BGR color image
        if img.ndim == 3 and img.shape[2] == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Already grayscale
        if img.ndim == 2:
            return img

        raise ValueError(f"Unsupported image format for grayscale read: {path}")

    # Fallback: color read (no alpha preservation)
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"The image file is corrupted or in an unsupported format: {path}")
    return img


def to_monochrome(image: np.ndarray, threshold: int = 128) -> np.ndarray:
    """Converts a grayscale image to a 1-bit monochrome bitmap.

    Args:
        image (np.ndarray): Grayscale input image (0-255).
        threshold (int): Threshold value for binarization. Defaults to 128.

    Returns:
        np.ndarray: Binary image (0 or 1) of type uint8.
    """
    if len(image.shape) > 2:
        raise ValueError("Image must be grayscale (2D array).")

    # Apply threshold: pixels > threshold become 1, else 0
    # Note: For OLEDs, usually 1 is ON (light), 0 is OFF (dark).
    # In standard image processing, 255 is white (light), 0 is black (dark).
    # So: Pixel > Threshold -> White (1). Pixel <= Threshold -> Black (0).
    binary = (image > threshold).astype(np.uint8)
    return binary


def normalize_image(image: np.ndarray) -> np.ndarray:
    """ Normalize image to 0-1 range using min-max scaling.
        Args:
            image (np.ndarray): Image

        Returns:
            np.ndarray: Normalized image
    """
    min_val = np.min(image)
    max_val = np.max(image)

    if max_val == min_val:
        raise ValueError("Image has no contrast.")

    return (image - min_val) / (max_val - min_val)


def invert_image(image: np.ndarray) -> np.ndarray:
    """Inverts the image.

    Args:
        image (np.ndarray): Input image.

    Returns:
        np.ndarray: Inverted image.
    """
    return 1 - np.double(image)


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
    img = cv2.resize(img, new_shape, interpolation=cv2.INTER_AREA)
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
    img = cv2.resize(img, new_shape, interpolation=cv2.INTER_AREA)
    return img


def enhance_contrast(img: np.ndarray) -> np.ndarray:
    """Enhances the contrast of a grayscale image using CLAHE.
    Args:
        img (np.ndarray): Grayscale input image.
    Returns:
        np.ndarray: Contrast-enhanced image.
    """
    # 1. Grayscale force
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Normalize to uint8
    if img.dtype != np.uint8:
        min_val = np.min(img)
        max_val = np.max(img)

        if max_val == min_val:
            raise ValueError("Image has no contrast.")

        img = (img - min_val) / (max_val - min_val)
        img = (img * 255).astype(np.uint8)

    # 3. CLAHE uygula
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img = clahe.apply(img)

    # 4. tekrar float 0–1 aralığına al
    return img.astype(np.float32) / 255.0


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


def to_spiral(img, lines=60, angle_step=0.05) -> np.ndarray:
    """Creates a spiral image from an image.

    Args:
        img (np.ndarray): Input image.
        lines (int): Number of lines in the spiral. Defaults to 60.
        angle_step (float): Angle step for the spiral. Defaults to 0.05.

    Returns:
        np.ndarray: Spiral image.
    """
    h, w = img.shape
    center = (w // 2, h // 2)
    max_r = min(center)

    canvas = np.zeros((h, w, 4), dtype=np.uint8)

    theta = 0
    prev_pt = None
    black_pixel = (0, 0, 0, 255)

    while True:
        # r = (theta / 2pi) * (max_r / count of lines)
        r = (theta / (2 * math.pi)) * (max_r / lines)
        if r >= max_r:
            break

        x = int(center[0] + r * math.cos(theta))
        y = int(center[1] + r * math.sin(theta))

        if x < 0 or x >= w or y < 0 or y >= h:
            theta += angle_step
            continue

        thickness = int((255 - img[y, x]) / 50) + 1

        if prev_pt:
            cv2.line(
                canvas,
                prev_pt,
                (x, y),
                black_pixel,
                thickness,
                cv2.LINE_AA
            )

        prev_pt = (x, y)
        theta += angle_step

    return canvas
