import os
import tempfile
import numpy as np
import cv2
from click.testing import CliRunner
from lumina.cli import cli


def create_test_image(path, size=(100, 100)):
    """Helper to create a test image."""
    img = np.random.randint(0, 255, size, dtype=np.uint8)
    cv2.imwrite(path, img)
    return path


class TestFlatCommand:
    def test_flat_creates_stl(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.jpg")
            create_test_image(img_path)
            
            result = runner.invoke(cli, ['flat', img_path, '--width', '50', '--height', '50'])
            
            assert result.exit_code == 0
            assert "Success!" in result.output
            assert os.path.exists(os.path.join(tmpdir, "test.stl"))

    def test_flat_with_shape(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.jpg")
            create_test_image(img_path)
            
            result = runner.invoke(cli, ['flat', img_path, '--shape', 'circle'])
            
            assert result.exit_code == 0
            assert "Success!" in result.output


class TestBitmapCommand:
    def test_bitmap_c_array(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.png")
            create_test_image(img_path)
            
            result = runner.invoke(cli, ['bitmap', img_path, '--width', '16', '--height', '8'])
            
            assert result.exit_code == 0
            assert "PROGMEM" in result.output or "Bitmap" in result.output

    def test_bitmap_hex(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.png")
            create_test_image(img_path)
            
            result = runner.invoke(cli, ['bitmap', img_path, '--output-format', 'hex'])
            
            assert result.exit_code == 0


class TestSpiralCommand:
    def test_spiral_creates_png(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.jpg")
            create_test_image(img_path)
            
            result = runner.invoke(cli, ['spiral', img_path, '--radius', '50'])
            
            assert result.exit_code == 0
            assert "Success!" in result.output
            assert os.path.exists(os.path.join(tmpdir, "test_spiral.png"))

    def test_spiral_with_custom_output(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.jpg")
            output_path = os.path.join(tmpdir, "custom_spiral.png")
            create_test_image(img_path)
            
            result = runner.invoke(cli, ['spiral', img_path, '-o', output_path])
            
            assert result.exit_code == 0
            assert os.path.exists(output_path)
