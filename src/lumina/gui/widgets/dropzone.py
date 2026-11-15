import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PySide6.QtWidgets import QFileDialog, QFrame, QLabel, QPushButton, QVBoxLayout


class ImageDropZone(QFrame):
    """Modern drag-and-drop zone widget for image input with thumbnail preview."""

    image_selected = Signal(str)

    def __init__(self, parent=None, title="Drop image here or click to browse"):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.image_path: str | None = None
        self.default_title = title

        self.setObjectName("dropZone")
        self.setStyleSheet("""
            #dropZone {
                background-color: #161b22;
                border: 2px dashed #30363d;
                border-radius: 12px;
                min-height: 140px;
            }
            #dropZone:hover {
                border-color: #58a6ff;
                background-color: #1c2128;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(16, 16, 16, 16)

        self.icon_label = QLabel("📷")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 32px; background: transparent;")

        self.text_label = QLabel(self.default_title)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet(
            "color: #8b949e; font-size: 13px; font-weight: 500; background: transparent;"
        )

        self.path_label = QLabel("")
        self.path_label.setAlignment(Qt.AlignCenter)
        self.path_label.setStyleSheet(
            "color: #58a6ff; font-size: 11px; font-weight: 600; background: transparent;"
        )
        self.path_label.hide()

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background: transparent; border-radius: 8px;")
        self.preview_label.hide()

        self.clear_btn = QPushButton("Remove")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: #21262d;
                color: #f85149;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #b62324;
                color: white;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_image)
        self.clear_btn.hide()

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addWidget(self.preview_label)
        layout.addWidget(self.path_label)
        layout.addWidget(self.clear_btn, alignment=Qt.AlignCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.browse_file()

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Source Image",
            "",
            "Image Files (*.jpg *.jpeg *.png *.webp *.bmp);;All Files (*)",
        )
        if file_path:
            self.set_image(file_path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                path = urls[0].toLocalFile()
                ext = os.path.splitext(path)[1].lower()
                if ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]:
                    event.acceptProposedAction()
                    self.setStyleSheet("""
                        #dropZone {
                            background-color: #1f2937;
                            border: 2px dashed #58a6ff;
                            border-radius: 12px;
                            min-height: 140px;
                        }
                    """)
                    return
        event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            #dropZone {
                background-color: #161b22;
                border: 2px dashed #30363d;
                border-radius: 12px;
                min-height: 140px;
            }
            #dropZone:hover {
                border-color: #58a6ff;
                background-color: #1c2128;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        self.dragLeaveEvent(None)
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.exists(path):
                self.set_image(path)
                event.acceptProposedAction()

    def set_image(self, file_path: str):
        self.image_path = file_path
        filename = os.path.basename(file_path)

        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                180, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled)
            self.preview_label.show()
            self.icon_label.hide()
            self.text_label.hide()
            self.path_label.setText(filename)
            self.path_label.show()
            self.clear_btn.show()
            self.image_selected.emit(file_path)

    def clear_image(self):
        self.image_path = None
        self.preview_label.hide()
        self.path_label.hide()
        self.clear_btn.hide()
        self.icon_label.show()
        self.text_label.show()
