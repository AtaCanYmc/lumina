import os

import pytest
from click.testing import CliRunner

from lumina.cli import cli

# Skip GUI tests if PySide6 is not available
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from lumina.gui.app import MainWindow
from lumina.gui.widgets.dropzone import ImageDropZone
from lumina.gui.widgets.lithophane_tab import LithophaneTab
from lumina.gui.widgets.spiral_tab import SpiralTab


@pytest.fixture(scope="session")
def qapp():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_main_window_init(qapp):
    win = MainWindow()
    assert "Lumina Studio" in win.windowTitle()
    assert win.tabs.count() == 2
    assert isinstance(win.litho_tab, LithophaneTab)
    assert isinstance(win.spiral_tab, SpiralTab)


def test_dropzone_behavior(qapp):
    zone = ImageDropZone(title="Test Zone")
    assert zone.image_path is None

    test_image = "assets/images/example_input.jpg"
    zone.set_image(test_image)
    assert zone.image_path == test_image
    assert not zone.preview_label.isHidden()

    zone.clear_image()
    assert zone.image_path is None
    assert zone.preview_label.isHidden()


def test_lithophane_tab_params(qapp):
    tab = LithophaneTab()
    assert tab.spin_width.value() == 100.0
    assert tab.spin_height.value() == 150.0
    assert tab.get_selected_shape() == "rect"

    tab.combo_shape.setCurrentIndex(1)
    assert tab.get_selected_shape() == "circle"

    tab.combo_shape.setCurrentIndex(2)
    assert tab.get_selected_shape() == "heart"


def test_spiral_tab_chaining(qapp):
    win = MainWindow()
    assert win.tabs.currentIndex() == 0

    test_image = "assets/images/example_input.jpg"
    # Emit chaining signal
    win.spiral_tab.send_to_lithophane.emit(test_image)

    # Should switch to Lithophane tab (index 0)
    assert win.tabs.currentIndex() == 0
    # Should automatically select circle shape
    assert win.litho_tab.get_selected_shape() == "circle"
    assert win.litho_tab.drop_zone.image_path == test_image


def test_cli_gui_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["gui", "--help"])
    assert result.exit_code == 0
    assert "Lumina Studio" in result.output
