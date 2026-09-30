"""Selector de hora com relógio analógico (estilo do design do MediSync).

Uso:
    campo = ClockTimeEdit(QTime.currentTime())

Ao clicar no campo (ou no ícone do relógio) abre-se um popup com:
  * um relógio onde se escolhe primeiro a HORA e, a seguir, os MINUTOS;
  * dois seletores numéricos (hora : minuto) com setas para cima/baixo;
  * botões OK / Cancelar.

O campo continua a aceitar digitação normal (HH:mm) pelo teclado.
"""
import math

from PySide6.QtCore import Qt, QEvent, QPointF, QRectF, QTime, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QPushButton,
    QTimeEdit, QToolButton, QVBoxLayout, QWidget,
)

from .icons import qicon

GREEN = QColor("#0f9d63")
GREEN_LIGHT = QColor("#e3f7ec")
FACE = QColor("#eef2f4")
TEXT = QColor("#35516b")
TEXT_SOFT = QColor("#7d93a5")


# ----------------------------------------------------------------------
# Relógio (mostrador)
# ----------------------------------------------------------------------
class ClockFace(QWidget):
    """Mostrador circular. Modo 'hour' (0-23, dois anéis) ou 'minute' (0-59)."""

    changed = Signal()       # hora ou minuto mudaram (clique/arrastar)
    hourPicked = Signal()    # o utilizador largou o rato a escolher a hora

    SIZE = 220
    R_OUTER = 86             # anel exterior: 1..12
    R_INNER = 56             # anel interior: 13..23 e 00
    MARK_R = 17              # raio do círculo verde de seleção

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(self.SIZE, self.SIZE)
        self._hour = 0
        self._minute = 0
        self._mode = "hour"
        self.setCursor(Qt.PointingHandCursor)

    # -- estado ---------------------------------------------------------
    def set_time(self, hour, minute):
        self._hour, self._minute = hour, minute
        self.update()

    def set_mode(self, mode):
        self._mode = mode
        self.update()

    def hour(self):
        return self._hour

    def minute(self):
        return self._minute

    # -- geometria ------------------------------------------------------
    def _center(self):
        return QPointF(self.width() / 2, self.height() / 2)

    def _point(self, angle_deg, radius):
        a = math.radians(angle_deg)
        c = self._center()
        return QPointF(c.x() + radius * math.sin(a), c.y() - radius * math.cos(a))

    def _selection(self):
        """(ângulo, raio) do marcador atual."""
        if self._mode == "hour":
            h = self._hour
            inner = h == 0 or h >= 13
            return (h % 12) * 30, self.R_INNER if inner else self.R_OUTER
        return self._minute * 6, self.R_OUTER

    # -- desenho --------------------------------------------------------
    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        c = self._center()

        p.setPen(Qt.NoPen)
        p.setBrush(FACE)
        p.drawEllipse(c, self.SIZE / 2 - 1, self.SIZE / 2 - 1)

        angle, radius = self._selection()
        marker = self._point(angle, radius)

        # ponteiro
        p.setPen(QPen(GREEN, 2, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(c, marker)
        p.setPen(Qt.NoPen)
        p.setBrush(GREEN)
        p.drawEllipse(c, 4.5, 4.5)

        # círculo de seleção
        p.drawEllipse(marker, self.MARK_R, self.MARK_R)

        # números
        font = QFont(self.font())
        font.setPixelSize(14)
        p.setFont(font)
        selected_label = None
        if self._mode == "hour":
            for i in range(12):
                outer = 12 if i == 0 else i
                inner = 0 if i == 0 else i + 12
                self._draw_label(p, i * 30, self.R_OUTER, str(outer), self._hour == outer, 14)
                self._draw_label(p, i * 30, self.R_INNER, f"{inner:02d}", self._hour == inner, 12)
        else:
            for m in range(0, 60, 5):
                self._draw_label(p, m * 6, self.R_OUTER, f"{m:02d}", self._minute == m, 14)
            if self._minute % 5 != 0:  # minuto "entre" marcas: ponto branco no círculo
                p.setPen(Qt.NoPen)
                p.setBrush(QColor("#ffffff"))
                p.drawEllipse(marker, 2.5, 2.5)
        p.end()

    def _draw_label(self, p, angle, radius, text, selected, px):
        font = QFont(self.font())
        font.setPixelSize(px)
        font.setBold(selected)
        p.setFont(font)
        p.setPen(QColor("#ffffff") if selected else (TEXT if radius == self.R_OUTER else TEXT_SOFT))
        pt = self._point(angle, radius)
        p.drawText(QRectF(pt.x() - 18, pt.y() - 12, 36, 24), Qt.AlignCenter, text)

    # -- rato -----------------------------------------------------------
    def _pick(self, pos):
        c = self._center()
        dx, dy = pos.x() - c.x(), pos.y() - c.y()
        dist = math.hypot(dx, dy)
        angle = math.degrees(math.atan2(dx, -dy)) % 360
        if self._mode == "hour":
            idx = int(round(angle / 30)) % 12
            if dist < (self.R_INNER + self.R_OUTER) / 2:      # anel interior
                self._hour = 0 if idx == 0 else idx + 12
            else:                                             # anel exterior
                self._hour = 12 if idx == 0 else idx
        else:
            self._minute = int(round(angle / 6)) % 60
        self.update()
        self.changed.emit()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._pick(e.position())

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            self._pick(e.position())

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self._mode == "hour":
            self.hourPicked.emit()


# ----------------------------------------------------------------------
# Caixa numérica (seta cima / valor / seta baixo)
# ----------------------------------------------------------------------
class _SpinBox(QFrame):
    stepped = Signal(int)    # +1 / -1
    clicked = Signal()       # clique no número (muda o modo do relógio)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("clockSpin")
        self.setFixedSize(62, 96)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 2, 0, 2)
        lay.setSpacing(0)

        up = QToolButton()
        up.setIcon(qicon("chevron-up", "#0f9d63", 16))
        down = QToolButton()
        down.setIcon(qicon("chevron-down", "#0f9d63", 16))
        for b, step in ((up, 1), (down, -1)):
            b.setObjectName("clockArrow")
            b.setCursor(Qt.PointingHandCursor)
            b.setAutoRaise(True)
            b.setAutoRepeat(True)
            b.clicked.connect(lambda _=False, s=step: self.stepped.emit(s))

        self.value = QPushButton("00")
        self.value.setObjectName("clockValue")
        self.value.setCursor(Qt.PointingHandCursor)
        self.value.setFocusPolicy(Qt.NoFocus)
        self.value.clicked.connect(self.clicked)

        lay.addWidget(up)
        lay.addWidget(self.value, 1)
        lay.addWidget(down)

    def set_value(self, v):
        self.value.setText(f"{v:02d}")

    def set_active(self, active):
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)


# ----------------------------------------------------------------------
# Popup
# ----------------------------------------------------------------------
class ClockPopup(QWidget):
    timeSelected = Signal(QTime)

    _QSS = """
    QFrame#clockCard { background: #ffffff; border: 1px solid #d6e4eb; border-radius: 12px; }
    QFrame#clockSpin { background: #e9f8f0; border-radius: 10px; border: 2px solid transparent; }
    QFrame#clockSpin[active="true"] { border: 2px solid #0f9d63; }
    QToolButton#clockArrow { border: none; background: transparent; min-height: 22px; max-height: 22px; }
    QToolButton#clockArrow:hover { background: #d3f0e1; border-radius: 6px; }
    QPushButton#clockValue { background: transparent; border: none; color: #0f9d63;
                             font-size: 24px; font-weight: 800; min-height: 0px; padding: 0; }
    QLabel#clockColon { font-size: 22px; font-weight: 800; color: #35516b; }
    QPushButton#successButton, QPushButton#secondaryButton { min-height: 34px; max-height: 34px; padding: 0 12px; }
    """

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoMouseReplay)  # o clique que fecha não "re-abre" o popup

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 8, 12, 16)  # espaço para a sombra
        card = QFrame()
        card.setObjectName("clockCard")
        card.setStyleSheet(self._QSS)
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(16, 50, 77, 60))
        card.setGraphicsEffect(shadow)
        outer.addWidget(card)

        row = QHBoxLayout(card)
        row.setContentsMargins(14, 14, 14, 14)
        row.setSpacing(16)

        self.face = ClockFace()
        row.addWidget(self.face, 0, Qt.AlignTop)

        side = QVBoxLayout()
        side.setSpacing(10)
        spins = QHBoxLayout()
        spins.setSpacing(6)
        self.hour_box = _SpinBox()
        self.min_box = _SpinBox()
        colon = QLabel(":")
        colon.setObjectName("clockColon")
        colon.setAlignment(Qt.AlignCenter)
        spins.addWidget(self.hour_box)
        spins.addWidget(colon)
        spins.addWidget(self.min_box)
        side.addLayout(spins)
        side.addStretch(1)

        ok = QPushButton("OK")
        ok.setObjectName("successButton")
        ok.setCursor(Qt.PointingHandCursor)
        ok.setDefault(True)
        cancel = QPushButton("Cancelar")
        cancel.setObjectName("secondaryButton")
        cancel.setCursor(Qt.PointingHandCursor)
        side.addWidget(ok)
        side.addWidget(cancel)
        row.addLayout(side)

        # ligações
        self.face.changed.connect(self._sync_from_face)
        self.face.hourPicked.connect(lambda: self._set_mode("minute"))
        self.hour_box.clicked.connect(lambda: self._set_mode("hour"))
        self.min_box.clicked.connect(lambda: self._set_mode("minute"))
        self.hour_box.stepped.connect(self._step_hour)
        self.min_box.stepped.connect(self._step_minute)
        ok.clicked.connect(self._accept)
        cancel.clicked.connect(self.close)

    # -- API ------------------------------------------------------------
    def open_at(self, anchor, time):
        """Mostra o popup por baixo do widget `anchor` (ou por cima se não couber)."""
        self.face.set_time(time.hour(), time.minute())
        self._refresh_boxes()
        self._set_mode("hour")
        self.adjustSize()

        below = anchor.mapToGlobal(anchor.rect().bottomLeft())
        screen = anchor.screen().availableGeometry()
        x = below.x() - 12
        y = below.y() - 4
        if y + self.height() > screen.bottom():
            y = anchor.mapToGlobal(anchor.rect().topLeft()).y() - self.height() + 4
        x = max(screen.left(), min(x, screen.right() - self.width()))
        self.move(x, max(screen.top(), y))
        self.show()

    # -- interno --------------------------------------------------------
    def _set_mode(self, mode):
        self.face.set_mode(mode)
        self.hour_box.set_active(mode == "hour")
        self.min_box.set_active(mode == "minute")

    def _refresh_boxes(self):
        self.hour_box.set_value(self.face.hour())
        self.min_box.set_value(self.face.minute())

    def _sync_from_face(self):
        self._refresh_boxes()

    def _step_hour(self, step):
        self.face.set_time((self.face.hour() + step) % 24, self.face.minute())
        self._refresh_boxes()
        self._set_mode("hour")

    def _step_minute(self, step):
        self.face.set_time(self.face.hour(), (self.face.minute() + step) % 60)
        self._refresh_boxes()
        self._set_mode("minute")

    def _accept(self):
        self.timeSelected.emit(QTime(self.face.hour(), self.face.minute()))
        self.close()

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._accept()
        elif e.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(e)


# ----------------------------------------------------------------------
# Campo de hora que abre o relógio
# ----------------------------------------------------------------------
class ClockTimeEdit(QTimeEdit):
    """QTimeEdit que abre o ClockPopup ao ser clicado."""

    def __init__(self, time=None, parent=None):
        super().__init__(time if time is not None else QTime.currentTime(), parent)
        self.setDisplayFormat("HH:mm")
        self.setButtonSymbols(QTimeEdit.NoButtons)
        self._popup = ClockPopup(self)
        self._popup.timeSelected.connect(self.setTime)
        # o QTimeEdit tem um QLineEdit interno que é quem recebe o clique
        self.lineEdit().installEventFilter(self)

    def show_clock(self):
        if not self._popup.isVisible():
            self._popup.open_at(self, self.time())

    def eventFilter(self, obj, event):
        if obj is self.lineEdit() and event.type() == QEvent.MouseButtonPress \
                and event.button() == Qt.LeftButton:
            self.show_clock()
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        # cliques fora do QLineEdit (p. ex. no ícone do relógio, à direita)
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.show_clock()

    def keyPressEvent(self, event):
        # Alt+Seta abaixo / F4 abrem o relógio pelo teclado
        if event.key() == Qt.Key_F4 or (
                event.key() == Qt.Key_Down and event.modifiers() & Qt.AltModifier):
            self.show_clock()
            return
        super().keyPressEvent(event)
