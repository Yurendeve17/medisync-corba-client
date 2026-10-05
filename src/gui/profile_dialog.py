from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import (
    QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QVBoxLayout, QWidget,
)

from .icons import pixmap


ROLE_LABELS = {
    "RECEPTION": "Recepção",
    "DOCTOR": "Médico",
    "ADMIN": "Administrador",
}


def _initials(name):
    parts = [p for p in (name or "").split() if p]
    if not parts:
        return "U"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def _avatar(initials, size=72):
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.NoPen)
    painter.setBrush(Qt.GlobalColor.transparent)
    painter.drawEllipse(0, 0, size, size)
    painter.setBrush(Qt.transparent)
    painter.end()

    # O círculo é criado como pixmap para manter o avatar independente do tema.
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.NoPen)
    from PySide6.QtGui import QColor, QFont
    painter.setBrush(QColor("#12b86e"))
    painter.drawEllipse(0, 0, size, size)
    font = QFont(painter.font())
    font.setBold(True)
    font.setPixelSize(int(size * 0.34))
    painter.setFont(font)
    painter.setPen(QColor("#ffffff"))
    painter.drawText(pm.rect(), Qt.AlignCenter, initials)
    painter.end()
    return pm


class ProfileDialog(QDialog):
    """Perfil do utilizador autenticado. Os dados vêm do User retornado pelo CORBA."""

    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setModal(True)
        self.setWindowTitle("Meu perfil")
        self.setMinimumWidth(620)
        self.setObjectName("profileDialog")

        full_name = getattr(user, "fullName", "") or "Utilizador"
        username = getattr(user, "username", "") or "—"
        role = getattr(user, "role", "") or "—"
        role_label = ROLE_LABELS.get(role, role)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 26, 28, 24)
        root.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(16)
        avatar = QLabel()
        avatar.setFixedSize(72, 72)
        avatar.setPixmap(_avatar(_initials(full_name)))
        header.addWidget(avatar)

        titles = QVBoxLayout()
        titles.setSpacing(3)
        title = QLabel(full_name)
        title.setStyleSheet("color: #112746; font-size: 24px; font-weight: 800;")
        sub = QLabel(f"@{username}")
        sub.setStyleSheet("color: #71869b; font-size: 13px; font-weight: 600;")
        status = QLabel("●  Conta activa")
        status.setStyleSheet("color: #0f9f64; font-size: 12px; font-weight: 800;")
        titles.addWidget(title)
        titles.addWidget(sub)
        titles.addWidget(status)
        header.addLayout(titles, 1)
        root.addLayout(header)

        section_title = QLabel("Dados da conta")
        section_title.setStyleSheet("color: #173653; font-size: 15px; font-weight: 800;")
        root.addWidget(section_title)

        card = QFrame()
        card.setObjectName("profileInfoCard")
        grid = QGridLayout(card)
        grid.setContentsMargins(18, 16, 18, 16)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(14)

        self._add_field(grid, 0, 0, "Nome completo", full_name)
        self._add_field(grid, 0, 1, "Utilizador", username)
        self._add_field(grid, 1, 0, "Perfil", role_label)
        self._add_field(grid, 1, 1, "Estado", "Activo")
        root.addWidget(card)

        security = QFrame()
        security.setObjectName("profileSecurityCard")
        sec_layout = QHBoxLayout(security)
        sec_layout.setContentsMargins(16, 14, 16, 14)
        sec_icon = QLabel()
        sec_icon.setFixedSize(24, 24)
        sec_icon.setPixmap(pixmap("shield", "#0f9f64", 22))
        sec_layout.addWidget(sec_icon)
        sec_text = QVBoxLayout()
        sec_text.setSpacing(2)
        sec_title = QLabel("Segurança da conta")
        sec_title.setStyleSheet("color: #173653; font-size: 13px; font-weight: 800;")
        sec_desc = QLabel("A palavra-passe é validada pelo serviço de autenticação do MediSync.")
        sec_desc.setWordWrap(True)
        sec_desc.setStyleSheet("color: #71869b; font-size: 12px;")
        sec_text.addWidget(sec_title)
        sec_text.addWidget(sec_desc)
        sec_layout.addLayout(sec_text, 1)
        root.addWidget(security)

        actions = QHBoxLayout()
        actions.addStretch(1)
        close = QPushButton("Fechar")
        close.setObjectName("secondaryButton")
        close.setFixedHeight(44)
        close.setMinimumWidth(110)
        close.clicked.connect(self.accept)
        actions.addWidget(close)
        root.addLayout(actions)

    @staticmethod
    def _add_field(grid, row, column, label, value):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        key = QLabel(label)
        key.setStyleSheet("color: #7a8fa0; font-size: 11px; font-weight: 700;")
        val = QLabel(str(value))
        val.setWordWrap(True)
        val.setStyleSheet("color: #183651; font-size: 13px; font-weight: 700;")
        layout.addWidget(key)
        layout.addWidget(val)
        grid.addWidget(wrapper, row, column)
