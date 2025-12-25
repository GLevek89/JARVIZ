from __future__ import annotations

import os
import threading

from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QFrame, QHBoxLayout, QLineEdit, QPushButton,
    QFileDialog, QProgressBar, QTextEdit, QMessageBox
)

from .base import Page
from ...modules.github_zip import download_repo_zip
from ...tools_registry import ToolAction

class GithubZipPage(Page):
    page_id = "github_zip"
    title = "GitHub ZIP"

    def __init__(self, parent=None):
        super().__init__(parent)

        self._repo = QLineEdit()
        self._repo.setPlaceholderText("https://github.com/OWNER/REPO (or paste /tree/branch)")

        self._branch = QLineEdit()
        self._branch.setPlaceholderText("Branch (default: main)")
        self._branch.setText("main")

        self._out_dir = QLineEdit()
        self._out_dir.setText(os.path.abspath(os.getcwd()))

        self._token = QLineEdit()
        self._token.setPlaceholderText("Token (only for private repos)")
        self._token.setEchoMode(QLineEdit.EchoMode.Password)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)

        self._log = QTextEdit()
        self._log.setReadOnly(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        h = QLabel("GitHub: Download repo as ZIP")
        h.setObjectName("H1")
        root.addWidget(h)

        card = QFrame()
        card.setObjectName("Card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        lay.addWidget(QLabel("Repo URL"))
        lay.addWidget(self._repo)

        row = QHBoxLayout()
        row.addWidget(QLabel("Branch"))
        row.addWidget(self._branch, 1)
        lay.addLayout(row)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Download folder"))
        row2.addWidget(self._out_dir, 1)
        btn_pick = QPushButton("Choose...")
        btn_pick.clicked.connect(self._choose_dir)
        row2.addWidget(btn_pick)
        lay.addLayout(row2)

        lay.addWidget(QLabel("Token (private repos only)"))
        lay.addWidget(self._token)

        btns = QHBoxLayout()
        self._btn_download = QPushButton("Download ZIP")
        self._btn_download.setObjectName("Primary")
        self._btn_download.clicked.connect(self._download)

        self._btn_open = QPushButton("Open folder")
        self._btn_open.clicked.connect(self._open_folder)

        btns.addWidget(self._btn_download)
        btns.addWidget(self._btn_open)
        btns.addStretch(1)

        lay.addLayout(btns)
        lay.addWidget(self._progress)
        lay.addWidget(QLabel("Log"))
        lay.addWidget(self._log)

        root.addWidget(card)
        root.addStretch(1)

    def register_actions(self, registry):
        registry.register(ToolAction(
            id="github_zip",
            title="GitHub: Download repo as ZIP",
            keywords=["github", "zip", "download", "repo", "token", "private"],
            open_page_id="github_zip",
        ))

    def _log_line(self, msg: str):
        self._log.append(msg)

    def _choose_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Choose download folder", self._out_dir.text())
        if d:
            self._out_dir.setText(d)

    def _open_folder(self):
        d = self._out_dir.text().strip()
        if d:
            os.startfile(d)

    def _download(self):
        repo = self._repo.text().strip()
        if not repo:
            QMessageBox.warning(self, "Missing", "Paste a GitHub repo link first.")
            return

        out_dir = self._out_dir.text().strip() or os.path.abspath(os.getcwd())
        branch = self._branch.text().strip() or "main"
        token = self._token.text().strip() or None

        self._btn_download.setEnabled(False)
        self._progress.setValue(0)
        self._log_line(f"Repo: {repo}")
        self._log_line(f"Branch: {branch}")
        self._log_line(f"Out: {out_dir}")

        def on_progress(done: int, total: int):
            if total > 0:
                pct = int(done * 100 / total)
                self._progress.setValue(max(0, min(100, pct)))
            else:
                self._progress.setValue(0)

        def worker():
            try:
                out_path = download_repo_zip(repo, branch, out_dir, token=token, on_progress=on_progress)
                self._progress.setValue(100)
                self._log_line(f"Saved: {out_path}")
                QMessageBox.information(self, "Done", f"Downloaded:\n{out_path}")
            except Exception as e:
                self._log_line(f"ERROR: {e}")
                QMessageBox.critical(self, "Failed", str(e))
            finally:
                self._btn_download.setEnabled(True)

        threading.Thread(target=worker, daemon=True).start()
