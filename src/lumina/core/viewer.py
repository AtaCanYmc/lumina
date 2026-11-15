import base64
import json
import os
import tempfile
import webbrowser
from importlib.resources import files
from typing import Any

from stl import mesh


def get_viewer_template() -> str:
    """Loads the HTML template from package resources with local filesystem fallback."""
    try:
        return (
            files("lumina")
            .joinpath("templates", "viewer.html")
            .read_text(encoding="utf-8")
        )
    except Exception:
        template_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "templates", "viewer.html")
        )
        with open(template_path, encoding="utf-8") as f:
            return f.read()


def get_mesh_stats(mesh_obj: mesh.Mesh, density_g_cm3: float = 1.24) -> dict[str, Any]:
    """Calculates physical and geometric statistics for a 3D STL mesh.

    Args:
        mesh_obj: numpy-stl Mesh object.
        density_g_cm3: Material density in g/cm³ (default: 1.24 for PLA).

    Returns:
        dict containing facets, vertices, dimensions (width, height, depth),
        volume in cm³, and estimated weight in grams.
    """
    facets = len(mesh_obj.vectors)
    minx, maxx = float(mesh_obj.x.min()), float(mesh_obj.x.max())
    miny, maxy = float(mesh_obj.y.min()), float(mesh_obj.y.max())
    minz, maxz = float(mesh_obj.z.min()), float(mesh_obj.z.max())

    width = round(maxx - minx, 2)
    height = round(maxy - miny, 2)
    depth = round(maxz - minz, 2)

    try:
        vol_mm3, _, _ = mesh_obj.get_mass_properties()
        volume_mm3 = max(0.0, float(vol_mm3))
    except Exception:
        volume_mm3 = 0.0

    volume_cm3 = round(volume_mm3 / 1000.0, 2)
    weight_g = round(volume_cm3 * density_g_cm3, 2)

    return {
        "facets": facets,
        "width_mm": width,
        "height_mm": height,
        "depth_mm": depth,
        "min_z": round(minz, 2),
        "max_z": round(maxz, 2),
        "volume_cm3": volume_cm3,
        "weight_grams": weight_g,
    }


def generate_viewer_html(
    stl_path_or_bytes: str | bytes,
    title: str = "Lumina 3D Lithophane Viewer",
    mesh_stats: dict[str, Any] | None = None,
) -> str:
    """Generates a self-contained, interactive WebGL 3D viewer HTML page.

    Features:
      - Interactive Three.js OrbitControls (rotate, pan, zoom).
      - Dual rendering modes:
          * Backlit Lithophane: Subsurface scattering / physical light transmission simulation.
          * Solid Shaded: Matte 3D relief with directional lighting and shadows.
          * Wireframe: Mesh facet topology.
      - Light temperature controls (Warm 2700K, Neutral 4000K, Cool 6500K, or custom).
      - Light intensity, backlight distance, and absorption contrast sliders.
      - Real-time mesh statistics (dimensions, facets, estimated PLA weight).
      - Drag-and-drop support for loading any external STL files.
    """
    if isinstance(stl_path_or_bytes, bytes):
        stl_b64 = base64.b64encode(stl_path_or_bytes).decode("ascii")
        filename = "lithophane.stl"
    else:
        if not os.path.exists(stl_path_or_bytes):
            raise FileNotFoundError(f"STL file not found: {stl_path_or_bytes}")
        with open(stl_path_or_bytes, "rb") as f:
            stl_b64 = base64.b64encode(f.read()).decode("ascii")
        filename = os.path.basename(stl_path_or_bytes)

        if mesh_stats is None:
            try:
                m = mesh.Mesh.from_file(stl_path_or_bytes)
                mesh_stats = get_mesh_stats(m)
            except Exception:
                mesh_stats = None

    stats_json = json.dumps(mesh_stats) if mesh_stats else "{}"

    template = get_viewer_template()
    html_content = (
        template.replace("__TITLE__", title)
        .replace("__FILENAME__", filename)
        .replace("__STATS_JSON__", stats_json)
        .replace("__STL_B64__", stl_b64)
    )

    return html_content


def open_viewer(
    stl_path: str,
    output_html: str | None = None,
    open_browser: bool = True,
) -> str:
    """Renders the 3D viewer for an STL file and optionally opens it in the browser.

    Args:
        stl_path: Path to the target .stl file.
        output_html: Optional explicit path to save the generated HTML file.
                     If None, a temporary HTML file is generated.
        open_browser: Whether to open the generated HTML file in the default browser.

    Returns:
        Path to the generated HTML file.
    """
    html_content = generate_viewer_html(stl_path)

    if output_html is None:
        fd, output_html = tempfile.mkstemp(prefix="lumina_viewer_", suffix=".html")
        with open(fd, "w", encoding="utf-8") as f:
            f.write(html_content)
    else:
        out_dir = os.path.dirname(os.path.abspath(output_html))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(output_html, "w", encoding="utf-8") as f:
            f.write(html_content)

    if open_browser:
        webbrowser.open(f"file://{os.path.abspath(output_html)}")

    return output_html
