import os
import tempfile

import cv2
import numpy as np
from click.testing import CliRunner

from lumina.cli import cli, format_bytes, format_duration, render_box


def create_test_image(path, size=(100, 100)):
    """Helper to create a test image."""
    img = np.random.randint(0, 255, size, dtype=np.uint8)
    cv2.imwrite(path, img)
    return path


class TestCliUi:
    def test_format_bytes(self):
        assert format_bytes(500) == "500 B"
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(2 * 1024 * 1024) == "2.00 MB"

    def test_format_duration(self):
        assert format_duration(0.25) == "250 ms"
        assert format_duration(1.5) == "1.50 s"

    def test_render_box(self):
        box = render_box("Test Box", [("Key", "Value")])
        assert "Test Box" in box
        assert "Key:" in box
        assert "Value" in box

    def test_bare_cli_shows_banner_and_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert "Lumina" in result.output
        assert "Lithophane" in result.output
        assert "Commands:" in result.output

    def test_cli_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        from lumina import __version__

        assert __version__ in result.output


class TestFlatCommand:
    def test_flat_creates_stl(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.jpg")
            create_test_image(img_path)

            result = runner.invoke(
                cli, ["flat", img_path, "--width", "50", "--height", "50"]
            )

            assert result.exit_code == 0
            assert "Success!" in result.output
            assert os.path.exists(os.path.join(tmpdir, "test.stl"))

    def test_flat_with_shape(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.jpg")
            create_test_image(img_path)

            result = runner.invoke(cli, ["flat", img_path, "--shape", "circle"])

            assert result.exit_code == 0
            assert "Success!" in result.output

    def test_flat_fails_on_invalid_dimensions(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.jpg")
            create_test_image(img_path)

            result = runner.invoke(cli, ["flat", img_path, "--width", "-10"])

            assert result.exit_code != 0
            assert "Error:" in result.output


class TestSpiralCommand:
    def test_spiral_creates_png(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.jpg")
            create_test_image(img_path)

            result = runner.invoke(cli, ["spiral", img_path, "--radius", "50"])

            assert result.exit_code == 0
            assert "Success!" in result.output
            assert os.path.exists(os.path.join(tmpdir, "test_spiral.png"))

    def test_spiral_with_custom_output(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.jpg")
            output_path = os.path.join(tmpdir, "custom_spiral.png")
            create_test_image(img_path)

            result = runner.invoke(cli, ["spiral", img_path, "-o", output_path])

            assert result.exit_code == 0
            assert os.path.exists(output_path)

    def test_spiral_fails_on_invalid_parameters(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.jpg")
            create_test_image(img_path)

            result = runner.invoke(cli, ["spiral", img_path, "--lines", "0"])

            assert result.exit_code != 0
            assert "Error:" in result.output


class TestInteractiveCommand:
    def test_interactive_flat(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.jpg")
            out_stl = os.path.join(tmpdir, "out.stl")
            create_test_image(img_path, size=(40, 40))

            # 1: Mode flat, image path, width, height, shape, resolution, max_thick, min_thick,
            # frame_thick, frame_height, enhance, normalize, output, confirm
            inputs = [
                "1",
                img_path,
                "30",
                "30",
                "rect",
                "2",
                "3.0",
                "0.5",
                "1.0",
                "2.0",
                "n",
                "n",
                out_stl,
                "y",
            ]
            result = runner.invoke(cli, ["interactive"], input="\n".join(inputs) + "\n")

            assert result.exit_code == 0
            assert "Success!" in result.output
            assert os.path.exists(out_stl)

    def test_interactive_spiral(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.jpg")
            out_png = os.path.join(tmpdir, "out_spiral.png")
            create_test_image(img_path, size=(40, 40))

            # 2: Mode spiral, image path, radius, lines, resolution, angle_step, output, confirm
            inputs = ["2", img_path, "20", "15", "2", "0.05", out_png, "y"]
            result = runner.invoke(cli, ["wizard"], input="\n".join(inputs) + "\n")

            assert result.exit_code == 0
            assert "Success!" in result.output
            assert os.path.exists(out_png)

    def test_interactive_cancel(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.jpg")
            create_test_image(img_path, size=(40, 40))

            # flat flow, but reject confirmation at the end
            inputs = [
                "1",
                img_path,
                "30",
                "30",
                "rect",
                "2",
                "3.0",
                "0.5",
                "1.0",
                "2.0",
                "n",
                "n",
                os.path.join(tmpdir, "cancel.stl"),
                "n",
            ]
            result = runner.invoke(cli, ["interactive"], input="\n".join(inputs) + "\n")

            assert result.exit_code == 0
            assert "Cancelled." in result.output
            assert not os.path.exists(os.path.join(tmpdir, "cancel.stl"))
