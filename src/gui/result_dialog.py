from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
)

from .icons import pixmap, qicon


class ResultDialog(QDialog):
    """Dialogo visual padronizado para resultados das operações."""

    KIND_CONFIG = {
        "success": ("check", "#0f9f64", "Operação concluída"),
        "error": ("x", "#d94b4b", "Não foi possível concluir"),
        "warning": ("alert", "#e08a17", "Atenção"),
        "info": ("info", "#1688e8", "Informação"),
    }

    def __init__(
        self,
        parent=None,
        kind="success",
        title="Operação concluída",
        message="",
        details=None,
        primary_text="Fechar",
        primary_slot=None,
        secondary_text=None,
        secondary_slot=None,
    ):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setMaximumWidth(680)
        self.setObjectName("resultDialog")

        icon_name, accent, default_title = self.KIND_CONFIG.get(
            kind, self.KIND_CONFIG["info"]
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 26, 28, 24)
        root.setSpacing(18)

        head = QHBoxLayout()
        head.setSpacing(16)

        icon_box = QFrame()
        icon_box.setFixedSize(58, 58)
        icon_box.setStyleSheet(
            f"background: rgba(15, 159, 100, 0.10); border-radius: 29px;"
        )
        icon_layout = QHBoxLayout(icon_box)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel()
        icon_label.setPixmap(pixmap(icon_name, accent, 30))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        head.addWidget(icon_box)

        titles = QVBoxLayout()
        titles.setSpacing(2)
        eyebrow = QLabel(default_title)
        eyebrow.setStyleSheet(
            f"color: {accent}; font-size: 12px; font-weight: 800;"
        )
        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(
            "color: #112746; font-size: 22px; font-weight: 800;"
        )
        titles.addWidget(eyebrow)
        titles.addWidget(title_label)
        head.addLayout(titles, 1)
        root.addLayout(head)

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(
            "color: #526b7e; font-size: 14px; line-height: 1.4;"
        )
        root.addWidget(message_label)

        if details:
            details_frame = QFrame()
            details_frame.setObjectName("resultDetails")
            details_layout = QVBoxLayout(details_frame)
            details_layout.setContentsMargins(16, 14, 16, 14)
            details_layout.setSpacing(10)

            for label, value in details:
                row = QHBoxLayout()
                row.setSpacing(12)
                key = QLabel(str(label))
                key.setStyleSheet(
                    "color: #708598; font-size: 12px; font-weight: 700;"
                )
                val = QLabel(str(value))
                val.setWordWrap(True)
                val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                val.setStyleSheet(
                    "color: #183651; font-size: 13px; font-weight: 700;"
                )
                row.addWidget(key)
                row.addWidget(val, 1)
                details_layout.addLayout(row)
            root.addWidget(details_frame)

        root.addSpacing(2)
        actions = QHBoxLayout()
        actions.addStretch(1)

        if secondary_text:
            secondary = QPushButton(secondary_text)
            secondary.setObjectName("secondaryButton")
            secondary.setFixedHeight(44)
            if secondary_slot:
                secondary.clicked.connect(secondary_slot)
            else:
                secondary.clicked.connect(self.reject)
            actions.addWidget(secondary)

        primary = QPushButton(primary_text)
        primary.setObjectName("successButton" if kind == "success" else "blueButton")
        primary.setFixedHeight(44)
        primary.setMinimumWidth(120)
        if primary_slot:
            primary.clicked.connect(primary_slot)
        else:
            primary.clicked.connect(self.accept)
        actions.addWidget(primary)
        root.addLayout(actions)

    @classmethod
    def show_result(cls, parent, kind, title, message, **kwargs):
        dialog = cls(parent, kind, title, message, **kwargs)
        return dialog.exec()

    @classmethod
    def success(cls, parent, title, message, **kwargs):
        return cls.show_result(parent, "success", title, message, **kwargs)

    @classmethod
    def error(cls, parent, title, message, **kwargs):
        return cls.show_result(parent, "error", title, message, **kwargs)

    @classmethod
    def warning(cls, parent, title, message, **kwargs):
        return cls.show_result(parent, "warning", title, message, **kwargs)

    @classmethod
    def info(cls, parent, title, message, **kwargs):
        return cls.show_result(parent, "info", title, message, **kwargs)
