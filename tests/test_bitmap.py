import numpy as np
from lumina.core.image_service import to_monochrome
from lumina.core.bitmap_service import export_to_c_array, export_to_hex

def test_to_monochrome():
    # 2x2 Image: 
    # [ 50, 200 ]
    # [ 100, 150 ]
    # Threshold 128
    # Result should be:
    # [ 0, 1 ]
    # [ 0, 1 ]
    
    img = np.array([[50, 200], [100, 150]], dtype=np.uint8)
    mono = to_monochrome(img, threshold=128)
    
    expected = np.array([[0, 1], [0, 1]], dtype=np.uint8)
    np.testing.assert_array_equal(mono, expected)

def test_export_to_c_array():
    # 8x1 Bitmap: 1 0 1 0 1 0 1 0 -> 0xAA (170)
    bitmap = np.array([[1, 0, 1, 0, 1, 0, 1, 0]], dtype=np.uint8)
    c_code = export_to_c_array(bitmap, var_name="test_bmp")
    
    assert "0xAA" in c_code
    assert "const unsigned char test_bmp [] PROGMEM" in c_code
    assert "// Bitmap size: 8x1" in c_code

def test_export_to_hex():
    # 8x1 Bitmap: 1 0 1 0 1 0 1 0 -> AA
    bitmap = np.array([[1, 0, 1, 0, 1, 0, 1, 0]], dtype=np.uint8)
    hex_str = export_to_hex(bitmap)
    assert hex_str == "AA"
    
def test_export_to_hex_2rows():
    # 8x2 Bitmap:
    # 1 1 1 1 0 0 0 0 -> F0
    # 0 0 0 0 1 1 1 1 -> 0F
    
    bitmap = np.array([
        [1, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 1]
    ], dtype=np.uint8)
    
    hex_str = export_to_hex(bitmap)
    assert hex_str == "F00F"
