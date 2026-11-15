from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from lumina import __version__
from lumina.gui.widgets.lithophane_tab import LithophaneTab
from lumina.gui.widgets.spiral_tab import SpiralTab

DARK_STYLESHEET = """
QMainWindow {
    background-color: #0d1117;
}

QWidget {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 13px;
}

QTabWidget::pane {
    border: 1px solid #30363d;
    background-color: #0d1117;
    border-radius: 8px;
    top: -1px;
}

QTabBar::tab {
    background: #161b22;
    color: #8b949e;
    border: 1px solid #30363d;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 24px;
    margin-right: 4px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background: #0d1117;
    color: #58a6ff;
    border-color: #58a6ff;
    border-bottom: 2px solid #58a6ff;
}

QTabBar::tab:hover:!selected {
    background: #21262d;
    color: #e6edf3;
}

QGroupBox {
    border: 1px solid #30363d;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 14px;
    font-weight: 600;
    color: #c9d1d9;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #58a6ff;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QDoubleSpinBox, QSpinBox, QComboBox {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 5px 8px;
    color: #e6edf3;
}

QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus {
    border-color: #58a6ff;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #21262d;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #58a6ff;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 1px solid #30363d;
    width: 14px;
    height: 14px;
    margin-top: -4px;
    margin-bottom: -4px;
    border-radius: 7px;
}

QProgressBar {
    border: 1px solid #30363d;
    border-radius: 6px;
    text-align: center;
    background-color: #161b22;
    color: #ffffff;
    height: 16px;
}

QProgressBar::chunk {
    background-color: #2ea043;
    border-radius: 5px;
}

QCheckBox {
    color: #c9d1d9;
    spacing: 6px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #30363d;
    border-radius: 4px;
    background: #161b22;
}

QCheckBox::indicator:checked {
    background: #1f6feb;
    border-color: #58a6ff;
}

QStatusBar {
    background: #161b22;
    border-top: 1px solid #30363d;
    color: #8b949e;
    font-size: 11px;
}
"""


class MainWindow(QMainWindow):
    """Lumina Studio Desktop Application Main Window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Lumina Studio • v{__version__}")
        self.resize(1020, 720)
        self.setMinimumSize(880, 620)
        self.setStyleSheet(DARK_STYLESHEET)

        self.setup_ui()
        self.setup_menu()

    def setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(16, 16, 16, 16)

        self.tabs = QTabWidget()
        self.litho_tab = LithophaneTab(self)
        self.spiral_tab = SpiralTab(self)

        # Chaining signal: Spiral -> Lithophane
        self.spiral_tab.send_to_lithophane.connect(self.on_spiral_chained)

        self.tabs.addTab(self.litho_tab, "🪟 Lithophane 3D Generator")
        self.tabs.addTab(self.spiral_tab, "🌀 Spiral Betty Studio")

        layout.addWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Drag and drop any photograph to begin.")

    def setup_menu(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")

        open_action = QAction("&Open Image...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_image_dialog)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View Menu
        view_menu = menu_bar.addMenu("&View")

        switch_litho = QAction("Lithophane Tab", self)
        switch_litho.setShortcut("Ctrl+1")
        switch_litho.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        view_menu.addAction(switch_litho)

        switch_spiral = QAction("Spiral Betty Tab", self)
        switch_spiral.setShortcut("Ctrl+2")
        switch_spiral.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        view_menu.addAction(switch_spiral)

    def open_image_dialog(self):
        current_idx = self.tabs.currentIndex()
        if current_idx == 0:
            self.litho_tab.drop_zone.browse_file()
        else:
            self.spiral_tab.drop_zone.browse_file()

    def on_spiral_chained(self, spiral_png_path: str):
        # Switch to Lithophane tab
        self.tabs.setCurrentIndex(0)
        # Load generated spiral image as source
        self.litho_tab.drop_zone.set_image(spiral_png_path)
        # Select circle shape automatically for circular spiral
        self.litho_tab.combo_shape.setCurrentIndex(1)  # Circle
        self.status_bar.showMessage(
            "Spiral Betty raster chained into 3D Lithophane. Ready to generate STL.",
            5000,
        )
