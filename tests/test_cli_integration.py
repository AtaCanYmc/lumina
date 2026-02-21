from pathlib import Path

import cv2
from click.testing import CliRunner
from stl import mesh

from lumina.cli import cli

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "assets" / "images" / "example_input.jpg"


def test_cli_flat_creates_stl(tmp_path):
    runner = CliRunner()
    out_stl = tmp_path / "out_flat.stl"

    result = runner.invoke(
        cli,
        [
            "flat",
            str(INPUT),
            "--output",
            str(out_stl),
            "--width",
            "80",
            "--height",
            "120",
            "--resolution",
            "3",
            "--shape",
            "rect",
        ],
    )

    assert result.exit_code == 0, f"CLI failed: {result.output}"
    assert out_stl.exists(), "STL output not created"
    assert out_stl.stat().st_size > 0, "STL output is empty"

    # Load mesh and assert triangles > 0
    m = mesh.Mesh.from_file(str(out_stl))
    assert len(m.vectors) > 0


def test_cli_spiral_creates_png(tmp_path):
    runner = CliRunner()
    out_png = tmp_path / "out_spiral.png"

    result = runner.invoke(
        cli,
        [
            "spiral",
            str(INPUT),
            "--output",
            str(out_png),
            "--radius",
            "40",
            "--resolution",
            "3",
            "--lines",
            "40",
            "--angle-step",
            "0.03",
        ],
    )

    assert result.exit_code == 0, f"CLI failed: {result.output}"
    assert out_png.exists(), "PNG output not created"
    img = cv2.imread(str(out_png), cv2.IMREAD_UNCHANGED)
    assert img is not None, "PNG could not be read"
    assert img.size > 0
