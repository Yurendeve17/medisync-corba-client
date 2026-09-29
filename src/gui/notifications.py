"""Componentes de notificação da recepção: painel do sino e aviso (toast)."""
from datetime import datetime

from PySide6.QtCore import QPoint, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .icons import pixmap


def notification_text(notification):
    patient = getattr(notification, "patientName", "") or f"#{notification.patientId}"
    return f"{notification.doctor} chamou o paciente {patient}"


def format_time(created_at):
    try:
        moment = datetime.fromisoformat(str(created_at).replace(" ", "T"))
    except ValueError:
        return str(created_at)

    if moment.date() == datetime.now().date():
        return f"Hoje, {moment:%H:%M}"

    return f"{moment:%d/%m/%Y %H:%M}"


class NotificationPopup(QFrame):
    """Lista de notificações que abre por baixo do sino."""

    read_requested = Signal(int)
    read_all_requested = Signal()

    WIDTH = 400

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.setObjectName("notifPopup")
        self.setFixedWidth(self.WIDTH)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(18, 14, 14, 10)
        title = QLabel("Notificações")
        title.setObjectName("notifTitle")
        self.mark_all_button = QPushButton("Marcar todas como lidas")
        self.mark_all_button.setObjectName("loginLink")
        self.mark_all_button.setCursor(Qt.PointingHandCursor)
        self.mark_all_button.clicked.connect(self.read_all_requested.emit)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.mark_all_button)
        root.addLayout(header)

        rule = QFrame()
        rule.setObjectName("loginRule")
        rule.setFixedHeight(1)
        root.addWidget(rule)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("notifScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setFixedHeight(360)

        self.body = QWidget()
        self.body.setObjectName("notifBody")
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(8, 8, 8, 8)
        self.body_layout.setSpacing(4)
        self.scroll.setWidget(self.body)
        root.addWidget(self.scroll)

    def set_notifications(self, notifications):
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.mark_all_button.setVisible(any(not n.isRead for n in notifications))

        if not notifications:
            empty = QLabel("Sem notificações.")
            empty.setObjectName("cardDescription")
            empty.setAlignment(Qt.AlignCenter)
            self.body_layout.addWidget(empty)
            self.body_layout.addStretch()
            return

        for notification in notifications:
            self.body_layout.addWidget(self._item(notification))
        self.body_layout.addStretch()

    def _item(self, notification):
        button = QPushButton()
        button.setObjectName("notifItem")
        button.setProperty("unread", not notification.isRead)
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(68)

        row = QHBoxLayout(button)
        row.setContentsMargins(12, 8, 12, 8)
        row.setSpacing(12)

        icon = QLabel()
        icon.setObjectName("notifIcon")
        icon.setFixedSize(40, 40)
        icon.setAlignment(Qt.AlignCenter)
        icon.setPixmap(pixmap("stethoscope", "#0f9f64", 20))

        texts = QVBoxLayout()
        texts.setSpacing(2)
        message = QLabel(notification_text(notification))
        message.setObjectName("notifMessage")
        message.setWordWrap(True)
        when = QLabel(format_time(notification.createdAt))
        when.setObjectName("notifTime")
        texts.addWidget(message)
        texts.addWidget(when)

        dot = QLabel()
        dot.setObjectName("notifDot")
        dot.setFixedSize(9, 9)
        dot.setVisible(not notification.isRead)

        row.addWidget(icon)
        row.addLayout(texts, 1)
        row.addWidget(dot)

        for child in (icon, message, when, dot):
            child.setAttribute(Qt.WA_TransparentForMouseEvents)

        if not notification.isRead:
            button.clicked.connect(
                lambda _checked=False, nid=notification.id: self.read_requested.emit(nid)
            )
        return button

    def show_below(self, anchor):
        pos = anchor.mapToGlobal(QPoint(anchor.width() - self.WIDTH + 10, anchor.height() + 8))
        self.move(pos)
        self.show()


class Toast(QFrame):
    """Aviso temporário no canto superior direito."""

    def __init__(self, parent, top_offset=88):
        super().__init__(parent)
        self.setObjectName("toast")
        self.top_offset = top_offset
        self.hide()

        row = QHBoxLayout(self)
        row.setContentsMargins(16, 12, 18, 12)
        row.setSpacing(12)

        icon = QLabel()
        icon.setPixmap(pixmap("bell", "#ffffff", 20))
        icon.setFixedSize(20, 20)
        self.label = QLabel()
        self.label.setObjectName("toastText")
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(320)
        row.addWidget(icon)
        row.addWidget(self.label)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def show_message(self, text, milliseconds=7000):
        self.label.setText(text)
        self.adjustSize()
        parent = self.parentWidget()
        self.move(parent.width() - self.width() - 28, self.top_offset)
        self.show()
        self.raise_()
        self._timer.start(milliseconds)
