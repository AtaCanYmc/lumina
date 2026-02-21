from pathlib import Path

import cv2

from lumina import flat_lithophane, generate_spiral_betty_png

ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / "assets" / "images"
STL_DIR = ROOT / "assets" / "stl"
STL_DIR.mkdir(parents=True, exist_ok=True)

img_path = str(IMG_DIR / "example_input.jpg")
spiral_out = IMG_DIR / "spiral_test_output.png"

results = []

# 1) Default flat lithophane (rect)
try:
    m = flat_lithophane(img_path, resolution=5)
    out = STL_DIR / "test_flat_rect.stl"
    m.save(str(out))
    results.append(("flat_rect", out))
    print("Wrote", out)
except Exception as e:
    print("flat_rect failed:", e)

# 2) Circle shape
try:
    m = flat_lithophane(
        img_path, resolution=5, shape="circle", width_mm=100, height_mm=100
    )
    out = STL_DIR / "test_flat_circle.stl"
    m.save(str(out))
    results.append(("flat_circle", out))
    print("Wrote", out)
except Exception as e:
    print("flat_circle failed:", e)

# 3) Heart shape
try:
    m = flat_lithophane(
        img_path, resolution=5, shape="heart", width_mm=100, height_mm=100
    )
    out = STL_DIR / "test_flat_heart.stl"
    m.save(str(out))
    results.append(("flat_heart", out))
    print("Wrote", out)
except Exception as e:
    print("flat_heart failed:", e)

# 4) Enhanced image
try:
    m = flat_lithophane(img_path, resolution=5, enhance=True)
    out = STL_DIR / "test_flat_enhanced.stl"
    m.save(str(out))
    results.append(("flat_enhanced", out))
    print("Wrote", out)
except Exception as e:
    print("flat_enhanced failed:", e)

# 5) Normalized image
try:
    m = flat_lithophane(img_path, resolution=5, normalize=True)
    out = STL_DIR / "test_flat_normalized.stl"
    m.save(str(out))
    results.append(("flat_normalized", out))
    print("Wrote", out)
except Exception as e:
    print("flat_normalized failed:", e)

# 6) Spiral generator
try:
    s = generate_spiral_betty_png(
        img_path, radius_mm=50, resolution=5, lines=60, angle_step=0.02
    )
    cv2.imwrite(str(spiral_out), s)
    results.append(("spiral_png", spiral_out))
    print("Wrote", spiral_out)
except Exception as e:
    print("spiral_png failed:", e)

# Summary
print("\nSummary of generated files:")
for name, path in results:
    print(
        name,
        "-",
        path,
        "- exists=",
        path.exists(),
        "size=",
        path.stat().st_size if path.exists() else "n/a",
    )

print("\nDone")
