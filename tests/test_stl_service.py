import numpy as np
from lumina.core.stl_service import (
    shape_mask,
    apply_shape_to_heightmap,
    image_to_flat_stl
)

def test_shape_mask_circle():
    height, width = 100, 100
    mask = shape_mask(height, width, "circle")
    assert mask.shape == (height, width)
    # Center should be True
    assert mask[50, 50]
    # Corners should be False
    assert not mask[0, 0]
    assert not mask[0, 99]
    assert not mask[99, 0]
    assert not mask[99, 99]

def test_shape_mask_heart():
    height, width = 100, 100
    mask = shape_mask(height, width, "heart")
    assert mask.shape == (height, width)
    # Center somewhat should be True (heart shape varies but usually covers center)
    assert mask[50, 50]
    # Corners should be False
    assert not mask[0, 0]

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
    
    z_values = mesh_frame_high.points[:, [2, 5, 8]].flatten()
    max_z = np.max(z_values)
    
    # Max Z should be approx 3.0 + 2.0 = 5.0
    assert max_z > 4.9, f"Expected max Z to be around 5.0, got {max_z}"

def test_image_to_flat_stl_frame_height_on_white_image():
    """
    Verify that the shaped frame has high Z even if the underlying image is low (white).
    This reproduces the bug where frame overlaps with image corners.
    """
    # White image -> Low Z (min_thick).
    # IMPORTANT: jpg_to_stl expects normalized image (0..1).
    image = np.ones((100, 100), dtype=np.float64)
    
    # Circle shape, Frame thick 5mm
    # min_th=0.5. Frame should be HIGH (max_th + extra? or just max_th?)
    # usually frame height is max_z (from image) + extra. Note: jpg_to_stl logic.
    # If image is white, max_z of image is 0.5. 
    # But jpg_to_stl might frame it at 0.5? 
    # Let's check jpg_to_stl: frame_height = np.max(z) + extra_height_mm.
    # If image is all 0.5, then frame is 0.5.
    # That's not good for a frame usually? Frame is usually "thickest part".
    # Wait, jpg_to_stl takes 'max_thick' processing argument but Z depends on Image.
    # If image is faint, Z is low.
    
    # But usually a frame is meant to stand out? 
    # Or at least be at the "Frame Height" level.
    # Let's explicitly ask for extra height.
    
    extra_h = 2.0
    mesh_obj = image_to_flat_stl(
        image=image, 
        max_th=3.0, min_th=0.5, 
        frame_thick_mm=5, frame_height_mm=extra_h, 
        resolution=1, shape="circle"
    )
    
    # The frame should be at least at Z = (image_max_z + extra_h).
    # Since image is flat 0.5, frame should be 2.5.
    
    # We inspect points.
    zs = mesh_obj.points[:, [2, 5, 8]].flatten()
    
    # The frame part should have Z ~ 2.5.
    # The image part (center) should have Z ~ 0.5.
    
    # If the bug exists, the "corners" (which are Frame now) will be Z ~ 0.5 (image level)
    # instead of Z ~ 2.5 (frame level).
    
    max_z = np.max(zs)
    
    assert max_z > 2.4, f"Frame should be high (approx 2.5), but max Z is {max_z}"





