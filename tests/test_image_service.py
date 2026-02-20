import os
import tempfile

import cv2
import numpy as np
import pytest

from lumina.core.image_service import (
    enhance_contrast,
    normalize_image,
    read_image,
    to_spiral,
)


def test_read_image_png_alpha_treated_as_white():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "alpha.png")
        # Create a 10x10 BGRA image, set one corner fully transparent
        h, w = 10, 10
        bgra = np.zeros((h, w, 4), dtype=np.uint8)
        bgra[:, :, :3] = 50  # dark gray color
        bgra[0, 0, 3] = 0  # fully transparent
        bgra[:, :, 3] = 255
        bgra[0, 0, 3] = 0
        cv2.imwrite(path, bgra)

        gray = read_image(path, is_grayscale=True)
        assert gray.shape == (h, w)
        # Transparent pixel should be white (255)
        assert gray[0, 0] == 255


def test_read_image_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_image("/non/existent/path.png", is_grayscale=True)


def test_normalize_image_raises_on_constant_image():
    img = np.ones((5, 5), dtype=np.uint8) * 42
    with pytest.raises(ValueError):
        normalize_image(img)


def test_enhance_contrast_returns_float32_unit_range():
    # Create a low-contrast uint8 image
    img = np.linspace(10, 40, 100, dtype=np.uint8).reshape((10, 10))
    out = enhance_contrast(img)
    assert out.dtype == np.float32
    assert out.min() >= 0.0
    assert out.max() <= 1.0


def test_to_spiral_small_image():
    img = np.ones((20, 20), dtype=np.uint8) * 128
    out = to_spiral(img, lines=10, angle_step=0.1)
    assert out.shape == (20, 20, 4)
    # Some transparency expected in corners
    assert np.all(out[0, 0] == (0, 0, 0, 0)) or np.all(out[0, -1] == (0, 0, 0, 0))
