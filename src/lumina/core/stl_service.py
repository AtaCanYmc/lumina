import numpy as np
import cv2
from stl import mesh, Mesh


def add_frame_to_z(z, frame_mm, resolution: float = 5, extra_height_mm: float = 0) -> np.ndarray:
    """Adds a frame around the z matrix.

    Args:
        z (np.ndarray): Z matrix
        frame_mm (float): Frame size in mm
        resolution (int, optional): Image resolution in pixels per mm. Defaults to 5.
        extra_height_mm (int, optional): Extra height to add to frame. Defaults to 0.

    Returns:
        np.ndarray: Z matrix with frame
    """
    if frame_mm <= 0:
        return z

    frame_pxl = int(frame_mm * resolution)
    frame_height = np.max(z) + extra_height_mm
    new_shape = (z.shape[0] + 2 * frame_pxl, z.shape[1] + 2 * frame_pxl)
    z_framed = np.full(new_shape, frame_height)
    z_framed[frame_pxl:-frame_pxl, frame_pxl:-frame_pxl] = z
    return z_framed


def jpg_to_stl(
        image: np.ndarray,
        max_thick: float = 3.0,
        min_thick: float = 0.5,
        frame_thick_mm: float = 0.5,
        frame_height_mm: float = 0.0,
        resolution: int = 5,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Function to convert filename to stl with given width.

    Args:
        image (np.ndarray): Path to image file
        max_thick (float, optional): Maximum thickness in mm. Defaults to 3.0.
        min_thick (float, optional): Minimum thickness in mm. Defaults to 0.5.
        frame_thick_mm (float, optional): Frame around image in mm. Defaults to 0.5.
        frame_height_mm (float, optional): Frame height in mm. Defaults to 0.0.
        resolution (int, optional): Image resolution in pixels per mm. Defaults to 10.

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray]: x, y, z matrices
    """

    if len(image.shape) > 2:
        raise RuntimeError(f"Image shape {image.shape} is not supported. "
                           f"Only grayscale images are supported.")

    if resolution <= 0:
        raise ValueError("Resolution must be a positive integer.")

    if min_thick >= max_thick:
        raise ValueError("min_thick must be less than max_thick.")

    # Flip image vertically
    image = np.flipud(image)

    # Invert threshold for z matrix
    image = 1 - np.double(image)

    # Scale z matrix to desired max depth and add base height
    depth_mm = max_thick - min_thick
    offset_mm = min_thick
    z = image * depth_mm + offset_mm

    # Add a frame around the image
    z = add_frame_to_z(
        z=z,
        frame_mm=frame_thick_mm,
        resolution=resolution,
        extra_height_mm=frame_height_mm
    )

    # Add a thin back plane
    z_with_back = np.zeros([z.shape[0] + 2, z.shape[1] + 2])
    z_with_back[1:-1, 1:-1] = z
    z = z_with_back

    x1 = np.linspace(0, z.shape[1] / resolution, z.shape[1])
    y1 = np.linspace(0, z.shape[0] / resolution, z.shape[0])
    x, y = np.meshgrid(x1, y1)
    x = np.fliplr(x)
    return x, y, z


# ... (ShapeStrategy classes and shape_mask function remain unchanged) ...


def image_to_flat_stl(
        image: np.ndarray,
        max_th: float,
        min_th: float,
        frame_thick_mm: float,
        frame_height_mm: float = 0.0,
        resolution: int = 5,
        shape: str = "rect"
) -> Mesh:
    """Converts an image to an STL file path.

    Supported shapes:
        rect
        circle
        heart

    Args:
        image (np.ndarray): Input image
        max_th (float): Maximum thickness in mm
        min_th (float): Minimum thickness in mm
        frame_thick_mm (float): Frame size in mm
        frame_height_mm (float): Frame height in mm
        resolution (int): Image resolution in pixels per mm
        shape (str): Image shape

    Returns:
        Mesh
    """
    # 1. Generate base Z matrix (with rectangular frame padding if frame_thick > 0)
    x, y, z = jpg_to_stl(
        image=image,
        frame_thick_mm=frame_thick_mm,
        max_thick=max_th,
        min_thick=min_th,
        resolution=resolution,
        frame_height_mm=frame_height_mm
    )

    # 2. Determine inner image ROI
    # jpg_to_stl adds frame padding, then a 1px backplane border.
    # Total padding on each side = frame_pxl + 1
    
    frame_pxl = int(frame_thick_mm * resolution)
    total_pad = frame_pxl + 1
    
    # Calculate dimensions of the actual image area
    h, w = z.shape
    img_h = h - 2 * total_pad
    img_w = w - 2 * total_pad
    
    # Defensive check
    if img_h <= 0 or img_w <= 0:
        # Should not happen given valid inputs, but if frame is huge...
        # Fallback to full mask
        mask = np.ones(z.shape, dtype=bool)
    else:
        # 3. Create Shape Mask for the active image area
        strategy = ShapeFactory.get_strategy(shape)
        inner_mask = strategy.create_mask(img_h, img_w)
        
        # 4. Create Full Mask
        # By default, everything is masked OUT (False)
        full_mask_uint8 = np.zeros(z.shape, dtype=np.uint8)
        
        # Place the inner mask in the center
        # y_start = total_pad
        # x_start = total_pad
        # But wait, jpg_to_stl flips things? 
        # jpg_to_stl: x = np.fliplr(x). Z is from flipped image.
        # But the mask generation uses standard grid. 
        # Assuming centered shape, it should be fine.
        
        full_mask_uint8[total_pad:total_pad+img_h, total_pad:total_pad+img_w] = inner_mask.astype(np.uint8)
        
        if shape == "rect":
            # For Rect, we usually usually want the whole thing including the rectangular frame.
            # If we just leave it as inner_mask, the frame is cut off!
            # So for Rect, we want the mask to be True whereever there is valid Z?
            # Or just all True?
            # Let's say all True to keep default behavior which includes the frame.
            mask = np.ones(z.shape, dtype=bool)
        else:
            # For Shapes (Circle/Heart):
            # We want the Frame to follow the shape.
            
            if frame_thick_mm > 0:
                # Dilate the inner shape to create the frame
                # Kernel size: radius = frame_pxl. Diameter ~ 2*frame_pxl.
                # Use slightly larger to ensure coverage?
                # frame_pxl corresponds to the added padding thickness.
                # So we need to expand the mask by frame_pxl pixels.
                
                k_size = 2 * frame_pxl + 1
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size, k_size))
                
                # Dilate
                outer_mask = cv2.dilate(full_mask_uint8, kernel)
                
                # The final mask includes both inner shape and the dilated frame
                mask = outer_mask.astype(bool)
                
                # Note: The area between inner_mask and outer_mask is the "Frame".
                # The Z values there come from jpg_to_stl, which sets them to frame_height.
                # Because jpg_to_stl creates a rectangular block of frame_height, 
                # and our dilation is within that block (mostly), 
                # the frame will have the correct height.
                # Corner areas of the rect frame that are NOT covered by dilation will be masked out.
            else:
                # No frame
                mask = full_mask_uint8.astype(bool)
                
            # Apply shape mask to heightmap? 
            # We assume jpg_to_stl returns 'z' which works. 
            # But the inner part of 'z' might need strictly min_thickness for masked-out areas?
            # actually our mask handles the cutting.
            # But `apply_shape_to_heightmap` (previous step) was used to ensure
            # visual correctness in the heightmap itself if we weren't cutting.
            # Do we still need to modify Z values inside the ROI?
            # Previous logic:
            # z, _ = apply_shape_to_heightmap(z, shape=shape, min_thickness=min_th)
            # This applies to the WHOLE z. But z includes frame padding.
            # If we apply shape mask to the whole Z, it treats the whole Z (frame included) as the shape domain.
            # That's wrong if we want shape *inside* frame.
            
            # The previous approach (Step 1-3 of this task) was applying shape to the result of jpg_to_stl.
            # Start: Z includes frame.
            # Shape Mask: Applied to HxW.
            # Result: Circle cutout of the Frame+Image.
            # That's why the user saw "white plate" (if we didn't cut) or "rectangular frame pieces" (if we partially cut).
            
            # NOW: We construct the mask based on Image Only, then Frame follows it.
            # So we DON'T need `apply_shape_to_heightmap` on the global Z anymore!
            # The `mask` we just built handles everything.
            pass

    stl = create_solid_lithophane(x, y, z, mask=mask)
    return stl

    """Adds a frame around the z matrix.

    Args:x
        z (np.ndarray): Z matrix
        frame_mm (float): Frame size in mm
        resolution (int, optional): Image resolution in pixels per mm. Defaults to 5.
        extra_height_mm (int, optional): Extra height to add to frame. Defaults to 0.

    Returns:
        np.ndarray: Z matrix with frame
    """
    if frame_mm <= 0:
        return z

    frame_pxl = int(frame_mm * resolution)
    frame_height = np.max(z) + extra_height_mm
    new_shape = (z.shape[0] + 2 * frame_pxl, z.shape[1] + 2 * frame_pxl)
    z_framed = np.full(new_shape, frame_height)
    z_framed[frame_pxl:-frame_pxl, frame_pxl:-frame_pxl] = z
    return z_framed


def jpg_to_stl(
        image: np.ndarray,
        max_thick: float = 3.0,
        min_thick: float = 0.5,
        frame_thick_mm: float = 0.5,
        frame_height_mm: float = 0.0,
        resolution: int = 5,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Function to convert filename to stl with given width.

    Args:
        image (np.ndarray): Path to image file
        max_thick (float, optional): Maximum thickness in mm. Defaults to 3.0.
        min_thick (float, optional): Minimum thickness in mm. Defaults to 0.5.
        frame_thick_mm (float, optional): Frame around image in mm. Defaults to 0.5.
        frame_height_mm (float, optional): Frame height in mm. Defaults to 0.0.
        resolution (int, optional): Image resolution in pixels per mm. Defaults to 10.

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray]: x, y, z matrices
    """

    if len(image.shape) > 2:
        raise RuntimeError(f"Image shape {image.shape} is not supported. "
                           f"Only grayscale images are supported.")

    if resolution <= 0:
        raise ValueError("Resolution must be a positive integer.")

    if min_thick >= max_thick:
        raise ValueError("min_thick must be less than max_thick.")

    # Flip image vertically
    image = np.flipud(image)

    # Invert threshold for z matrix
    image = 1 - np.double(image)

    # Scale z matrix to desired max depth and add base height
    depth_mm = max_thick - min_thick
    offset_mm = min_thick
    z = image * depth_mm + offset_mm

    # Add a frame around the image
    z = add_frame_to_z(
        z=z,
        frame_mm=frame_thick_mm,
        resolution=resolution,
        extra_height_mm=frame_height_mm
    )

    # Add a thin back plane
    z_with_back = np.zeros([z.shape[0] + 2, z.shape[1] + 2])
    z_with_back[1:-1, 1:-1] = z
    z = z_with_back

    x1 = np.linspace(0, z.shape[1] / resolution, z.shape[1])
    y1 = np.linspace(0, z.shape[0] / resolution, z.shape[0])
    x, y = np.meshgrid(x1, y1)
    x = np.fliplr(x)
    return x, y, z


from abc import ABC, abstractmethod

class ShapeStrategy(ABC):
    @abstractmethod
    def create_mask(self, height: int, width: int) -> np.ndarray:
        pass

class RectShape(ShapeStrategy):
    def create_mask(self, height: int, width: int) -> np.ndarray:
        return np.ones((height, width), dtype=bool)

class CircleShape(ShapeStrategy):
    def create_mask(self, height: int, width: int) -> np.ndarray:
        y, x = np.ogrid[:height, :width]
        cx, cy = width / 2, height / 2
        # Normalize coordinates
        nx = (x - cx) / (width / 2)
        ny = (y - cy) / (height / 2)
        return nx ** 2 + ny ** 2 <= 1

class HeartShape(ShapeStrategy):
    def create_mask(self, height: int, width: int) -> np.ndarray:
        y, x = np.ogrid[:height, :width]
        cx, cy = width / 2, height / 2
        # Normalize coordinates. Note: Heart shape often looks better if we scale y slightly differently or shift it.
        # But keeping the original logic for now.
        nx = (x - cx) / (width / 2)
        ny = (y - cy) / (height / 2)
        # Inverting Y for the formula to match visual expectation if needed, 
        # but the original code used standard coordinates.
        # classic implicit heart equation: (x^2 + y^2 - 1)^3 - x^2 * y^3 = 0
        # NOTE: Original code had: (nx ** 2 + ny ** 2 - 1) ** 3 - nx ** 2 * ny ** 3
        # However, usually heart is upright if Y points up. In images, Y points down.
        # Because we flip image in jpg_to_stl (np.flipud), we might need to be careful.
        # But let's stick to the existing math for now to match `shape_mask` behavior.
        
        heart = (nx ** 2 + ny ** 2 - 1) ** 3 - nx ** 2 * ny ** 3
        return heart <= 0

class ShapeFactory:
    @staticmethod
    def get_strategy(shape: str) -> ShapeStrategy:
        if shape == "circle":
            return CircleShape()
        elif shape == "heart":
            return HeartShape()
        elif shape == "rect":
            return RectShape()
        else:
            # Default or raise error? The original raised ValueError
            raise ValueError(f"Unsupported shape: {shape}")


def shape_mask(height, width, shape="circle"):
    """
    Deprecated: Use ShapeStrategy classes instead.
    Maintained for backward compatibility if needed, using the new strategies.
    """
    strategy = ShapeFactory.get_strategy(shape)
    return strategy.create_mask(height, width)


def create_solid_lithophane(x, y, z, mask=None) -> mesh.Mesh:
    """Creates a solid flat lithophane STL file.

    Args:
        x (np.ndarray): X matrix
        y (np.ndarray): Y matrix
        z (np.ndarray): Z matrix
        mask (np.ndarray, optional): Boolean mask for valid vertices. Defaults to None.

    Returns:
        mesh.Mesh
    """
    rows, cols = z.shape
    faces = []

    # Vertices: Top and Bottom faces (Z and Z=0)
    vertices = np.vstack([
        np.column_stack([x.flatten(), y.flatten(), z.flatten()]),
        np.column_stack([x.flatten(), y.flatten(), np.zeros_like(z.flatten())])
    ])
    offset = rows * cols

    # Helper to check if a cell (quad) is valid
    # A cell at (r, c) is considered valid if all its 4 corners are inside the mask
    def is_valid_cell(r, c):
        if mask is None:
            return True
        # Check bounds just in case
        if r < 0 or r >= rows - 1 or c < 0 or c >= cols - 1:
            return False
        return (mask[r, c] and mask[r, c+1] and 
                mask[r+1, c] and mask[r+1, c+1])

    # FreeCAD logic for face creation
    for r in range(rows - 1):
        for c in range(cols - 1):
            if not is_valid_cell(r, c):
                continue

            lt = r * cols + c  # Sol-Üst
            rt = lt + 1  # Sağ-Üst
            lb = (r + 1) * cols + c  # Sol-Alt
            rb = lb + 1  # Sağ-Alt

            # Front face (Z+ direction)
            faces.append([lt, lb, rt])
            faces.append([rt, lb, rb])

            # Back face (Z- direction)
            faces.append([lt + offset, rt + offset, lb + offset])
            faces.append([rt + offset, rb + offset, lb + offset])

            # WALLS (Waterproof) - Check 4 neighbors
            
            # Left Wall (check if neighbor to left is invalid)
            if c == 0 or not is_valid_cell(r, c - 1):
                faces.append([lt, lt + offset, lb])
                faces.append([lb, lt + offset, lb + offset])
            
            # Right Wall (check if neighbor to right is invalid)
            if c == cols - 2 or not is_valid_cell(r, c + 1):
                faces.append([rt, rb, rt + offset])
                faces.append([rb, rb + offset, rt + offset])
            
            # Top Wall (check if neighbor above is invalid)
            if r == 0 or not is_valid_cell(r - 1, c):
                faces.append([lt, rt, lt + offset])
                faces.append([rt, rt + offset, lt + offset])
                
            # Bottom Wall (check if neighbor below is invalid)
            if r == rows - 2 or not is_valid_cell(r + 1, c):
                faces.append([lb, lb + offset, rb])
                faces.append([rb, lb + offset, rb + offset])

    litho_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        litho_mesh.v0[i] = vertices[f[0]]
        litho_mesh.v1[i] = vertices[f[1]]
        litho_mesh.v2[i] = vertices[f[2]]

    return litho_mesh


def image_to_flat_stl(
        image: np.ndarray,
        max_th: float,
        min_th: float,
        frame_thick_mm: float,
        frame_height_mm: float = 0.0,
        resolution: int = 5,
        shape: str = "rect"
) -> Mesh:
    """Converts an image to an STL file path.

    Supported shapes:
        rect
        circle
        heart

    Args:
        image (np.ndarray): Input image
        max_th (float): Maximum thickness in mm
        min_th (float): Minimum thickness in mm
        frame_thick_mm (float): Frame size in mm
        frame_height_mm (float): Frame height in mm
        resolution (int): Image resolution in pixels per mm
        shape (str): Image shape

    Returns:
        Mesh
    """
    x, y, z = jpg_to_stl(
        image=image,
        frame_thick_mm=frame_thick_mm,
        max_thick=max_th,
        min_thick=min_th,
        resolution=resolution,
        frame_height_mm=frame_height_mm
    )

    # Apply shape mask
    z, mask = apply_shape_to_heightmap(z, shape=shape, min_thickness=min_th)

    stl = create_solid_lithophane(x, y, z, mask=mask)
    return stl


def apply_shape_to_heightmap(heightmap, shape="circle", min_thickness=0.8):
    h, w = heightmap.shape
    # Use Factory/Strategy to get mask
    strategy = ShapeFactory.get_strategy(shape)
    mask = strategy.create_mask(h, w)

    shaped = heightmap.copy()
    shaped[~mask] = min_thickness

    return shaped, mask

