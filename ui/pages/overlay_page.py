
from __future__ import annotations

import multiprocessing
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

def _run_timer_overlay():
    from modules.overlay.timer_overlay_tk import launch_overlay
    launch_overlay(30, 30)

class OverlayPage(QWidget):
    page_id = "overlay"
    title = "OVERLAY"

    def __init__(self):
        super().__init__()
        self._proc = None

        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        lay.setSpacing(14)

        title = QLabel("Overlay Tools")
        title.setObjectName("H2")

        desc = QLabel(
            "In-game overlay tools. More features will be added here over time."
        )
        desc.setObjectName("Dim")
        desc.setWordWrap(True)

        self.btn_timer = QPushButton("Toggle Event Timers Overlay")
        self.btn_timer.clicked.connect(self._toggle_timer)

        lay.addWidget(title)
        lay.addWidget(desc)
        lay.addWidget(self.btn_timer)
        lay.addStretch(1)

    def _toggle_timer(self):
        if self._proc and self._proc.is_alive():
            self._proc.terminate()
            self._proc = None
            self.btn_timer.setText("Toggle Event Timers Overlay")
        else:
            self._proc = multiprocessing.Process(target=_run_timer_overlay, daemon=True)
            self._proc.start()
            self.btn_timer.setText("Disable Event Timers Overlay")

    def register_actions(self, registry):
        pass
