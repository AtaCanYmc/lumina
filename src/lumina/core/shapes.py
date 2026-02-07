import numpy as np
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
        
        # Scale factor to fit the heart within the [-1, 1] box
        scale = 1.4  
        
        # Normalize coordinates to [-scale, scale]
        nx = ((x - cx) / (width / 2)) * scale
        
        # Fix Orientation: Removed the negative sign based on user feedback.
        # Original (inverted) had -((y-cy)...) which flipped it.
        # Now restoring to standard coordinate direction relative to grid.
        ny = ((y - cy) / (height / 2)) * scale
        
        # Classic implicit heart equation
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
            raise ValueError(f"Unsupported shape: {shape}")
