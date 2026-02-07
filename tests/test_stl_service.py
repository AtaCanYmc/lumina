import numpy as np
import pytest
from lumina.core.stl_service import (
    shape_mask,
    apply_shape_to_heightmap,
    image_to_flat_stl,
    jpg_to_stl
)

def test_shape_mask_circle():
    height, width = 100, 100
    mask = shape_mask(height, width, "circle")
    assert mask.shape == (height, width)
    # Center should be True
    assert mask[50, 50] == True
    # Corners should be False
    assert mask[0, 0] == False
    assert mask[0, 99] == False
    assert mask[99, 0] == False
    assert mask[99, 99] == False

def test_shape_mask_heart():
    height, width = 100, 100
    mask = shape_mask(height, width, "heart")
    assert mask.shape == (height, width)
    # Center somewhat should be True (heart shape varies but usually covers center)
    assert mask[50, 50] == True
    # Corners should be False
    assert mask[0, 0] == False

def test_apply_shape_to_heightmap():
    heightmap = np.ones((100, 100)) * 10.0
    min_thickness = 1.0
    shaped, mask = apply_shape_to_heightmap(heightmap, "circle", min_thickness)
    
    assert shaped.shape == heightmap.shape
    # Check that masked out areas have min_thickness
    assert shaped[0, 0] == min_thickness
    # Check that center area retains original height
    assert shaped[50, 50] == 10.0

def test_image_to_flat_stl_integration():
    # Create a dummy image
    image = np.zeros((100, 100), dtype=np.uint8)
    image[25:75, 25:75] = 255 # White square in middle
    
    # This should run without error
    mesh = image_to_flat_stl(
        image=image,
        max_th=3.0,
        min_th=0.5,
        frame_thick_mm=0.0,
        resolution=1,
        shape="circle"
    )
    assert mesh is not None
    # We can't easily check the mesh content for shape without complex logic, 
    # but we can verify it generated valid mesh data.
    assert len(mesh.points) > 0




def test_image_to_flat_stl_mesh_cutout():
    """Verify that using a shape reduces the mesh size (cuts vertices/faces)."""
    image = np.zeros((100, 100), dtype=np.uint8)
    
    # Generate RECT mesh
    mesh_rect = image_to_flat_stl(
        image=image, max_th=3.0, min_th=0.5, frame_thick_mm=0, resolution=1, shape="rect"
    )
    
    # Generate CIRCLE mesh
    mesh_circle = image_to_flat_stl(
        image=image, max_th=3.0, min_th=0.5, frame_thick_mm=0, resolution=1, shape="circle"
    )
    
    # Rect mesh should be full grid.
    # Circle mesh should be smaller (approx pi/4 of rect area).
    # Being conservative, it should definitely be smaller.
    
    print(f"Rect Vectors: {len(mesh_rect.vectors)}")
    print(f"Circle Vectors: {len(mesh_circle.vectors)}")
    
    assert len(mesh_circle.vectors) < len(mesh_rect.vectors), "Circle mesh should have fewer faces than Rect mesh"
    
    # Rough check of ratio (should be around 0.78 for circle vs square, 
    # but walls add some faces, backplane is double, etc.)
    # Just asserting it's substantially smaller is enough to prove "cutting" happens.
    ratio = len(mesh_circle.vectors) / len(mesh_rect.vectors)
    assert ratio < 0.9, f"Expected ratio < 0.9, got {ratio}"

def test_image_to_flat_stl_frame_generation():
    """Verify that a shaped frame adds to the mesh size and has correct height."""
    image = np.zeros((100, 100), dtype=np.uint8)
    
    # Generate CIRCLE mesh WITHOUT frame
    mesh_no_frame = image_to_flat_stl(
        image=image, max_th=3.0, min_th=0.5, frame_thick_mm=0, resolution=1, shape="circle"
    )
    
    # Generate CIRCLE mesh WITH frame
    # frame_thick_mm=5 -> 5 pixels padding
    mesh_frame = image_to_flat_stl(
        image=image, max_th=3.0, min_th=0.5, frame_thick_mm=5, resolution=1, shape="circle"
    )
    
    # Frame adds area around the circle, so mesh should have more faces.
    print(f"No Frame Vectors: {len(mesh_no_frame.vectors)}")
    print(f"With Frame Vectors: {len(mesh_frame.vectors)}")
    
    assert len(mesh_frame.vectors) > len(mesh_no_frame.vectors), "Frame should add faces to the mesh"
    
    # Check Max Z
    # With frame, max Z should be higher?
    # jpg_to_stl: frame_height = np.max(z) + extra_height_mm
    # defaulting extra_height_mm=0.
    # So frame height = max image height.
    # If image is black (0), max thickness is 3.0.
    # So frame is at 3.0.
    # But wait, max Z in mesh_no_frame is also 3.0.
    # Let's check min Z?
    # No, frame is high.
    
    # If we set frame_height_mm=2.0 (extra)
    mesh_frame_high = image_to_flat_stl(
        image=image, max_th=3.0, min_th=0.5, frame_thick_mm=5, frame_height_mm=2.0, resolution=1, shape="circle"
    )
    
    z_values = mesh_frame_high.points[:, [2, 5, 8]].flatten()
    max_z = np.max(z_values)
    
    # Max Z should be approx 3.0 + 2.0 = 5.0
    assert max_z > 4.9, f"Expected max Z to be around 5.0, got {max_z}"




