from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    # Base palette
    bg0: str = "#070b12"     # main background
    bg1: str = "#0b1220"     # secondary background
    panel: str = "#0f1a2d"   # panels / inputs
    panel2: str = "#0b1424"  # deeper panels
    line: str = "#1a2f4f"    # borders / lines
    text: str = "#dbe8ff"    # primary text
    text_dim: str = "#93add6"
    accent: str = "#3aa3ff"
    danger: str = "#ff476f"
    ok: str = "#2cffc8"


THEME = Theme()


def qss(theme: Theme) -> str:
    # QSS must be entirely inside this string. No QSS should exist below the closing triple quote.
    return f"""
/* =========================
   Base
   ========================= */
QWidget {{
    background-color: {theme.bg0};
    color: {theme.text};
    font-family: Segoe UI;
    font-size: 10pt;
}}

QMainWindow {{
    background-color: {theme.bg0};
}}

/* =========================
   Labels
   ========================= */
QLabel {{
    color: {theme.text};
}}
QLabel#Dim {{
    color: {theme.text_dim};
}}

/* =========================
   Buttons
   ========================= */
QPushButton {{
    background-color: {theme.panel};
    color: {theme.text};
    border: 1px solid {theme.line};
    border-radius: 8px;
    padding: 7px 12px;
}}
QPushButton:hover {{
    background-color: {theme.panel2};
    border-color: {theme.accent};
}}
QPushButton:pressed {{
    background-color: {theme.bg1};
    border-color: {theme.accent};
}}
QPushButton:disabled {{
    color: {theme.text_dim};
    border-color: {theme.line};
    background-color: {theme.panel2};
}}

/* Accent button (optional) */
QPushButton#Accent {{
    background-color: {theme.accent};
    color: #06111f;
    border: 1px solid {theme.accent};
}}
QPushButton#Accent:hover {{
    filter: none; /* Qt ignores filter, harmless */
}}
QPushButton#Accent:pressed {{
    background-color: {theme.ok};
    border-color: {theme.ok};
}}

/* Danger button (optional) */
QPushButton#Danger {{
    background-color: {theme.danger};
    color: #1a0006;
    border: 1px solid {theme.danger};
}}

/* =========================
   Inputs
   ========================= */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {theme.panel};
    color: {theme.text};
    border: 1px solid {theme.line};
    border-radius: 8px;
    padding: 6px 8px;
    selection-background-color: {theme.accent};
    selection-color: #06111f;
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {theme.accent};
}}

QComboBox {{
    background-color: {theme.panel};
    color: {theme.text};
    border: 1px solid {theme.line};
    border-radius: 8px;
    padding: 6px 10px;
}}
QComboBox:hover {{
    border-color: {theme.accent};
}}
QComboBox::drop-down {{
    border: 0px;
    width: 28px;
}}
QComboBox QAbstractItemView {{
    background-color: {theme.bg1};
    color: {theme.text};
    border: 1px solid {theme.line};
    selection-background-color: {theme.accent};
    selection-color: #06111f;
}}

/* =========================
   Lists / Trees / Tables
   ========================= */
QListWidget, QTreeWidget, QTableWidget {{
    background-color: {theme.bg1};
    color: {theme.text};
    border: 1px solid {theme.line};
    border-radius: 10px;
}}
QHeaderView::section {{
    background-color: {theme.panel2};
    color: {theme.text};
    border: 1px solid {theme.line};
    padding: 6px 8px;
}}
QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {{
    background-color: {theme.accent};
    color: #06111f;
}}

/* =========================
   Tabs (Inner tool tabs)
   ========================= */
QTabWidget#InnerTabs::pane {{
    border: 1px solid {theme.line};
    border-radius: 10px;
    padding: 6px;
    background: {theme.bg1};
}}

QTabBar::tab {{
    background: {theme.panel2};
    color: {theme.text};
    padding: 8px 12px;
    border: 1px solid {theme.line};
    border-bottom: none;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 6px;
}}

QTabBar::tab:selected {{
    background: {theme.bg1};
    border-color: {theme.accent};
}}

QTabBar::tab:hover {{
    background: {theme.panel};
}}

/* =========================
   Cards used inside pages
   ========================= */
QFrame#Card {{
    background: {theme.panel2};
    border: 1px solid {theme.line};
    border-radius: 14px;
}}

/* =========================
   Scrollbars
   ========================= */
QScrollBar:vertical {{
    background: {theme.bg1};
    width: 10px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: {theme.line};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {theme.accent};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: {theme.bg1};
    height: 10px;
    margin: 0px;
}}
QScrollBar::handle:horizontal {{
    background: {theme.line};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {theme.accent};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* =========================
   Tooltips
   ========================= */
QToolTip {{
    background-color: {theme.panel};
    color: {theme.text};
    border: 1px solid {theme.line};
    padding: 6px;
}}
"""
