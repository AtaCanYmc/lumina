import numpy as np
from lumina.core.image_service import to_spiral


def test_to_spiral_output_shape():
    """Test that to_spiral returns an image of the same shape."""
    # Create a simple 100x100 grayscale image
    img = np.ones((100, 100), dtype=np.uint8) * 128
    
    result = to_spiral(img, lines=30, angle_step=0.1)
    
    assert result.shape == img.shape
    assert result.dtype == np.uint8


def test_to_spiral_white_background():
    """Test that the spiral has a white background."""
    img = np.ones((100, 100), dtype=np.uint8) * 128
    
    result = to_spiral(img, lines=30, angle_step=0.1)
    
    # Corners should be white (255) since spiral doesn't reach them
    assert result[0, 0] == 255
    assert result[0, 99] == 255
    assert result[99, 0] == 255
    assert result[99, 99] == 255


def test_to_spiral_has_lines():
    """Test that the spiral actually draws lines (not all white)."""
    img = np.ones((100, 100), dtype=np.uint8) * 128
    
    result = to_spiral(img, lines=30, angle_step=0.1)
    
    # There should be some non-white pixels (the spiral lines)
    assert np.any(result < 255)
