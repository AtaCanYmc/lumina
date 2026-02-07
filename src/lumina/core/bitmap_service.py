import numpy as np
import os


def export_to_c_array(bitmap: np.ndarray, var_name: str = "bitmap_data") -> str:
    """Exports a bitmap to a C array string (column-major or row-major).

    For SSD1306 (horizontal addressing), we typically pack 8 pixels into a byte row-wise.
    Structure:
    Byte 0: (x0,y0), (x1,y0), ... (x7,y0) -> MSB first or LSB first depends on controller.
    Most common for GFX libs (Adafruit_GFX) is row-major, MSB-first?
    Actually Adafruit_GFX uses row-major, top-left pixel is MSB of first byte.

    Args:
        bitmap (np.ndarray): 0/1 bitmap.
        var_name (str): Variable name for C array.

    Returns:
        str: C header file content.
    """
    height, width = bitmap.shape
    
    # Pack bits into bytes
    # Pad width to multiple of 8 if needed (though usually we expect valid inputs)
    # We'll flatten row by row.
    
    # Example: row 0: 1 0 1 0 1 0 1 0 -> 0xAA
    
    bytes_list = []
    
    for y in range(height):
        row_bytes = []
        byte_val = 0
        for x in range(width):
            bit = bitmap[y, x]
            # Adafruit GFX: MSB first
            # x%8 == 0 -> bit 7 (0x80)
            # x%8 == 1 -> bit 6 (0x40)
            shift = 7 - (x % 8)
            if bit:
                byte_val |= (1 << shift)
            
            if (x % 8) == 7 or x == width - 1:
                row_bytes.append(byte_val)
                byte_val = 0
                
        bytes_list.extend(row_bytes)
    
    # Format as C array
    hex_values = [f"0x{b:02X}" for b in bytes_list]
    
    # Wrap lines for readability
    lines = []
    chunk_size = 12 # 12 bytes per line
    for i in range(0, len(hex_values), chunk_size):
        chunk = hex_values[i:i + chunk_size]
        lines.append(", ".join(chunk))
        
    c_array_body = ",\n  ".join(lines)
    
    header = f"// Bitmap size: {width}x{height}\n"
    header += f"const unsigned char {var_name} [] PROGMEM = {{\n"
    header += f"  {c_array_body}\n"
    header += "};\n"
    
    return header


def export_to_hex(bitmap: np.ndarray) -> str:
    """Exports bitmap as a raw hex string."""
    # Similar packing logic, but just one long string
    # Re-use export_to_c_array logic but minimal
    # Or just return similar to above without C syntax.
    
    height, width = bitmap.shape
    hex_str = ""
    
    for y in range(height):
        byte_val = 0
        for x in range(width):
            bit = bitmap[y, x]
            shift = 7 - (x % 8)
            if bit:
                byte_val |= (1 << shift)
            
            if (x % 8) == 7 or x == width - 1:
                hex_str += f"{byte_val:02X}"
                byte_val = 0
                
    return hex_str


def write_hex_to_file(hex_str: str, file_path: str, file_name: str) -> str:
    """Writes a hex string to a file.

    Args:
        hex_str (str): Hex string to write.
        file_path (str): Path to file to write to.
        file_name (str): Name of the file to write to.

    Returns:
        str: Path to the file that was written to.
    """
    write_path = os.path.join(file_path, file_name)
    with open(write_path, "w") as f:
        f.write(hex_str)
    return write_path