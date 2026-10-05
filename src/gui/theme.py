"""Tema visual do MediSync.

O tema claro usa style.qss. O tema escuro é aplicado como uma camada de
sobrescrita, permitindo alternar sem reconstruir a interface.
"""
import re
import tempfile
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .icons import pixmap

_TOKEN = re.compile(r"\{\{icon:([\w-]+):(#[0-9a-fA-F]{3,8})\}\}")


def _icon_file(name, color):
    folder = Path(tempfile.gettempdir()) / "medisync_icons"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}_{color.lstrip('#')}.png"
    pixmap(name, color, 16).save(str(path), "PNG")
    return path.as_posix()


DARK_OVERRIDES = r"""
/* ==========================================================
   MediSync — tema escuro
   ========================================================== */
QMainWindow, QWidget#receptionDashboard, QWidget#doctorDashboard,
QWidget#pageCanvas, QScrollArea#pageScroll, QFrame#topbar {
    background: #111827;
    color: #e5e7eb;
}

QLabel#pageTitle, QLabel#cardTitle, QLabel#statValue,
QLabel#formSection, QLabel#fieldLabel {
    color: #f3f4f6;
}

QLabel#pageSubtitle, QLabel#cardDescription, QLabel#statLabel {
    color: #a9b7c7;
}

QFrame#modernCard, QFrame#formCard, QFrame#statCard {
    background: #1f2937;
    border-color: #374151;
}

QFrame#searchBox {
    background: #1f2937;
    border-color: #374151;
}

QLineEdit, QComboBox, QDateEdit, QTimeEdit {
    background: #111827;
    color: #e5e7eb;
    border-color: #4b5563;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus {
    background: #172033;
    border-color: #2ad4a6;
}

QLineEdit[readOnly="true"] {
    background: #273244;
    color: #a9b7c7;
}

QComboBox QAbstractItemView {
    background: #1f2937;
    color: #e5e7eb;
    border-color: #4b5563;
    selection-background-color: #174d3b;
    selection-color: #ffffff;
}

QPushButton#secondaryButton {
    background: #1f2937;
    color: #dbe5ee;
    border-color: #4b5563;
}

QPushButton#secondaryButton:hover {
    background: #273244;
}

QTableWidget {
    background: #1f2937;
    color: #e5e7eb;
    border-color: #374151;
    gridline-color: #374151;
    alternate-background-color: #243142;
    selection-background-color: #17513e;
    selection-color: #ffffff;
}

QHeaderView::section {
    background: #273244;
    color: #cbd5e1;
    border-bottom-color: #374151;
}

QTableWidget::item {
    color: #e5e7eb;
    border-bottom-color: #374151;
}

QPushButton#backButton {
    color: #a9b7c7;
}

QLabel#userName {
    color: #f3f4f6;
}

QLabel#userRole {
    color: #9fb0c1;
}

QMenu, QMenu#profileMenu {
    background: #1f2937;
    color: #e5e7eb;
    border: 1px solid #374151;
}

QMenu::item {
    color: #e5e7eb;
}

QMenu::item:selected {
    background: #174d3b;
}

QToolButton#topIconButton:hover {
    background: #273244;
}

QFrame#topSeparator {
    background: #374151;
}

QPushButton#userChip:hover, QToolButton#profileButton:hover {
    background: #273244;
}

QToolButton#profileButton {
    color: #e5e7eb;
}

QMenu#profileMenu {
    background: #1f2937;
    color: #e5e7eb;
    border-color: #374151;
}

QMenu#profileMenu::item {
    color: #e5e7eb;
}

QMenu#profileMenu::item:selected {
    background: #174d3b;
    color: #8ee8c6;
}

QFrame#nextPatientBox {
    background: #173b31;
    border-color: #285c4d;
}

QLabel#callStatus {
    background: #173b31;
    color: #8ee8c6;
    border-color: #285c4d;
}

QFrame#notifPopup {
    background: #1f2937;
    border-color: #374151;
}

QLabel#notifTitle, QLabel#notifMessage {
    color: #f3f4f6;
}

QLabel#notifTime {
    color: #9fb0c1;
}

QPushButton#notifItem:hover {
    background: #273244;
}

QPushButton#notifItem[unread="true"] {
    background: #173b31;
}

QToolTip {
    background: #f3f4f6;
    color: #111827;
}

QToolButton#loginTheme {
    background: #ffffff;
    border: 1px solid #e3ebf0;
    border-radius: 12px;
}

QToolButton#loginTheme:hover {
    background: #f4f9f8;
}

QToolButton#loginTheme {
    background: #1f2937;
    border-color: #374151;
}

QToolButton#loginTheme:hover {
    background: #273244;
}

QLabel#loginWelcome, QLabel#loginFieldLabel {
    color: #f3f4f6;
}

QLabel#loginWelcomeSub {
    color: #a9b7c7;
}

QLineEdit#loginInput {
    background: #111827;
    color: #e5e7eb;
    border-color: #4b5563;
}

QFrame#loginRule {
    background: #374151;
}

QLabel#loginOr {
    color: #a9b7c7;
}

QPushButton#loginSecondary {
    background: #173b31;
    color: #8ee8c6;
    border-color: #2b8f70;
}
"""


def load_stylesheet(qss_path):
    text = Path(qss_path).read_text(encoding="utf-8")
    return _TOKEN.sub(lambda m: _icon_file(m.group(1), m.group(2)), text)


def apply_theme(app=None, dark=False):
    app = app or QApplication.instance()
    if app is None:
        return
    base = load_stylesheet(Path(__file__).resolve().parent / "style.qss")
    app.setStyleSheet(base + ("\n" + DARK_OVERRIDES if dark else ""))
    app.setProperty("medisync_dark_mode", bool(dark))


def is_dark(app=None):
    app = app or QApplication.instance()
    return bool(app and app.property("medisync_dark_mode"))


def toggle_theme(window=None):
    app = QApplication.instance()
    if app is None:
        return
    dark = not is_dark(app)
    apply_theme(app, dark)
    if window is not None:
        window.setProperty("medisync_dark_mode", dark)
        window.style().unpolish(window)
        window.style().polish(window)
