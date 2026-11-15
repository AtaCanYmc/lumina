import os
from unittest.mock import patch

from click.testing import CliRunner

from lumina import flat_lithophane
from lumina.cli import cli
from lumina.core.viewer import generate_viewer_html, get_mesh_stats, open_viewer


def test_get_mesh_stats(tmp_path):
    img_path = "assets/images/example_input.jpg"
    m = flat_lithophane(img_path, width_mm=40, height_mm=40, resolution=2)
    stats = get_mesh_stats(m)

    assert stats["facets"] > 0
    assert stats["width_mm"] > 0
    assert stats["height_mm"] > 0
    assert stats["depth_mm"] > 0
    assert stats["volume_cm3"] > 0
    assert stats["weight_grams"] > 0


def test_generate_viewer_html_from_file(tmp_path):
    stl_path = tmp_path / "model.stl"
    m = flat_lithophane(
        "assets/images/example_input.jpg", width_mm=30, height_mm=30, resolution=2
    )
    m.save(str(stl_path))

    html = generate_viewer_html(str(stl_path))
    assert "<!DOCTYPE html>" in html
    assert "three" in html
    assert "OrbitControls" in html
    assert "STLLoader" in html
    assert "LithophaneShader" in html
    assert "model.stl" in html


def test_generate_viewer_html_from_bytes():
    raw_data = b"solid test\nendsolid test"
    html = generate_viewer_html(raw_data)
    assert "<!DOCTYPE html>" in html
    assert "Lithophane Viewport" in html


def test_generate_viewer_html_file_not_found():
    import pytest

    with pytest.raises(FileNotFoundError):
        generate_viewer_html("nonexistent_path_12345.stl")


def test_open_viewer_creates_file(tmp_path):
    stl_path = tmp_path / "model.stl"
    out_html = tmp_path / "preview.html"
    m = flat_lithophane(
        "assets/images/example_input.jpg", width_mm=30, height_mm=30, resolution=2
    )
    m.save(str(stl_path))

    result_path = open_viewer(
        str(stl_path), output_html=str(out_html), open_browser=False
    )
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0


def test_open_viewer_tempfile(tmp_path):
    stl_path = tmp_path / "model.stl"
    m = flat_lithophane(
        "assets/images/example_input.jpg", width_mm=30, height_mm=30, resolution=2
    )
    m.save(str(stl_path))

    result_path = open_viewer(str(stl_path), open_browser=False)
    assert os.path.exists(result_path)
    assert result_path.endswith(".html")
    # Clean up temp file
    if os.path.exists(result_path):
        os.remove(result_path)


def test_cli_view_command(tmp_path):
    runner = CliRunner()
    stl_path = tmp_path / "test.stl"
    out_html = tmp_path / "out.html"
    m = flat_lithophane(
        "assets/images/example_input.jpg", width_mm=30, height_mm=30, resolution=2
    )
    m.save(str(stl_path))

    result = runner.invoke(
        cli, ["view", str(stl_path), "-o", str(out_html), "--no-browser"]
    )
    assert result.exit_code == 0
    assert "3D Viewport HTML ready at:" in result.output
    assert out_html.exists()


def test_cli_flat_with_preview_flag(tmp_path):
    runner = CliRunner()
    out_stl = tmp_path / "flat_preview.stl"

    with patch("webbrowser.open") as mock_open:
        result = runner.invoke(
            cli,
            [
                "flat",
                "assets/images/example_input.jpg",
                "-o",
                str(out_stl),
                "--width",
                "30",
                "--height",
                "30",
                "--resolution",
                "2",
                "--preview",
            ],
        )
        assert result.exit_code == 0
        assert "Launching 3D interactive viewport in browser..." in result.output
        assert mock_open.called
