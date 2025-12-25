from __future__ import annotations

import os
import time

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QFrame, QHBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QComboBox
)

from .base import Page
from ...tools_registry import ToolAction
from ...paths import data_dir
from ...modules.capture_recorder import CaptureRecorder, CaptureConfig


class CapturePage(Page):
    page_id = "capture"
    title = "Capture"

    def __init__(self, parent=None):
        super().__init__(parent)

        self._rec = CaptureRecorder()

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        h = QLabel("Capture")
        h.setObjectName("H1")
        root.addWidget(h)

        sub = QLabel("Record mouse and keyboard input while a target window is focused. No playback, just logging.")
        sub.setObjectName("Dim")
        root.addWidget(sub)

        card = QFrame()
        card.setObjectName("Card")
        root.addWidget(card)

        c = QVBoxLayout(card)
        c.setContentsMargins(16, 16, 16, 16)
        c.setSpacing(12)

        row1 = QHBoxLayout()
        row1.setSpacing(10)
        c.addLayout(row1)

        self._target = QLineEdit()
        self._target.setPlaceholderText("Foreground window contains... (default: Diablo IV)")
        self._target.setText("Diablo IV")
        row1.addWidget(QLabel("Target window:"))
        row1.addWidget(self._target, 1)

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        c.addLayout(row2)

        self._mode = QComboBox()
        self._mode.addItem("Event-driven (recommended)", "event")
        self._mode.addItem("Fixed-rate mouse move throttle", "fixed")

        self._rate = QLineEdit()
        self._rate.setPlaceholderText("25")
        self._rate.setText("25")

        row2.addWidget(QLabel("Mode:"))
        row2.addWidget(self._mode, 1)
        row2.addWidget(QLabel("Rate (ms):"))
        row2.addWidget(self._rate)

        row3 = QHBoxLayout()
        row3.setSpacing(10)
        c.addLayout(row3)

        self._out = QLineEdit()
        self._out.setReadOnly(True)
        self._refresh_output_path()

        btn_new = QPushButton("New File")
        btn_new.clicked.connect(self._refresh_output_path)

        row3.addWidget(QLabel("Output:"))
        row3.addWidget(self._out, 1)
        row3.addWidget(btn_new)

        row4 = QHBoxLayout()
        row4.setSpacing(10)
        c.addLayout(row4)

        self._btn_start = QPushButton("Start Recording")
        self._btn_stop = QPushButton("Stop")
        self._btn_stop.setEnabled(False)

        self._btn_start.clicked.connect(self._start)
        self._btn_stop.clicked.connect(self._stop)

        row4.addWidget(self._btn_start)
        row4.addWidget(self._btn_stop)
        row4.addStretch(1)

        self._status = QLabel("Status: idle")
        self._status.setObjectName("Dim")
        c.addWidget(self._status)

        if not self._rec.available():
            QMessageBox.warning(
                self,
                "Missing dependency",
                "Input capture requires 'pynput'. Install requirements.txt then restart JARVIZ."
            )

        if not self._rec.supports_foreground_gate():
            QMessageBox.information(
                self,
                "Limited foreground check",
                "Foreground-window gating (auto-pause outside the target app) is only available on Windows with pywin32 installed.\n"
                "You can still record, but it may capture input from any focused window."
            )

        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def register_actions(self, registry):
        registry.register(ToolAction(
            id="open_capture",
            title="Capture Recorder",
            keywords=["capture", "record", "macro", "mouse", "keyboard", "input"],
            open_page_id=self.page_id
        ))

    def _captures_dir(self) -> str:
        d = os.path.join(data_dir(), "captures")
        os.makedirs(d, exist_ok=True)
        return d

    def _refresh_output_path(self):
        ts = time.strftime("%Y%m%d_%H%M%S")
        out = os.path.join(self._captures_dir(), f"capture_{ts}.jsonl")
        self._out.setText(out)

    def _start(self):
        if not self._rec.available():
            QMessageBox.critical(self, "Not available", "pynput is not installed. Install requirements.txt then restart.")
            return

        try:
            fixed = int((self._rate.text() or "25").strip())
            fixed = max(1, min(250, fixed))
        except Exception:
            fixed = 25

        cfg = CaptureConfig(
            target_window_substring=(self._target.text() or "Diablo IV").strip(),
            mode=str(self._mode.currentData()),
            fixed_rate_ms=fixed,
            output_path=self._out.text().strip(),
        )

        try:
            self._rec.start(cfg)
            self._btn_start.setEnabled(False)
            self._btn_stop.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Could not start", str(e))

    def _stop(self):
        self._rec.stop()
        self._btn_start.setEnabled(True)
        self._btn_stop.setEnabled(False)

    def _tick(self):
        st = self._rec.status()
        if st["running"]:
            state = "paused (target not focused)" if st["paused"] else "recording"
        else:
            state = "idle"
        self._status.setText(f"Status: {state} | events: {st['events_written']}")

    def closeEvent(self, event):
        # Ensure recorder stops if user navigates away and closes the app.
        try:
            self._rec.stop()
        except Exception:
            pass
        return super().closeEvent(event)
