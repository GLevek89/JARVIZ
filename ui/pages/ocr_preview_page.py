from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QSpinBox, QMessageBox
)

from .base import Page

try:
    import mss  # type: ignore
except Exception:  # pragma: no cover
    mss = None

@dataclass
class Region:
    x: int = 0
    y: int = 0
    w: int = 800
    h: int = 600

class OCRPreviewPage(Page):
    page_id = "ocr_preview"
    title = "OCR Preview"

    def __init__(self, parent=None):
        super().__init__(parent)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

        self._sct = None
        self._monitor_index = 1  # mss uses 1..N (0 is all)

        self._region = Region()

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        h = QLabel("Live Capture Preview")
        h.setObjectName("H1")
        root.addWidget(h)

        card = QFrame()
        card.setObjectName("Card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 16, 16, 16)
        cl.setSpacing(10)

        row = QHBoxLayout()
        row.addWidget(QLabel("Monitor"), 0)
        self._mon = QSpinBox()
        self._mon.setMinimum(1)
        self._mon.setMaximum(8)
        self._mon.setValue(1)
        self._mon.valueChanged.connect(self._on_mon_changed)
        row.addWidget(self._mon, 0)

        row.addSpacing(12)
        row.addWidget(QLabel("X"), 0)
        self._x = QSpinBox(); self._x.setMaximum(99999); self._x.setValue(self._region.x); self._x.valueChanged.connect(self._on_region)
        row.addWidget(self._x, 0)
        row.addWidget(QLabel("Y"), 0)
        self._y = QSpinBox(); self._y.setMaximum(99999); self._y.setValue(self._region.y); self._y.valueChanged.connect(self._on_region)
        row.addWidget(self._y, 0)
        row.addWidget(QLabel("W"), 0)
        self._w = QSpinBox(); self._w.setMaximum(99999); self._w.setValue(self._region.w); self._w.valueChanged.connect(self._on_region)
        row.addWidget(self._w, 0)
        row.addWidget(QLabel("H"), 0)
        self._h = QSpinBox(); self._h.setMaximum(99999); self._h.setValue(self._region.h); self._h.valueChanged.connect(self._on_region)
        row.addWidget(self._h, 0)

        row.addSpacing(12)
        row.addWidget(QLabel("FPS"), 0)
        self._fps = QSpinBox()
        self._fps.setMinimum(1)
        self._fps.setMaximum(30)
        self._fps.setValue(10)
        row.addWidget(self._fps, 0)

        self._btn = QPushButton("Start Preview")
        self._btn.setObjectName("Primary")
        self._btn.clicked.connect(self._toggle)
        row.addWidget(self._btn, 0)

        cl.addLayout(row)

        self._img = QLabel("Preview will appear here.")
        self._img.setAlignment(Qt.AlignCenter)
        self._img.setMinimumHeight(360)
        self._img.setObjectName("Preview")
        cl.addWidget(self._img, 1)

        tip = QLabel("Tip: Set the region to your tooltip area in-game. This is capture-only (no OCR).")
        tip.setObjectName("Dim")
        cl.addWidget(tip)

        root.addWidget(card, 1)

    def _ensure_mss(self) -> bool:
        if mss is None:
            QMessageBox.critical(self, "Missing dependency", "mss is not installed. Run: py -m pip install -r requirements.txt")
            return False
        return True

    def _on_mon_changed(self, v: int):
        self._monitor_index = max(1, int(v))

    def _on_region(self, _):
        self._region = Region(
            x=int(self._x.value()),
            y=int(self._y.value()),
            w=int(self._w.value()),
            h=int(self._h.value()),
        )

    def _toggle(self):
        if self._timer.isActive():
            self._timer.stop()
            if self._sct is not None:
                try:
                    self._sct.close()
                except Exception:
                    pass
            self._sct = None
            self._btn.setText("Start Preview")
            return

        if not self._ensure_mss():
            return

        try:
            self._sct = mss.mss()
        except Exception as e:
            QMessageBox.critical(self, "Capture error", f"Unable to start screen capture.\n\n{e}")
            self._sct = None
            return

        fps = max(1, int(self._fps.value()))
        self._timer.start(int(1000 / fps))
        self._btn.setText("Stop Preview")

    def _tick(self):
        if self._sct is None:
            return
        try:
            mon = self._sct.monitors[self._monitor_index]
            bbox = {
                "left": mon["left"] + self._region.x,
                "top": mon["top"] + self._region.y,
                "width": self._region.w,
                "height": self._region.h,
            }
            shot = self._sct.grab(bbox)
            # BGRA -> QImage
            qimg = QImage(shot.raw, shot.width, shot.height, QImage.Format.Format_BGRA8888)
            pix = QPixmap.fromImage(qimg)
            # Fit to label while preserving aspect
            self._img.setPixmap(pix.scaled(self._img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            # Stop preview on repeated failures
            self._timer.stop()
            self._btn.setText("Start Preview")
            self._img.setText(f"Preview stopped.\n{e}")
