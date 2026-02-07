import numpy as np
from lumina.core.image_service import to_spiral


def test_to_spiral_output_shape():
    """Test that to_spiral returns an image of the same shape."""
    # Create a simple 100x100 grayscale image
    img = np.ones((100, 100), dtype=np.uint8) * 128
    
    result = to_spiral(img, lines=30, angle_step=0.1)
    
    assert result.shape[:2] == img.shape
    assert result.shape[2] == 4
    assert result.dtype == np.uint8


def test_to_spiral_transparent_background():
    """Test that the spiral has a transparent background."""
    img = np.ones((100, 100), dtype=np.uint8) * 128
    
    result = to_spiral(img, lines=30, angle_step=0.1)
    
    # Corners should be transparent (0, 0, 0, 0) since spiral doesn't reach them
    assert np.all(result[0, 0] == (0, 0, 0, 0))
    assert np.all(result[0, 99] == (0, 0, 0, 0))
    assert np.all(result[99, 0] == (0, 0, 0, 0))
    assert np.all(result[99, 99] == (0, 0, 0, 0))


def test_to_spiral_has_lines():
    """Test that the spiral actually draws lines (not all white)."""
    img = np.ones((100, 100), dtype=np.uint8) * 128
    
    result = to_spiral(img, lines=30, angle_step=0.1)
    
    # There should be some non-transparent pixels (the spiral lines)
    assert np.any(result[:, :, 3] > 0)
