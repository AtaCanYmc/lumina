import os
import tempfile
import time

import cv2
from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from lumina import generate_spiral_betty_png
from lumina.gui.widgets.dropzone import ImageDropZone


class SpiralWorker(QObject):
    finished = Signal(object, float)  # result_img, elapsed
    error = Signal(str)

    def __init__(self, kwargs):
        super().__init__()
        self.kwargs = kwargs

    def run(self):
        try:
            start = time.perf_counter()
            result = generate_spiral_betty_png(**self.kwargs)
            elapsed = time.perf_counter() - start
            self.finished.emit(result, elapsed)
        except Exception as e:
            self.error.emit(str(e))


class SpiralTab(QWidget):
    """Interactive GUI Tab for Archimedean Spiral Betty vector/raster art."""

    send_to_lithophane = Signal(str)  # emitted with temp png path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_img = None
        self.temp_png_path: str | None = None
        self.worker_thread = None

        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(20)

        # Left Column: Controls (Width 380px)
        left_panel = QWidget()
        left_panel.setFixedWidth(380)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        # 1. Drop Zone
        self.drop_zone = ImageDropZone(self, "Drop photo here for Spiral Betty art")
        self.drop_zone.image_selected.connect(
            lambda _: self.btn_generate.setEnabled(True)
        )
        left_layout.addWidget(self.drop_zone)

        # 2. Spiral Parameters Group
        param_group = QGroupBox("Spiral Betty Parameters")
        param_layout = QVBoxLayout(param_group)
        param_layout.setSpacing(10)

        # Radius
        row_radius = QHBoxLayout()
        row_radius.addWidget(QLabel("Target Radius:"))
        self.spin_radius = QDoubleSpinBox()
        self.spin_radius.setRange(10.0, 500.0)
        self.spin_radius.setValue(100.0)
        self.spin_radius.setSuffix(" mm")
        row_radius.addWidget(self.spin_radius)
        param_layout.addLayout(row_radius)

        # Lines count
        row_lines = QHBoxLayout()
        row_lines.addWidget(QLabel("Spiral Lines:"))
        self.slider_lines = QSlider(Qt.Horizontal)
        self.slider_lines.setRange(10, 100)
        self.slider_lines.setValue(35)
        self.lbl_lines = QLabel("35")
        self.slider_lines.valueChanged.connect(lambda v: self.lbl_lines.setText(str(v)))
        row_lines.addWidget(self.slider_lines)
        row_lines.addWidget(self.lbl_lines)
        param_layout.addLayout(row_lines)

        # Resolution
        row_res = QHBoxLayout()
        row_res.addWidget(QLabel("Resolution:"))
        self.slider_res = QSlider(Qt.Horizontal)
        self.slider_res.setRange(1, 8)
        self.slider_res.setValue(4)
        self.lbl_res = QLabel("4 px/mm")
        self.slider_res.valueChanged.connect(
            lambda v: self.lbl_res.setText(f"{v} px/mm")
        )
        row_res.addWidget(self.slider_res)
        row_res.addWidget(self.lbl_res)
        param_layout.addLayout(row_res)

        # Angle Step
        row_step = QHBoxLayout()
        row_step.addWidget(QLabel("Angle Step:"))
        self.spin_step = QDoubleSpinBox()
        self.spin_step.setRange(0.01, 0.20)
        self.spin_step.setSingleStep(0.01)
        self.spin_step.setValue(0.05)
        row_step.addWidget(self.spin_step)
        param_layout.addLayout(row_step)

        left_layout.addWidget(param_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        left_layout.addWidget(self.progress_bar)

        # Generate Button
        self.btn_generate = QPushButton("🌀 Generate Spiral Betty Art")
        self.btn_generate.setStyleSheet("""
            QPushButton {
                background: #1f6feb;
                color: white;
                font-size: 13px;
                font-weight: 700;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover { background: #388bfd; }
            QPushButton:disabled { background: #21262d; color: #8b949e; }
        """)
        self.btn_generate.clicked.connect(self.start_generation)
        self.btn_generate.setEnabled(False)
        left_layout.addWidget(self.btn_generate)

        left_layout.addStretch()
        main_layout.addWidget(left_panel)

        # Right Column: Generated Spiral Output Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        preview_group = QGroupBox("Spiral Betty Continuous Line Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.label_preview = QLabel("Click Generate to render continuous spiral art")
        self.label_preview.setAlignment(Qt.AlignCenter)
        self.label_preview.setMinimumHeight(380)
        self.label_preview.setStyleSheet("""
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            color: #8b949e;
        """)
        preview_layout.addWidget(self.label_preview)
        right_layout.addWidget(preview_group)

        # Action Buttons
        btn_box = QHBoxLayout()
        self.btn_save_png = QPushButton("💾 Export PNG Image...")
        self.btn_save_png.setStyleSheet("""
            QPushButton {
                background: #238636;
                color: white;
                font-weight: 600;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover { background: #2ea043; }
        """)
        self.btn_save_png.clicked.connect(self.save_png)
        self.btn_save_png.hide()

        self.btn_to_litho = QPushButton("⚡ Convert Spiral to 3D Lithophane STL")
        self.btn_to_litho.setStyleSheet("""
            QPushButton {
                background: #8957e5;
                color: white;
                font-weight: 600;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover { background: #a371f7; }
        """)
        self.btn_to_litho.clicked.connect(self.chain_to_lithophane)
        self.btn_to_litho.hide()

        btn_box.addWidget(self.btn_save_png)
        btn_box.addWidget(self.btn_to_litho)
        right_layout.addLayout(btn_box)

        main_layout.addWidget(right_panel)

    def start_generation(self):
        if not self.drop_zone.image_path:
            return

        self.btn_generate.setEnabled(False)
        self.progress_bar.show()

        kwargs = {
            "image_path": self.drop_zone.image_path,
            "radius_mm": self.spin_radius.value(),
            "lines": self.slider_lines.value(),
            "resolution": self.slider_res.value(),
            "angle_step": self.spin_step.value(),
        }

        self.worker_thread = QThread()
        self.worker = SpiralWorker(kwargs)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.error.connect(self.on_generation_error)

        self.worker_thread.start()

    def on_generation_finished(self, result_img, elapsed):
        self.result_img = result_img
        self.progress_bar.hide()
        self.btn_generate.setEnabled(True)

        # Save temp PNG for chaining
        fd, self.temp_png_path = tempfile.mkstemp(prefix="spiral_art_", suffix=".png")
        os.close(fd)
        cv2.imwrite(self.temp_png_path, result_img)

        # Display preview
        h, w = result_img.shape[:2]
        qimg = QImage(result_img.data, w, h, w, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg)

        scaled = pixmap.scaled(
            self.label_preview.width() - 20,
            self.label_preview.height() - 20,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.label_preview.setPixmap(scaled)

        self.btn_save_png.show()
        self.btn_to_litho.show()

        self.worker_thread.quit()
        self.worker_thread.wait()

    def on_generation_error(self, err_msg):
        self.progress_bar.hide()
        self.btn_generate.setEnabled(True)
        self.label_preview.setText(f"Error: {err_msg}")
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()

    def save_png(self):
        if self.result_img is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Spiral Art PNG",
            "spiral_art.png",
            "PNG Images (*.png);;All Files (*)",
        )
        if file_path:
            cv2.imwrite(file_path, self.result_img)

    def chain_to_lithophane(self):
        if self.temp_png_path and os.path.exists(self.temp_png_path):
            self.send_to_lithophane.emit(self.temp_png_path)
