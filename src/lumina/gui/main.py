import sys

from PySide6.QtWidgets import QApplication

from lumina.gui.app import MainWindow


def launch_gui() -> int:
    """Initializes and runs the Lumina Studio PySide6 GUI desktop application."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    app.setApplicationName("Lumina Studio")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(launch_gui())
