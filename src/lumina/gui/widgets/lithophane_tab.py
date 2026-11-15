import os
import tempfile
import time

import cv2
import numpy as np
from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from lumina import flat_lithophane, get_mesh_stats, open_viewer
from lumina.core.shapes import ShapeFactory
from lumina.gui.widgets.dropzone import ImageDropZone


class LithophaneWorker(QObject):
    finished = Signal(object, float)  # mesh_obj, elapsed
    error = Signal(str)

    def __init__(self, kwargs):
        super().__init__()
        self.kwargs = kwargs

    def run(self):
        try:
            start = time.perf_counter()
            mesh_obj = flat_lithophane(**self.kwargs)
            elapsed = time.perf_counter() - start
            self.finished.emit(mesh_obj, elapsed)
        except Exception as e:
            self.error.emit(str(e))


class LithophaneTab(QWidget):
    """Interactive GUI Tab for Flat & Shaped 3D Lithophane generation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mesh_obj = None
        self.temp_stl_path: str | None = None
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
        self.drop_zone = ImageDropZone(self, "Drop photo here for 3D Lithophane")
        self.drop_zone.image_selected.connect(self.on_image_selected)
        left_layout.addWidget(self.drop_zone)

        # 2. Dimensions Group
        dim_group = QGroupBox("Dimensions (mm)")
        dim_layout = QGridLayout(dim_group)
        dim_layout.setSpacing(8)

        dim_layout.addWidget(QLabel("Width:"), 0, 0)
        self.spin_width = QDoubleSpinBox()
        self.spin_width.setRange(10.0, 500.0)
        self.spin_width.setValue(100.0)
        self.spin_width.setSuffix(" mm")
        dim_layout.addWidget(self.spin_width, 0, 1)

        dim_layout.addWidget(QLabel("Height:"), 0, 2)
        self.spin_height = QDoubleSpinBox()
        self.spin_height.setRange(10.0, 500.0)
        self.spin_height.setValue(150.0)
        self.spin_height.setSuffix(" mm")
        dim_layout.addWidget(self.spin_height, 0, 3)

        left_layout.addWidget(dim_group)

        # 3. Thickness & Frame Group
        thick_group = QGroupBox("Relief & Frame (mm)")
        thick_layout = QGridLayout(thick_group)
        thick_layout.setSpacing(8)

        thick_layout.addWidget(QLabel("Min Thick:"), 0, 0)
        self.spin_min_thick = QDoubleSpinBox()
        self.spin_min_thick.setRange(0.2, 5.0)
        self.spin_min_thick.setSingleStep(0.1)
        self.spin_min_thick.setValue(0.5)
        self.spin_min_thick.setSuffix(" mm")
        thick_layout.addWidget(self.spin_min_thick, 0, 1)

        thick_layout.addWidget(QLabel("Max Thick:"), 0, 2)
        self.spin_max_thick = QDoubleSpinBox()
        self.spin_max_thick.setRange(1.0, 10.0)
        self.spin_max_thick.setSingleStep(0.2)
        self.spin_max_thick.setValue(3.0)
        self.spin_max_thick.setSuffix(" mm")
        thick_layout.addWidget(self.spin_max_thick, 0, 3)

        thick_layout.addWidget(QLabel("Frame Width:"), 1, 0)
        self.spin_frame_w = QDoubleSpinBox()
        self.spin_frame_w.setRange(0.0, 20.0)
        self.spin_frame_w.setValue(1.0)
        self.spin_frame_w.setSuffix(" mm")
        thick_layout.addWidget(self.spin_frame_w, 1, 1)

        thick_layout.addWidget(QLabel("Frame Height:"), 1, 2)
        self.spin_frame_h = QDoubleSpinBox()
        self.spin_frame_h.setRange(0.0, 20.0)
        self.spin_frame_h.setValue(2.0)
        self.spin_frame_h.setSuffix(" mm")
        thick_layout.addWidget(self.spin_frame_h, 1, 3)

        left_layout.addWidget(thick_group)

        # 4. Shape & Resolution
        shape_group = QGroupBox("Geometry & Resolution")
        shape_layout = QGridLayout(shape_group)
        shape_layout.setSpacing(8)

        shape_layout.addWidget(QLabel("Shape:"), 0, 0)
        self.combo_shape = QComboBox()
        self.combo_shape.addItems(["Rectangle", "Circle", "Heart"])
        self.combo_shape.currentIndexChanged.connect(self.update_2d_preview)
        shape_layout.addWidget(self.combo_shape, 0, 1)

        shape_layout.addWidget(QLabel("Resolution:"), 1, 0)
        res_box = QHBoxLayout()
        self.slider_res = QSlider(Qt.Horizontal)
        self.slider_res.setRange(1, 8)
        self.slider_res.setValue(4)
        self.label_res = QLabel("4 px/mm")
        self.slider_res.valueChanged.connect(
            lambda v: self.label_res.setText(f"{v} px/mm")
        )
        res_box.addWidget(self.slider_res)
        res_box.addWidget(self.label_res)
        shape_layout.addLayout(res_box, 1, 1)

        opt_box = QHBoxLayout()
        self.chk_enhance = QCheckBox("Enhance Contrast")
        self.chk_normalize = QCheckBox("Normalize")
        opt_box.addWidget(self.chk_enhance)
        opt_box.addWidget(self.chk_normalize)
        shape_layout.addLayout(opt_box, 2, 0, 1, 2)

        left_layout.addWidget(shape_group)

        # 5. Action Buttons & Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        left_layout.addWidget(self.progress_bar)

        self.btn_generate = QPushButton("⚡ Generate 3D Lithophane")
        self.btn_generate.setStyleSheet("""
            QPushButton {
                background: #238636;
                color: white;
                font-size: 13px;
                font-weight: 700;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.1);
            }
            QPushButton:hover {
                background: #2ea043;
            }
            QPushButton:disabled {
                background: #21262d;
                color: #8b949e;
            }
        """)
        self.btn_generate.clicked.connect(self.start_generation)
        self.btn_generate.setEnabled(False)
        left_layout.addWidget(self.btn_generate)

        left_layout.addStretch()
        main_layout.addWidget(left_panel)

        # Right Column: Preview & Results
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        # 2D Shape Boundary Preview
        preview_group = QGroupBox("Shape Mask & Input Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.label_preview = QLabel("Select an image to see boundary preview")
        self.label_preview.setAlignment(Qt.AlignCenter)
        self.label_preview.setMinimumHeight(240)
        self.label_preview.setStyleSheet("""
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            color: #8b949e;
        """)
        preview_layout.addWidget(self.label_preview)
        right_layout.addWidget(preview_group)

        # Mesh Statistics Box
        self.stats_group = QGroupBox("Generated Mesh Statistics")
        stats_layout = QGridLayout(self.stats_group)
        stats_layout.setSpacing(8)

        self.lbl_stat_dims = QLabel("-")
        self.lbl_stat_thick = QLabel("-")
        self.lbl_stat_facets = QLabel("-")
        self.lbl_stat_weight = QLabel("-")

        stats_layout.addWidget(QLabel("Dimensions:"), 0, 0)
        stats_layout.addWidget(self.lbl_stat_dims, 0, 1)
        stats_layout.addWidget(QLabel("Relief Range:"), 0, 2)
        stats_layout.addWidget(self.lbl_stat_thick, 0, 3)
        stats_layout.addWidget(QLabel("Facets (Triangles):"), 1, 0)
        stats_layout.addWidget(self.lbl_stat_facets, 1, 1)
        stats_layout.addWidget(QLabel("Est. PLA Weight:"), 1, 2)
        stats_layout.addWidget(self.lbl_stat_weight, 1, 3)

        right_layout.addWidget(self.stats_group)
        self.stats_group.hide()

        # Output Actions
        self.btn_box = QHBoxLayout()
        self.btn_save_stl = QPushButton("💾 Export STL File...")
        self.btn_save_stl.setStyleSheet("""
            QPushButton {
                background: #1f6feb;
                color: white;
                font-weight: 600;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover { background: #388bfd; }
        """)
        self.btn_save_stl.clicked.connect(self.save_stl)
        self.btn_save_stl.hide()

        self.btn_view_3d = QPushButton("🌐 Open in 3D WebGL Viewport")
        self.btn_view_3d.setStyleSheet("""
            QPushButton {
                background: #8957e5;
                color: white;
                font-weight: 600;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover { background: #a371f7; }
        """)
        self.btn_view_3d.clicked.connect(self.open_3d_preview)
        self.btn_view_3d.hide()

        self.btn_box.addWidget(self.btn_save_stl)
        self.btn_box.addWidget(self.btn_view_3d)
        right_layout.addLayout(self.btn_box)

        main_layout.addWidget(right_panel)

    def on_image_selected(self, path: str):
        self.btn_generate.setEnabled(True)
        self.update_2d_preview()

    def get_selected_shape(self) -> str:
        idx = self.combo_shape.currentIndex()
        return ["rect", "circle", "heart"][idx]

    def update_2d_preview(self):
        if not self.drop_zone.image_path or not os.path.exists(
            self.drop_zone.image_path
        ):
            return

        try:
            img = cv2.imread(self.drop_zone.image_path)
            if img is None:
                return

            h, w = img.shape[:2]
            shape = self.get_selected_shape()
            mask = ShapeFactory.get_strategy(shape).create_mask(h, w)

            # Apply alpha/darkening outside mask
            preview_img = img.copy()
            preview_img[~mask] = (preview_img[~mask] * 0.25).astype(np.uint8)

            # Convert BGR to RGB
            rgb = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)

            scaled = pixmap.scaled(
                self.label_preview.width() - 10,
                self.label_preview.height() - 10,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.label_preview.setPixmap(scaled)
        except Exception:
            pass

    def start_generation(self):
        if not self.drop_zone.image_path:
            return

        self.btn_generate.setEnabled(False)
        self.progress_bar.show()

        kwargs = {
            "image_path": self.drop_zone.image_path,
            "width_mm": self.spin_width.value(),
            "height_mm": self.spin_height.value(),
            "max_thickness": self.spin_max_thick.value(),
            "min_thickness": self.spin_min_thick.value(),
            "frame_thick_mm": self.spin_frame_w.value(),
            "frame_height_mm": self.spin_frame_h.value(),
            "resolution": self.slider_res.value(),
            "enhance": self.chk_enhance.isChecked(),
            "normalize": self.chk_normalize.isChecked(),
            "shape": self.get_selected_shape(),
        }

        self.worker_thread = QThread()
        self.worker = LithophaneWorker(kwargs)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.error.connect(self.on_generation_error)

        self.worker_thread.start()

    def on_generation_finished(self, mesh_obj, elapsed):
        self.mesh_obj = mesh_obj
        self.progress_bar.hide()
        self.btn_generate.setEnabled(True)

        # Save to temp file for 3D viewer
        fd, self.temp_stl_path = tempfile.mkstemp(prefix="lumina_temp_", suffix=".stl")
        os.close(fd)
        mesh_obj.save(self.temp_stl_path)

        # Update stats
        stats = get_mesh_stats(mesh_obj)
        self.lbl_stat_dims.setText(f"{stats['width_mm']} × {stats['height_mm']} mm")
        self.lbl_stat_thick.setText(f"{stats['min_z']} .. {stats['max_z']} mm")
        self.lbl_stat_facets.setText(f"{stats['facets']:,} facets")
        self.lbl_stat_weight.setText(f"{stats['weight_grams']} g (PLA)")

        self.stats_group.show()
        self.btn_save_stl.show()
        self.btn_view_3d.show()

        self.worker_thread.quit()
        self.worker_thread.wait()

    def on_generation_error(self, err_msg):
        self.progress_bar.hide()
        self.btn_generate.setEnabled(True)
        self.label_preview.setText(f"Error: {err_msg}")
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()

    def save_stl(self):
        if not self.mesh_obj:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Lithophane STL",
            "lithophane.stl",
            "STL Files (*.stl);;All Files (*)",
        )
        if file_path:
            self.mesh_obj.save(file_path)

    def open_3d_preview(self):
        if self.temp_stl_path and os.path.exists(self.temp_stl_path):
            open_viewer(self.temp_stl_path)
