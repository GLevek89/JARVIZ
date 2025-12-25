from __future__ import annotations

import base64
import hashlib
import json
import re
import time
import uuid
from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QLineEdit,
    QTextEdit, QMessageBox, QTabWidget, QWidget, QComboBox, QCheckBox
)

from .base import Page
from ...tools_registry import ToolAction


def _card(title: str) -> tuple[QFrame, QVBoxLayout]:
    card = QFrame()
    card.setObjectName("Card")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(14, 14, 14, 14)
    lay.setSpacing(10)
    h = QLabel(title)
    h.setObjectName("H2")
    lay.addWidget(h)
    return card, lay


def _try_json(text: str):
    # Accept JSON or Python-ish dicts? Keep strict JSON by default.
    return json.loads(text)


def _pretty_json(obj, indent: int = 2) -> str:
    return json.dumps(obj, indent=indent, ensure_ascii=False, sort_keys=True)


class CodingHelperPage(Page):
    page_id = "coding"
    title = "Coding Helper"

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        top = QLabel("Utilities for quick formatting, encoding, hashing, regex testing, and timestamps.")
        top.setObjectName("Muted")
        top.setWordWrap(True)
        root.addWidget(top)

        tabs = QTabWidget()
        tabs.setObjectName("InnerTabs")
        root.addWidget(tabs, 1)

        tabs.addTab(self._build_json_tab(), "JSON")
        tabs.addTab(self._build_regex_tab(), "Regex")
        tabs.addTab(self._build_encode_tab(), "Encode/Hash")
        tabs.addTab(self._build_time_tab(), "Time")

    def register_actions(self, registry):
        registry.register(ToolAction(
            id="open_coding_helper",
            title="Coding Helper",
            keywords=["coding", "helper", "json", "regex", "base64", "hash", "uuid", "timestamp", "epoch", "format"],
            open_page_id=self.page_id
        ))

    # -------------------- JSON --------------------
    def _build_json_tab(self) -> QWidget:
        w = QWidget()
        root = QVBoxLayout(w)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        card, lay = _card("JSON formatter")
        root.addWidget(card)

        row = QHBoxLayout()
        self.json_indent = QComboBox()
        self.json_indent.addItems(["2 spaces", "4 spaces"])
        self.json_indent.setCurrentIndex(0)
        row.addWidget(QLabel("Indent:"))
        row.addWidget(self.json_indent)
        row.addStretch(1)

        self.json_sort = QCheckBox("Sort keys")
        self.json_sort.setChecked(True)
        row.addWidget(self.json_sort)

        lay.addLayout(row)

        self.json_in = QTextEdit()
        self.json_in.setPlaceholderText('Paste JSON here. Example: {"a":1,"b":[2,3]}')
        lay.addWidget(self.json_in, 1)

        btns = QHBoxLayout()
        b_format = QPushButton("Format")
        b_min = QPushButton("Minify")
        b_copy = QPushButton("Copy output")
        btns.addWidget(b_format)
        btns.addWidget(b_min)
        btns.addStretch(1)
        btns.addWidget(b_copy)
        lay.addLayout(btns)

        out_label = QLabel("Output")
        out_label.setObjectName("Muted")
        lay.addWidget(out_label)

        self.json_out = QTextEdit()
        self.json_out.setReadOnly(True)
        lay.addWidget(self.json_out, 1)

        def indent_val() -> int:
            return 2 if self.json_indent.currentIndex() == 0 else 4

        def do_format():
            try:
                obj = _try_json(self.json_in.toPlainText().strip())
                text = json.dumps(
                    obj,
                    indent=indent_val(),
                    ensure_ascii=False,
                    sort_keys=bool(self.json_sort.isChecked())
                )
                self.json_out.setPlainText(text)
            except Exception as e:
                QMessageBox.warning(self, "JSON error", f"Could not parse JSON.\n\n{e}")

        def do_minify():
            try:
                obj = _try_json(self.json_in.toPlainText().strip())
                text = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
                self.json_out.setPlainText(text)
            except Exception as e:
                QMessageBox.warning(self, "JSON error", f"Could not parse JSON.\n\n{e}")

        def do_copy():
            self.json_out.selectAll()
            self.json_out.copy()

        b_format.clicked.connect(do_format)
        b_min.clicked.connect(do_minify)
        b_copy.clicked.connect(do_copy)

        return w

    # -------------------- REGEX --------------------
    def _build_regex_tab(self) -> QWidget:
        w = QWidget()
        root = QVBoxLayout(w)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        card, lay = _card("Regex tester (Python)")
        root.addWidget(card)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Pattern:"))
        self.re_pat = QLineEdit()
        self.re_pat.setPlaceholderText(r"(\b\w+\b)")
        r1.addWidget(self.re_pat, 1)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        self.re_flags = QComboBox()
        self.re_flags.addItems(["None", "IGNORECASE", "MULTILINE", "DOTALL", "IGNORECASE|MULTILINE", "IGNORECASE|DOTALL", "MULTILINE|DOTALL", "IGNORECASE|MULTILINE|DOTALL"])
        r2.addWidget(QLabel("Flags:"))
        r2.addWidget(self.re_flags)
        r2.addStretch(1)
        lay.addLayout(r2)

        self.re_in = QTextEdit()
        self.re_in.setPlaceholderText("Paste text to test against here.")
        lay.addWidget(self.re_in, 1)

        btns = QHBoxLayout()
        b_find = QPushButton("Find matches")
        b_sub = QPushButton("Substitute")
        btns.addWidget(b_find)
        btns.addWidget(b_sub)
        btns.addStretch(1)
        lay.addLayout(btns)

        subrow = QHBoxLayout()
        subrow.addWidget(QLabel("Replace with:"))
        self.re_repl = QLineEdit()
        self.re_repl.setPlaceholderText(r"\1")
        subrow.addWidget(self.re_repl, 1)
        lay.addLayout(subrow)

        self.re_out = QTextEdit()
        self.re_out.setReadOnly(True)
        lay.addWidget(self.re_out, 1)

        def flags_val():
            s = self.re_flags.currentText()
            f = 0
            if "IGNORECASE" in s: f |= re.IGNORECASE
            if "MULTILINE" in s: f |= re.MULTILINE
            if "DOTALL" in s: f |= re.DOTALL
            return f

        def do_find():
            try:
                pat = self.re_pat.text()
                rx = re.compile(pat, flags_val())
                text = self.re_in.toPlainText()
                matches = list(rx.finditer(text))
                lines = [f"Matches: {len(matches)}"]
                for i, m in enumerate(matches[:200], start=1):
                    span = m.span()
                    preview = m.group(0)
                    if len(preview) > 80:
                        preview = preview[:77] + "..."
                    lines.append(f"{i:03d}  {span[0]}-{span[1]}  {preview}")
                if len(matches) > 200:
                    lines.append(f"... showing first 200 of {len(matches)}")
                self.re_out.setPlainText("\n".join(lines))
            except Exception as e:
                QMessageBox.warning(self, "Regex error", str(e))

        def do_sub():
            try:
                pat = self.re_pat.text()
                rx = re.compile(pat, flags_val())
                text = self.re_in.toPlainText()
                repl = self.re_repl.text()
                out = rx.sub(repl, text)
                self.re_out.setPlainText(out)
            except Exception as e:
                QMessageBox.warning(self, "Regex error", str(e))

        b_find.clicked.connect(do_find)
        b_sub.clicked.connect(do_sub)

        return w

    # -------------------- ENCODE/HASH --------------------
    def _build_encode_tab(self) -> QWidget:
        w = QWidget()
        root = QVBoxLayout(w)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # Base64
        card, lay = _card("Base64")
        root.addWidget(card)

        self.b64_in = QTextEdit()
        self.b64_in.setPlaceholderText("Input text")
        lay.addWidget(self.b64_in, 1)

        btns = QHBoxLayout()
        b_enc = QPushButton("Encode ->")
        b_dec = QPushButton("<- Decode")
        btns.addWidget(b_enc)
        btns.addWidget(b_dec)
        btns.addStretch(1)
        lay.addLayout(btns)

        self.b64_out = QTextEdit()
        self.b64_out.setReadOnly(True)
        lay.addWidget(self.b64_out, 1)

        def do_enc():
            raw = self.b64_in.toPlainText().encode("utf-8", errors="replace")
            self.b64_out.setPlainText(base64.b64encode(raw).decode("ascii"))

        def do_dec():
            try:
                raw = self.b64_in.toPlainText().strip().encode("ascii", errors="ignore")
                dec = base64.b64decode(raw, validate=False)
                self.b64_out.setPlainText(dec.decode("utf-8", errors="replace"))
            except Exception as e:
                QMessageBox.warning(self, "Base64 error", str(e))

        b_enc.clicked.connect(do_enc)
        b_dec.clicked.connect(do_dec)

        # Hash + UUID
        card2, lay2 = _card("Hash & UUID")
        root.addWidget(card2)

        hrow = QHBoxLayout()
        hrow.addWidget(QLabel("Algorithm:"))
        self.hash_alg = QComboBox()
        self.hash_alg.addItems(["sha256", "sha1", "md5"])
        hrow.addWidget(self.hash_alg)
        hrow.addStretch(1)
        lay2.addLayout(hrow)

        self.hash_in = QTextEdit()
        self.hash_in.setPlaceholderText("Text to hash")
        lay2.addWidget(self.hash_in, 1)

        hbtns = QHBoxLayout()
        b_hash = QPushButton("Compute hash")
        b_uuid = QPushButton("New UUID")
        hbtns.addWidget(b_hash)
        hbtns.addWidget(b_uuid)
        hbtns.addStretch(1)
        lay2.addLayout(hbtns)

        self.hash_out = QLineEdit()
        self.hash_out.setReadOnly(True)
        lay2.addWidget(self.hash_out)

        self.uuid_out = QLineEdit()
        self.uuid_out.setReadOnly(True)
        lay2.addWidget(self.uuid_out)

        def do_hash():
            txt = self.hash_in.toPlainText().encode("utf-8", errors="replace")
            alg = self.hash_alg.currentText()
            h = hashlib.new(alg)
            h.update(txt)
            self.hash_out.setText(h.hexdigest())

        def do_uuid():
            self.uuid_out.setText(str(uuid.uuid4()))

        b_hash.clicked.connect(do_hash)
        b_uuid.clicked.connect(do_uuid)

        root.addStretch(1)
        return w

    # -------------------- TIME --------------------
    def _build_time_tab(self) -> QWidget:
        w = QWidget()
        root = QVBoxLayout(w)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        card, lay = _card("Timestamp helper")
        root.addWidget(card)

        nowrow = QHBoxLayout()
        self.now_out = QLineEdit()
        self.now_out.setReadOnly(True)
        b_now = QPushButton("Now")
        nowrow.addWidget(QLabel("Current time:"))
        nowrow.addWidget(self.now_out, 1)
        nowrow.addWidget(b_now)
        lay.addLayout(nowrow)

        eprow = QHBoxLayout()
        self.epoch_in = QLineEdit()
        self.epoch_in.setPlaceholderText("Epoch seconds (e.g. 1735000000)")
        b_to_iso = QPushButton("Epoch -> ISO")
        eprow.addWidget(self.epoch_in, 1)
        eprow.addWidget(b_to_iso)
        lay.addLayout(eprow)

        isorow = QHBoxLayout()
        self.iso_in = QLineEdit()
        self.iso_in.setPlaceholderText("ISO time (e.g. 2025-12-24 22:00:00)")
        b_to_epoch = QPushButton("ISO -> Epoch")
        isorow.addWidget(self.iso_in, 1)
        isorow.addWidget(b_to_epoch)
        lay.addLayout(isorow)

        self.time_out = QTextEdit()
        self.time_out.setReadOnly(True)
        lay.addWidget(self.time_out, 1)

        def do_now():
            t = time.time()
            self.now_out.setText(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)))
            self.time_out.setPlainText(f"Epoch: {int(t)}\nISO: {self.now_out.text()}")

        def do_epoch_to_iso():
            try:
                t = float(self.epoch_in.text().strip())
                iso = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
                self.time_out.setPlainText(f"Epoch: {t}\nISO: {iso}")
            except Exception as e:
                QMessageBox.warning(self, "Time error", str(e))

        def do_iso_to_epoch():
            try:
                s = self.iso_in.text().strip()
                # Accept "YYYY-MM-DD HH:MM:SS"
                tt = time.strptime(s, "%Y-%m-%d %H:%M:%S")
                epoch = int(time.mktime(tt))
                self.time_out.setPlainText(f"ISO: {s}\nEpoch: {epoch}")
            except Exception as e:
                QMessageBox.warning(self, "Time error", "Use format: YYYY-MM-DD HH:MM:SS\n\n" + str(e))

        b_now.clicked.connect(do_now)
        b_to_iso.clicked.connect(do_epoch_to_iso)
        b_to_epoch.clicked.connect(do_iso_to_epoch)

        do_now()
        return w
