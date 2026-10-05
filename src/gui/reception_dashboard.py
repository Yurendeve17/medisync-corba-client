import re
from PySide6.QtCore import Qt, QDateTime, QEvent, QObject, QPoint, QPointF, QRect, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QMessageBox, QHeaderView,
    QStackedWidget, QDateEdit, QToolButton, QSizePolicy, QMenu,
    QScrollArea, QGraphicsDropShadowEffect, QDialog, QDialogButtonBox,
)

from .icons import pixmap, qicon, illustration
from .notifications import NotificationPopup, Toast, notification_text
from .profile_dialog import ProfileDialog
from .result_dialog import ResultDialog

# ----------------------------------------------------------------------
# Medidas do layout (um único sítio para manter tudo harmónico)
# ----------------------------------------------------------------------
SIDEBAR_W = 232
NOTIF_POLL_MS = 8000     # de quanto em quanto tempo a recepção verifica novas chamadas
TOPBAR_H = 72
PAGE_MAX_W = 1000        # largura máxima do conteúdo (cabeçalho e cartão alinhados)
TABLE_MAX_W = 1040
FIELD_H = 42             # altura única de todos os campos
ROW_GAP = 10             # espaço vertical entre linhas do formulário
COL_GAP = 16             # espaço horizontal entre etiqueta e campo
LABEL_W_SHORT = 76       # coluna de etiquetas: Agendar consulta
LABEL_W_LONG = 162       # coluna de etiquetas: Registar paciente


def _repolish(widget):
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def _initials(name):
    parts = [p for p in (name or "").split() if p]
    if not parts:
        return "U"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def _avatar(initials, size=38):
    dpr = 2
    pm = QPixmap(size * dpr, size * dpr)
    pm.setDevicePixelRatio(dpr)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor("#12b86e"))
    p.drawEllipse(0, 0, size, size)
    font = QFont(p.font())
    font.setBold(True)
    font.setPixelSize(int(size * 0.36))
    p.setFont(font)
    p.setPen(QColor("#ffffff"))
    p.drawText(QRect(0, 0, size, size), Qt.AlignCenter, initials)
    p.end()
    return pm


class _IconOverlay(QObject):
    """Ícone decorativo desenhado dentro de um campo (esquerda ou direita)."""

    def __init__(self, host, icon_name, color="#5b7a90", side="left", size=18, margin=14):
        super().__init__(host)
        self.host, self.side, self.size, self.margin = host, side, size, margin
        self.label = QLabel(host)
        self.label.setPixmap(pixmap(icon_name, color, size))
        self.label.setFixedSize(size, size)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        host.installEventFilter(self)
        self._place()

    def _place(self):
        x = self.margin if self.side == "left" else self.host.width() - self.size - self.margin
        self.label.move(x, (self.host.height() - self.size) // 2)
        self.label.raise_()

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Resize, QEvent.Show):
            self._place()
        return False


class _WheelGuard(QObject):
    """Evita que a roda do rato altere combos/datas ao fazer scroll na página."""

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel and not obj.hasFocus():
            event.ignore()
            return True  # o Qt reencaminha o evento ignorado para o QScrollArea
        return False


class NavItem(QPushButton):
    """Item do menu lateral (ícone + texto + chevron opcional)."""

    def __init__(self, icon_name, text, sub=False, expandable=False):
        super().__init__()
        self.icon_name = icon_name
        self.setObjectName("navSub" if sub else "navItem")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(44)
        self.setProperty("active", False)
        self.setProperty("group", expandable)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(26 if sub else 14, 0, 10, 0)
        lay.setSpacing(12)
        self._icon = QLabel()
        self._icon.setFixedSize(20, 20)
        self._text = QLabel(text)
        self._text.setObjectName("navLabel")
        lay.addWidget(self._icon)
        lay.addWidget(self._text, 1)
        self._chevron = None
        if expandable:
            self._chevron = QLabel()
            self._chevron.setFixedSize(16, 16)
            lay.addWidget(self._chevron)
            self.set_expanded(True)
        for w in (self._icon, self._text, self._chevron):
            if w is not None:
                w.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._refresh_icon()

    def _refresh_icon(self):
        bright = self.property("active") or self.property("group")
        self._icon.setPixmap(pixmap(self.icon_name, "#ffffff" if bright else "#bcd6d0", 20))

    def set_active(self, active):
        self.setProperty("active", bool(active))
        for w in (self, self._text):
            _repolish(w)
        self._refresh_icon()

    def set_expanded(self, expanded):
        if self._chevron is not None:
            self._chevron.setPixmap(pixmap("chevron-up" if expanded else "chevron-down", "#dff3ec", 16))


class Sidebar(QFrame):
    """Barra lateral com as ondas decorativas no fundo (como no design)."""

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        for base, amp, color in ((h - 70, 26, QColor(20, 170, 105, 55)), (h - 42, 20, QColor(12, 120, 80, 90))):
            path = QPainterPath(QPointF(0, h))
            path.lineTo(0, base)
            path.cubicTo(w * 0.30, base - amp * 1.6, w * 0.60, base + amp, w, base - amp * 0.6)
            path.lineTo(w, h)
            path.closeSubpath()
            p.fillPath(path, color)
        p.end()


class ReceptionDashboard(QWidget):
    """Interface da recepção: layout responsivo e serviços CORBA existentes."""

    def __init__(self, app, stack, logout_callback=None):
        super().__init__()
        self.app = app
        self.stack = stack
        self.logout_callback = logout_callback
        self.current_user = None
        self.setObjectName("receptionDashboard")
        self.content_stack = QStackedWidget()
        self.nav_buttons = []
        self._wheel_guard = _WheelGuard(self)
        self._notifications = []
        self._notif_last_id = 0
        self._notif_primed = False
        self._notif_error_shown = False
        self._build_shell()
        self._build_pages()
        self._build_notifications()
        self.show_page(0)
        self.load_patients()
        self.load_appointments()
        self.load_directory()

    # ------------------------------------------------------------------
    # Shell (menu lateral + barra superior)
    # ------------------------------------------------------------------
    def _build_shell(self):
        shell = QHBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)
        shell.addWidget(self._build_sidebar())

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)
        right.addWidget(self._build_topbar())
        right.addWidget(self.content_stack, 1)
        shell.addLayout(right, 1)

    def _build_sidebar(self):
        sidebar = Sidebar()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(SIDEBAR_W)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(14, 22, 14, 18)
        side.setSpacing(4)

        logo_row = QHBoxLayout()
        logo_row.setContentsMargins(6, 0, 0, 0)
        logo_row.setSpacing(10)
        logo_icon = QLabel()
        logo_icon.setPixmap(pixmap("logo", "#12b86e", 42))
        logo_icon.setFixedSize(42, 42)
        logo_texts = QVBoxLayout()
        logo_texts.setSpacing(0)
        logo_text = QLabel("MediSync")
        logo_text.setObjectName("logo")
        logo_sub = QLabel("Sistema Hospitalar")
        logo_sub.setObjectName("logoSubtitle")
        logo_texts.addWidget(logo_text)
        logo_texts.addWidget(logo_sub)
        logo_row.addWidget(logo_icon)
        logo_row.addLayout(logo_texts, 1)
        side.addLayout(logo_row)
        side.addSpacing(16)
        side.addWidget(self._sidebar_divider())
        side.addSpacing(12)

        self._nav_item(side, "home", "Início", 0)
        self.reception_group = NavItem("users", "Recepção", expandable=True)
        self.reception_group.clicked.connect(self._toggle_reception_group)
        side.addWidget(self.reception_group)
        self.reception_sub = QWidget()
        sub_l = QVBoxLayout(self.reception_sub)
        sub_l.setContentsMargins(0, 0, 0, 0)
        sub_l.setSpacing(4)
        self._nav_item(sub_l, "calendar", "Agendar consulta", 1, sub=True)
        self._nav_item(sub_l, "user", "Registar paciente", 2, sub=True)
        side.addWidget(self.reception_sub)
        self._nav_item(side, "users", "Pacientes", 3)
        self._nav_item(side, "calendar", "Consultas", 4)
        self._nav_item(side, "stethoscope", "Médicos", 5)
        self._nav_item(side, "bar-chart", "Relatórios", 6)
        self._nav_item(side, "settings", "Configurações", 7)
        side.addStretch(1)

        footer = QVBoxLayout()
        footer.setContentsMargins(6, 0, 0, 34)
        footer.setSpacing(6)
        footer_icon = QLabel()
        footer_icon.setPixmap(pixmap("heart-pulse", "#21d487", 30))
        footer_text = QLabel("Cuidando de pessoas,\ntodos os dias.")
        footer_text.setObjectName("sidebarFooter")
        footer.addWidget(footer_icon)
        footer.addWidget(footer_text)
        side.addLayout(footer)
        return sidebar

    def _sidebar_divider(self):
        line = QFrame()
        line.setObjectName("sidebarDivider")
        line.setFixedHeight(1)
        return line

    def _nav_item(self, layout, icon_name, text, index, sub=False):
        item = NavItem(icon_name, text, sub=sub)
        item.clicked.connect(lambda _=False, i=index: self.show_page(i))
        self.nav_buttons.append((index, item))
        layout.addWidget(item)
        return item

    def _toggle_reception_group(self):
        expanded = not self.reception_sub.isVisible()
        self.reception_sub.setVisible(expanded)
        self.reception_group.set_expanded(expanded)

    def _build_topbar(self):
        header = QFrame()
        header.setObjectName("topbar")
        header.setFixedHeight(TOPBAR_H)
        h = QHBoxLayout(header)
        h.setContentsMargins(28, 0, 28, 0)
        h.setSpacing(10)

        h.addStretch(1)

        self.bell_button = QToolButton()
        self.bell_button.setObjectName("topIconButton")
        self.bell_button.setIcon(qicon("bell", "#466277", 20))
        self.bell_button.setFixedSize(40, 40)
        self.bell_button.setCursor(Qt.PointingHandCursor)
        self.bell_button.setToolTip("Notificações")
        self.notification_badge = QLabel("0", self.bell_button)
        self.notification_badge.setObjectName("notifBadge")
        self.notification_badge.setAlignment(Qt.AlignCenter)
        self.notification_badge.setGeometry(22, 3, 16, 16)
        self.notification_badge.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.notification_badge.hide()
        h.addWidget(self.bell_button)


        h.addSpacing(6)
        separator = QFrame()
        separator.setObjectName("topSeparator")
        separator.setFixedSize(1, 34)
        h.addWidget(separator)
        h.addSpacing(6)

        self.profile_button = QPushButton()
        self.profile_button.setObjectName("userChip")
        self.profile_button.setCursor(Qt.PointingHandCursor)
        self.profile_button.setFixedHeight(52)
        chip = QHBoxLayout(self.profile_button)
        chip.setContentsMargins(8, 0, 8, 0)
        chip.setSpacing(10)
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(38, 38)
        self.avatar_label.setPixmap(_avatar("U"))
        names = QVBoxLayout()
        names.setSpacing(0)
        names.setContentsMargins(0, 0, 0, 0)
        self.user_name_label = QLabel("Utilizador")
        self.user_name_label.setObjectName("userName")
        self.user_role_label = QLabel("Recepção")
        self.user_role_label.setObjectName("userRole")
        names.addStretch(1)
        names.addWidget(self.user_name_label)
        names.addWidget(self.user_role_label)
        names.addStretch(1)
        chevron = QLabel()
        chevron.setPixmap(pixmap("chevron-down", "#6b8194", 14))
        chevron.setFixedSize(14, 14)
        chip.addWidget(self.avatar_label)
        chip.addLayout(names)
        chip.addWidget(chevron)
        for w in (self.avatar_label, self.user_name_label, self.user_role_label, chevron):
            w.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.profile_menu = QMenu(self.profile_button)
        self.profile_menu.setObjectName("profileMenu")
        self.profile_action = self.profile_menu.addAction(qicon("user", "#0ca466", 16), "Meu perfil")
        self.profile_action.triggered.connect(self.show_profile)
        self.profile_menu.addSeparator()
        self.logout_action = self.profile_menu.addAction(qicon("logout", "#d14d4d", 16), "Terminar sessão")
        self.logout_action.triggered.connect(self.request_logout)
        self.profile_button.clicked.connect(self._open_profile_menu)
        h.addWidget(self.profile_button)
        return header

    def eventFilter(self, obj, event):
        return super().eventFilter(obj, event)

    def _open_profile_menu(self):
        width = self.profile_menu.sizeHint().width()
        pos = self.profile_button.mapToGlobal(QPoint(self.profile_button.width() - width, self.profile_button.height() + 4))
        self.profile_menu.exec(pos)

    def set_notification_count(self, count):
        self.notification_badge.setText("9+" if count > 9 else str(count))
        self.notification_badge.setVisible(count > 0)

    # ------------------------------------------------------------------
    # Notificações (chamadas de pacientes feitas pelos médicos)
    # ------------------------------------------------------------------
    def _build_notifications(self):
        self.notification_popup = NotificationPopup(self)
        self.notification_popup.read_requested.connect(self._mark_notification_read)
        self.notification_popup.read_all_requested.connect(self._mark_all_notifications_read)
        self.toast = Toast(self, top_offset=TOPBAR_H + 16)
        self.bell_button.clicked.connect(self.show_notifications)

        self._notif_timer = QTimer(self)
        self._notif_timer.timeout.connect(self.refresh_notifications)
        self._notif_timer.start(NOTIF_POLL_MS)

    def show_notifications(self):
        self.refresh_notifications()
        self.notification_popup.set_notifications(self._notifications)
        self.notification_popup.show_below(self.bell_button)

    def refresh_notifications(self):
        # sem sessão activa (p. ex. depois do logout) não consulta o servidor
        if self.current_user is None or getattr(self.app, "current_user", None) is None:
            return

        try:
            items = self.app.list_notifications()
        except Exception as error:
            # o servidor pode ainda não ter o NotificationService: avisa só uma vez
            if not self._notif_error_shown:
                print("ERRO AO CARREGAR NOTIFICAÇÕES:", type(error).__name__, repr(error), flush=True)
                self._notif_error_shown = True
            return
        self._notif_error_shown = False

        items = sorted(items, key=lambda n: n.id, reverse=True)
        self._notifications = items
        self.set_notification_count(sum(1 for n in items if not n.isRead))

        # aviso apenas para chamadas novas (no 1.º carregamento após o login não avisa)
        if self._notif_primed:
            fresh = [n for n in items if n.id > self._notif_last_id and not n.isRead]
            if len(fresh) == 1:
                self.toast.show_message(notification_text(fresh[0]))
            elif fresh:
                self.toast.show_message(f"{len(fresh)} novas chamadas de pacientes")

        self._notif_last_id = max([self._notif_last_id] + [n.id for n in items])
        self._notif_primed = True

        if self.notification_popup.isVisible():
            self.notification_popup.set_notifications(items)

    def _mark_notification_read(self, notification_id):
        try:
            self.app.mark_notification_read(notification_id)
        except Exception as error:
            self.show_error(f"Não foi possível marcar a notificação como lida:\n{error}")
        self.refresh_notifications()

    def _mark_all_notifications_read(self):
        try:
            self.app.mark_all_notifications_read()
        except Exception as error:
            self.show_error(f"Não foi possível marcar as notificações como lidas:\n{error}")
        self.refresh_notifications()

    def set_current_user(self, user):
        self.current_user = user
        full_name = getattr(user, "fullName", "") or getattr(user, "username", "Utilizador")
        username = getattr(user, "username", "")
        role = getattr(user, "role", "")
        role_label = {"RECEPTION": "Recepção", "DOCTOR": "Médico"}.get(role, role or "Utilizador")
        self.user_name_label.setText(full_name)
        self.user_role_label.setText(role_label)
        self.avatar_label.setPixmap(_avatar(_initials(full_name)))
        self.profile_button.setToolTip(f"{full_name} ({username})")

        # nova sessão: recomeça o controlo de chamadas já vistas
        self._notif_primed = False
        self._notif_last_id = 0
        self.refresh_notifications()

    def show_profile(self):
        user = self.current_user or getattr(self.app, "current_user", None)
        if user is None:
            return
        full_name = getattr(user, "fullName", "")
        username = getattr(user, "username", "")
        role = getattr(user, "role", "")
        role_label = {"RECEPTION": "Recepção", "DOCTOR": "Médico"}.get(role, role or "Utilizador")
        ProfileDialog(user, self).exec()

    def request_logout(self):
        if self.logout_callback:
            self.logout_callback()

    def accept_result_navigation(self):
        # Mantido como ponto de extensão para acções futuras dos diálogos de resultado.
        self.load_patients()

    # ------------------------------------------------------------------
    # Estrutura comum das páginas
    # ------------------------------------------------------------------
    def _build_pages(self):
        self.content_stack.addWidget(self._home_page())
        self.content_stack.addWidget(self._appointment_page())
        self.content_stack.addWidget(self._register_page())
        self.content_stack.addWidget(self._patients_page())
        self.content_stack.addWidget(self._appointments_page())
        self.content_stack.addWidget(self._doctors_page())
        self.content_stack.addWidget(self._placeholder_page("bar-chart", "Relatórios", "Indicadores e relatórios do hospital."))
        self.content_stack.addWidget(self._placeholder_page("settings", "Configurações", "Preferências do sistema."))

    def _scaffold(self, max_width=PAGE_MAX_W):
        """Página com scroll vertical e conteúdo centrado (cabeçalho e cartão alinhados).

        Se o ecrã for pequeno, aparece scroll em vez de os widgets se sobreporem.
        """
        scroll = QScrollArea()
        scroll.setObjectName("pageScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        canvas = QWidget()
        canvas.setObjectName("pageCanvas")
        outer = QHBoxLayout(canvas)
        outer.setContentsMargins(32, 12, 32, 20)
        outer.setSpacing(0)

        container = QWidget()
        container.setMaximumWidth(max_width)
        col = QVBoxLayout(container)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(12)

        outer.addStretch(1)
        outer.addWidget(container, 100)
        outer.addStretch(1)
        scroll.setWidget(canvas)
        return scroll, col

    def _page_header(self, icon_name, title, subtitle, back=True, art=None):
        wrapper = QWidget()
        outer = QVBoxLayout(wrapper)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)
        if back:
            back_btn = QPushButton("Voltar para o início")
            back_btn.setObjectName("backButton")
            back_btn.setCursor(Qt.PointingHandCursor)
            back_btn.setIcon(qicon("arrow-left", "#49667d", 15))
            back_btn.clicked.connect(lambda: self.show_page(0))
            outer.addWidget(back_btn, 0, Qt.AlignLeft)

        hero = QHBoxLayout()
        hero.setContentsMargins(0, 0, 0, 0)
        hero.setSpacing(18)
        icon_box = QLabel()
        icon_box.setObjectName("heroIcon")
        icon_box.setPixmap(pixmap(icon_name, "#ffffff", 34))
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setFixedSize(72, 72)
        texts = QVBoxLayout()
        texts.setSpacing(4)
        texts.addStretch(1)
        t = QLabel(title)
        t.setObjectName("pageTitle")
        s = QLabel(subtitle)
        s.setObjectName("pageSubtitle")
        s.setWordWrap(True)
        texts.addWidget(t)
        texts.addWidget(s)
        texts.addStretch(1)
        hero.addWidget(icon_box, 0, Qt.AlignVCenter)
        hero.addLayout(texts, 1)
        if art:
            art_label = QLabel()
            art_label.setPixmap(illustration(art, 132, 84))
            art_label.setFixedSize(132, 84)
            hero.addWidget(art_label, 0, Qt.AlignVCenter)
        outer.addLayout(hero)
        return wrapper

    def _card(self, margins=(28, 18, 28, 22)):
        card = QFrame()
        card.setObjectName("formCard")
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(16, 50, 77, 24))
        card.setGraphicsEffect(shadow)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(*margins)
        lay.setSpacing(0)
        return card, lay

    def _section(self, icon_name, text):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(10)
        i = QLabel()
        i.setObjectName("sectionIcon")
        i.setPixmap(pixmap(icon_name, "#0c9a5e", 18))
        i.setFixedSize(32, 32)
        i.setAlignment(Qt.AlignCenter)
        t = QLabel(text)
        t.setObjectName("formSection")
        l.addWidget(i)
        l.addWidget(t)
        l.addStretch()
        return w

    def _divider(self):
        line = QFrame()
        line.setObjectName("formDivider")
        line.setFixedHeight(1)
        return line

    def _section_header(self, lay, icon_name, text, first=False):
        """Título de secção + linha separadora, sempre com o mesmo ritmo vertical."""
        if not first:
            lay.addSpacing(12)
            lay.addWidget(self._divider())
            lay.addSpacing(12)
        lay.addWidget(self._section(icon_name, text))
        if first:
            lay.addSpacing(8)
            lay.addWidget(self._divider())
            lay.addSpacing(10)
        else:
            lay.addSpacing(10)

    # ------------------------------------------------------------------
    # Helpers de campos
    # ------------------------------------------------------------------
    def _field(self, placeholder, icon=None):
        e = QLineEdit()
        e.setPlaceholderText(placeholder)
        e.setFixedHeight(FIELD_H)
        e.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if icon:
            e.addAction(qicon(icon, "#5b7a90", 18), QLineEdit.LeadingPosition)
        return e

    def _combo(self, icon=None, editable=False):
        c = QComboBox()
        c.setEditable(editable)
        c.setFixedHeight(FIELD_H)
        c.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._guard(c)
        if icon:
            c.setProperty("leftIcon", True)
            _IconOverlay(c, icon, "#0c9a5e", side="left")
        return c

    def _guard(self, widget):
        widget.setFocusPolicy(Qt.StrongFocus)
        widget.installEventFilter(self._wheel_guard)

    def _label(self, text):
        l = QLabel(text)
        l.setObjectName("fieldLabel")
        return l

    def _form_row(self, label, widget, label_w):
        """Etiqueta à esquerda (largura fixa) + campo — colunas sempre alinhadas."""
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(COL_GAP)
        lab = self._label(label)
        lab.setFixedSize(label_w, FIELD_H)
        row.addWidget(lab)
        row.addWidget(widget, 1)
        return row

    def _stack(self, label, widget):
        """Etiqueta por cima do campo."""
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(5)
        l.addWidget(self._label(label))
        l.addWidget(widget)
        return w

    def _actions(self, primary_text, primary_icon, primary_slot, clear_slot):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)
        primary = QPushButton("  " + primary_text)
        primary.setObjectName("successButton")
        primary.setIcon(qicon(primary_icon, "#ffffff", 18))
        primary.setMinimumWidth(200)
        primary.setFixedHeight(44)
        primary.setCursor(Qt.PointingHandCursor)
        primary.clicked.connect(primary_slot)
        clear = QPushButton("  Limpar")
        clear.setObjectName("secondaryButton")
        clear.setIcon(qicon("trash", "#496276", 18))
        clear.setMinimumWidth(130)
        clear.setFixedHeight(44)
        clear.setCursor(Qt.PointingHandCursor)
        clear.clicked.connect(clear_slot)
        row.addWidget(primary)
        row.addWidget(clear)
        row.addStretch(1)
        return row

    def _table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.setMinimumHeight(260)
        return table

    # ------------------------------------------------------------------
    # Páginas
    # ------------------------------------------------------------------
    def _home_page(self):
        scroll, col = self._scaffold()
        col.addWidget(self._page_header("users", "Área da Recepção", "Gestão de pacientes e atendimento hospitalar", back=False, art="users"))
        grid = QHBoxLayout()
        grid.setSpacing(20)
        grid.addWidget(self._action_card("calendar", "Agendar consulta", "Marque uma consulta para um paciente já cadastrado.", "Agendar consulta", 1, "successButton"), 1)
        grid.addWidget(self._action_card("user-plus", "Registar paciente", "Adicione um novo paciente ao sistema.", "Registar paciente", 2, "blueButton"), 1)
        col.addLayout(grid)
        stats = QHBoxLayout()
        stats.setSpacing(20)
        self.home_patient_stat = self._stat_card("users", "Pacientes", "0")
        self.home_appointment_stat = self._stat_card("calendar", "Consultas", "0")
        stats.addWidget(self.home_patient_stat, 1)
        stats.addWidget(self.home_appointment_stat, 1)
        col.addLayout(stats)
        col.addStretch(1)
        return scroll

    def _action_card(self, icon_name, title, desc, button_text, page_index, button_style):
        card, lay = self._card((26, 24, 26, 24))
        card.setMinimumHeight(215)
        lay.setSpacing(10)
        ic = QLabel()
        ic.setObjectName("cardIcon")
        ic.setPixmap(pixmap(icon_name, "#07945b", 25))
        ic.setAlignment(Qt.AlignCenter)
        ic.setFixedSize(54, 54)
        lay.addWidget(ic, alignment=Qt.AlignLeft)
        t = QLabel(title)
        t.setObjectName("cardTitle")
        d = QLabel(desc)
        d.setObjectName("cardDescription")
        d.setWordWrap(True)
        lay.addWidget(t)
        lay.addWidget(d)
        lay.addStretch()
        b = QPushButton("  " + button_text)
        b.setObjectName(button_style)
        b.setCursor(Qt.PointingHandCursor)
        b.setIcon(qicon("calendar" if page_index == 1 else "user-plus", "#ffffff", 18))
        b.clicked.connect(lambda: self.show_page(page_index))
        b.setFixedHeight(46)
        lay.addWidget(b)
        return card

    def _stat_card(self, icon_name, title, value):
        card = QFrame()
        card.setObjectName("statCard")
        card.setFixedHeight(84)
        lay = QHBoxLayout(card)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(14)
        ic = QLabel()
        ic.setObjectName("statIcon")
        ic.setPixmap(pixmap(icon_name, "#0aa365", 21))
        ic.setAlignment(Qt.AlignCenter)
        ic.setFixedSize(46, 46)
        lay.addWidget(ic)
        texts = QVBoxLayout()
        texts.setSpacing(0)
        texts.addStretch(1)
        v = QLabel(value)
        v.setObjectName("statValue")
        l = QLabel(title)
        l.setObjectName("statLabel")
        texts.addWidget(v)
        texts.addWidget(l)
        texts.addStretch(1)
        lay.addLayout(texts)
        lay.addStretch()
        card.value_label = v  # referência directa (evita mexer no ícone por engano)
        return card

    def _appointment_page(self):
        scroll, col = self._scaffold()
        col.addWidget(self._page_header("calendar", "Agendar consulta", "Marque uma consulta para um paciente já cadastrado no sistema.", art="calendar"))

        card, lay = self._card()
        self._section_header(lay, "user", "Dados do paciente", first=True)

        lay.addWidget(self._label("ID do paciente"))
        lay.addSpacing(5)
        self.appointment_patient_id_input = self._field("Ex.: 1202")
        self.appointment_patient_id_input.setObjectName("appointmentPatientId")
        search = self.appointment_patient_id_input.addAction(qicon("search", "#466277", 18), QLineEdit.TrailingPosition)
        search.setToolTip("Pesquisar paciente")
        search.triggered.connect(self.find_appointment_patient)
        self.appointment_patient_id_input.returnPressed.connect(self.find_appointment_patient)
        id_row = QHBoxLayout()
        id_row.setContentsMargins(0, 0, 0, 0)
        id_row.setSpacing(0)
        id_row.addSpacing(LABEL_W_SHORT + COL_GAP)
        id_row.addWidget(self.appointment_patient_id_input, 1)
        lay.addLayout(id_row)
        lay.addSpacing(ROW_GAP)

        self.appointment_patient_name_input = self._field("Nome do paciente")
        self.appointment_patient_name_input.setObjectName("appointmentPatientName")
        self.appointment_patient_name_input.setReadOnly(True)
        lay.addLayout(self._form_row("Nome", self.appointment_patient_name_input, LABEL_W_SHORT))
        lay.addSpacing(ROW_GAP)

        self._section_header(lay, "stethoscope", "Especialidade e médico")

        self.appointment_specialty_input = self._combo("stethoscope")
        self.appointment_specialty_input.setPlaceholderText("Seleccione a especialidade")
        self.appointment_specialty_input.setCurrentIndex(-1)
        self.appointment_specialty_input.currentIndexChanged.connect(self.filter_doctors_by_specialty)
        lay.addWidget(self._stack("Especialidade", self.appointment_specialty_input))
        lay.addSpacing(ROW_GAP)

        self.appointment_doctor_input = self._combo()
        self.appointment_doctor_input.addItem("Seleccione primeiro a especialidade")
        self.appointment_doctor_input.setEnabled(False)
        lay.addLayout(self._form_row("Médico", self.appointment_doctor_input, LABEL_W_SHORT))

        self._section_header(lay, "calendar", "Detalhes da consulta")

        self.appointment_date_input = QDateEdit(QDateTime.currentDateTime().date())
        self.appointment_date_input.setCalendarPopup(True)
        self.appointment_date_input.setDisplayFormat("dd/MM/yyyy")
        self.appointment_date_input.setFixedHeight(FIELD_H)
        self.appointment_date_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._guard(self.appointment_date_input)

        self.appointment_time_input = self._combo("clock")
        for hour in range(24):
            for minute in (0, 30):
                self.appointment_time_input.addItem(f"{hour:02d}:{minute:02d}")

        details = QHBoxLayout()
        details.setContentsMargins(0, 0, 0, 0)
        details.setSpacing(COL_GAP + 4)
        details.addWidget(self._stack("Data", self.appointment_date_input), 1)
        details.addWidget(self._stack("Hora", self.appointment_time_input), 1)
        lay.addLayout(details)

        lay.addSpacing(16)
        lay.addLayout(self._actions("Agendar consulta", "calendar", self.schedule_appointment, self.clear_appointment_form))

        col.addWidget(card)
        col.addStretch(1)
        return scroll

    def _register_page(self):
        scroll, col = self._scaffold()
        col.addWidget(self._page_header("user-plus", "Registar paciente", "Adicione um novo paciente ao sistema.", art="user-plus"))

        card, lay = self._card()
        self._section_header(lay, "user", "Dados pessoais", first=True)

        self.full_name_input = self._field("Nome completo do paciente")
        lay.addLayout(self._form_row("Nome completo", self.full_name_input, LABEL_W_LONG))
        lay.addSpacing(ROW_GAP)

        self.birth_date_input = self._field("Ex.: 2000-05-20", icon="calendar")
        lay.addLayout(self._form_row("Data de nascimento", self.birth_date_input, LABEL_W_LONG))
        lay.addSpacing(ROW_GAP)

        self.gender_input = self._combo("gender")
        self.gender_input.addItems(["Seleccione o género", "Masculino", "Feminino", "Outro"])
        lay.addLayout(self._form_row("Género", self.gender_input, LABEL_W_LONG))
        lay.addSpacing(ROW_GAP)

        self.phone_input = self._field("Contacto telefónico", icon="phone")
        lay.addLayout(self._form_row("Telefone", self.phone_input, LABEL_W_LONG))

        self._section_header(lay, "map-pin", "Endereço")

        self.address_input = self._field("Ex.: Av. Eduardo Mondlane, Nº 123")
        lay.addLayout(self._form_row("Morada", self.address_input, LABEL_W_LONG))
        lay.addSpacing(ROW_GAP)

        self.neighborhood_input = self._field("Ex.: Sommerschield")
        self.city_input = self._field("Ex.: Maputo")
        city_label = self._label("Cidade")
        city_label.setFixedSize(58, FIELD_H)
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(COL_GAP)
        bairro_label = self._label("Bairro")
        bairro_label.setFixedSize(LABEL_W_LONG, FIELD_H)
        row.addWidget(bairro_label)
        row.addWidget(self.neighborhood_input, 1)
        row.addSpacing(4)
        row.addWidget(city_label)
        row.addWidget(self.city_input, 1)
        lay.addLayout(row)

        lay.addSpacing(18)
        lay.addLayout(self._actions("Registar paciente", "user-plus", self.register_patient, self.clear_form))

        col.addWidget(card)
        col.addStretch(1)
        return scroll

    def _patients_page(self):
        scroll, col = self._scaffold(TABLE_MAX_W)
        col.addWidget(self._page_header("users", "Pacientes", "Pesquise, consulte e actualize os dados dos pacientes.", art="users"))
        card, lay = self._card((22, 20, 22, 22))
        lay.setSpacing(14)

        search_row = QHBoxLayout()
        search_row.setSpacing(10)
        self.patient_search_input = self._field("ID, nome ou telefone")
        self.patient_search_input.textChanged.connect(self.filter_patients_table)
        search_row.addWidget(self.patient_search_input, 1)

        edit = QPushButton("Editar seleccionado")
        edit.setObjectName("blueButton")
        edit.setFixedHeight(44)
        edit.clicked.connect(self.edit_selected_patient)
        search_row.addWidget(edit)

        clear_search = QPushButton("Limpar")
        clear_search.setObjectName("secondaryButton")
        clear_search.setFixedHeight(44)
        clear_search.clicked.connect(self.patient_search_input.clear)
        search_row.addWidget(clear_search)

        refresh = QPushButton("Actualizar")
        refresh.setObjectName("secondaryButton")
        refresh.setFixedHeight(44)
        refresh.clicked.connect(self.load_patients)
        search_row.addWidget(refresh)
        lay.addLayout(search_row)

        self.patients_table = self._table([
            "ID", "Nome completo", "Nascimento", "Género", "Telefone",
            "Morada", "Bairro", "Cidade"
        ])
        self.patients_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.patients_table.doubleClicked.connect(self.edit_selected_patient)
        header = self.patients_table.horizontalHeader()
        for column in range(8):
            header.setSectionResizeMode(column, QHeaderView.Interactive)
        widths = [45, 150, 92, 82, 105, 230, 105, 95]
        for column, width in enumerate(widths):
            self.patients_table.setColumnWidth(column, width)
        lay.addWidget(self.patients_table)
        col.addWidget(card, 1)
        return scroll

    def _appointments_page(self):
        scroll, col = self._scaffold(TABLE_MAX_W)
        col.addWidget(self._page_header("calendar", "Consultas", "Consulte e actualize as consultas agendadas.", art="calendar"))
        card, lay = self._card((22, 20, 22, 22))
        lay.setSpacing(14)
        actions = QHBoxLayout()
        title = QLabel("Consultas agendadas")
        title.setObjectName("cardTitle")
        actions.addWidget(title)
        actions.addStretch()
        confirm_arrival = QPushButton("Confirmar presença")
        confirm_arrival.setObjectName("successButton")
        confirm_arrival.setFixedHeight(40)
        confirm_arrival.setMinimumWidth(130)
        confirm_arrival.clicked.connect(self.confirm_selected_arrival)
        actions.addWidget(confirm_arrival)

        add_queue = QPushButton("Adicionar à fila")
        add_queue.setObjectName("successButton")
        add_queue.setFixedHeight(40)
        add_queue.setMinimumWidth(120)
        add_queue.clicked.connect(self.add_selected_appointment_to_queue)
        actions.addWidget(add_queue)

        reschedule = QPushButton("Reagendar")
        reschedule.setObjectName("secondaryButton")
        reschedule.setFixedHeight(40)
        reschedule.setMinimumWidth(95)
        reschedule.clicked.connect(self.reschedule_selected_appointment)
        actions.addWidget(reschedule)

        cancel = QPushButton("Cancelar consulta")
        cancel.setObjectName("dangerButton")
        cancel.setFixedHeight(40)
        cancel.setMinimumWidth(125)
        cancel.clicked.connect(self.cancel_selected_appointment)
        actions.addWidget(cancel)

        refresh = QPushButton("Actualizar")
        refresh.setObjectName("secondaryButton")
        refresh.setFixedHeight(40)
        refresh.setMinimumWidth(90)
        refresh.clicked.connect(self.load_appointments)
        actions.addWidget(refresh)
        lay.addLayout(actions)

        filters = QHBoxLayout()
        self.appointment_search_input = self._field("Pesquisar ID, médico ou especialidade...")
        self.appointment_search_input.textChanged.connect(self.filter_appointments_table)
        filters.addWidget(self.appointment_search_input, 3)

        self.appointment_status_filter = self._combo()
        self.appointment_status_filter.addItems([
            "Todos os estados", "AGENDADA", "CONFIRMADA", "AGUARDANDO",
            "CHAMADA", "EM_ATENDIMENTO", "CONCLUIDA", "CANCELADA", "FALTOU"
        ])
        self.appointment_status_filter.currentIndexChanged.connect(self.filter_appointments_table)
        filters.addWidget(self.appointment_status_filter, 2)

        self.appointment_specialty_filter = self._combo()
        self.appointment_specialty_filter.addItem("Todas as especialidades")
        self.appointment_specialty_filter.currentIndexChanged.connect(self.filter_appointments_table)
        filters.addWidget(self.appointment_specialty_filter, 1)

        self.appointment_doctor_filter = self._combo()
        self.appointment_doctor_filter.addItem("Todos os médicos")
        self.appointment_doctor_filter.currentIndexChanged.connect(self.filter_appointments_table)
        filters.addWidget(self.appointment_doctor_filter, 1)
        lay.addLayout(filters)

        self.appointments_table = self._table([
            "ID", "Paciente", "Médico", "Data e hora", "Especialidade", "Estado"
        ])
        appointment_header = self.appointments_table.horizontalHeader()
        for column in range(6):
            appointment_header.setSectionResizeMode(column, QHeaderView.Interactive)
        for column, width in enumerate([48, 70, 150, 145, 145, 120]):
            self.appointments_table.setColumnWidth(column, width)
        lay.addWidget(self.appointments_table)
        col.addWidget(card, 1)
        return scroll

    def _doctors_page(self):
        scroll, col = self._scaffold(max_width=1200)
        col.addWidget(self._page_header("stethoscope", "Médicos e especialidades", "Gerir o corpo clínico e as especialidades disponíveis para agendamento."))

        doctors_card, doctors_lay = self._card((24, 28, 24, 28))
        self._section_header(doctors_lay, "stethoscope", "Médicos", first=True)
        doctor_actions = QHBoxLayout()
        doctor_actions.setSpacing(10)
        add_doctor = QPushButton("  Novo médico")
        add_doctor.setObjectName("successButton")
        add_doctor.setIcon(qicon("plus", "#ffffff", 18))
        add_doctor.clicked.connect(lambda: self._doctor_dialog())
        edit_doctor = QPushButton("  Editar selecionado")
        edit_doctor.setObjectName("secondaryButton")
        edit_doctor.clicked.connect(self._edit_selected_doctor)
        toggle_doctor = QPushButton("  Activar/desactivar")
        toggle_doctor.setObjectName("secondaryButton")
        toggle_doctor.clicked.connect(self._toggle_selected_doctor)
        refresh_doctors = QPushButton("  Actualizar")
        refresh_doctors.setObjectName("secondaryButton")
        refresh_doctors.clicked.connect(self.load_doctor_management)
        for b in (add_doctor, edit_doctor, toggle_doctor, refresh_doctors):
            b.setFixedHeight(40); b.setCursor(Qt.PointingHandCursor); doctor_actions.addWidget(b)
        doctor_actions.addStretch(1)
        doctors_lay.addLayout(doctor_actions)
        doctors_lay.addSpacing(10)
        self.doctors_management_table = self._table(["ID", "Médico", "Especialidade", "Estado"])
        doctors_lay.addWidget(self.doctors_management_table)
        col.addWidget(doctors_card)

        specialties_card, specialties_lay = self._card((24, 28, 24, 28))
        self._section_header(specialties_lay, "stethoscope", "Especialidades", first=True)
        specialty_actions = QHBoxLayout(); specialty_actions.setSpacing(10)
        add_specialty = QPushButton("  Nova especialidade")
        add_specialty.setObjectName("successButton"); add_specialty.setIcon(qicon("plus", "#ffffff", 18))
        add_specialty.clicked.connect(lambda: self._specialty_dialog())
        edit_specialty = QPushButton("  Editar selecionada")
        edit_specialty.setObjectName("secondaryButton"); edit_specialty.clicked.connect(self._edit_selected_specialty)
        toggle_specialty = QPushButton("  Activar/desactivar")
        toggle_specialty.setObjectName("secondaryButton"); toggle_specialty.clicked.connect(self._toggle_selected_specialty)
        refresh_specialties = QPushButton("  Actualizar")
        refresh_specialties.setObjectName("secondaryButton"); refresh_specialties.clicked.connect(self.load_doctor_management)
        for b in (add_specialty, edit_specialty, toggle_specialty, refresh_specialties):
            b.setFixedHeight(40); b.setCursor(Qt.PointingHandCursor); specialty_actions.addWidget(b)
        specialty_actions.addStretch(1); specialties_lay.addLayout(specialty_actions); specialties_lay.addSpacing(10)
        self.specialties_management_table = self._table(["ID", "Especialidade", "Estado"])
        specialties_lay.addWidget(self.specialties_management_table)
        col.addWidget(specialties_card)
        col.addStretch(1)
        QTimer.singleShot(0, self.load_doctor_management)
        return scroll

    def load_doctor_management(self):
        try:
            self._management_doctors = list(self.app.list_all_doctors())
            self._management_specialties = list(self.app.list_all_specialties())
            if hasattr(self, "doctors_management_table"):
                self.doctors_management_table.setRowCount(len(self._management_doctors))
                for row, doctor in enumerate(self._management_doctors):
                    vals=[doctor.id, doctor.fullName, doctor.specialty, "ACTIVO" if doctor.active else "INACTIVO"]
                    for col, value in enumerate(vals): self.doctors_management_table.setItem(row,col,QTableWidgetItem(str(value)))
                self.doctors_management_table.resizeColumnsToContents()
            if hasattr(self, "specialties_management_table"):
                self.specialties_management_table.setRowCount(len(self._management_specialties))
                for row, specialty in enumerate(self._management_specialties):
                    vals=[specialty.id, specialty.name, "ACTIVA" if specialty.active else "INACTIVA"]
                    for col, value in enumerate(vals): self.specialties_management_table.setItem(row,col,QTableWidgetItem(str(value)))
                self.specialties_management_table.resizeColumnsToContents()
            self.load_directory()
        except Exception as error:
            self.show_error(f"Não foi possível carregar médicos e especialidades:\n{error}")

    def _doctor_dialog(self, doctor=None):
        dialog=QDialog(self); dialog.setWindowTitle("Editar médico" if doctor else "Novo médico"); dialog.setModal(True)
        lay=QVBoxLayout(dialog); lay.setSpacing(10)
        name=self._field("Nome completo do médico");
        if doctor: name.setText(str(doctor.fullName))
        lay.addWidget(self._label("Nome completo")); lay.addWidget(name)
        specialty=self._combo("stethoscope"); lay.addWidget(self._label("Especialidade")); lay.addWidget(specialty)
        active_specialties=[x for x in getattr(self,"_management_specialties",[]) if getattr(x,"active",True)]
        for x in active_specialties: specialty.addItem(x.name,x.id)
        if doctor:
            idx=specialty.findText(str(doctor.specialty)); specialty.setCurrentIndex(idx if idx>=0 else 0)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject); lay.addWidget(buttons)
        if dialog.exec()!=QDialog.Accepted:return
        if not name.text().strip(): self.show_error("Indique o nome do médico."); return
        if specialty.currentData() is None: self.show_error("Seleccione uma especialidade activa."); return
        try:
            if doctor: self.app.update_doctor(int(doctor.id),name.text().strip(),int(specialty.currentData()))
            else: self.app.create_doctor(name.text().strip(),int(specialty.currentData()))
            self.load_doctor_management()
        except Exception as error: self.show_error(f"Não foi possível guardar o médico:\n{error}")

    def _selected_doctor(self):
        if not hasattr(self,"doctors_management_table"): return None
        rows=self.doctors_management_table.selectionModel().selectedRows()
        if not rows: self.show_error("Seleccione um médico primeiro."); return None
        idx=rows[0].row()
        return self._management_doctors[idx] if idx < len(getattr(self,"_management_doctors",[])) else None

    def _edit_selected_doctor(self):
        doctor=self._selected_doctor()
        if doctor: self._doctor_dialog(doctor)

    def _toggle_selected_doctor(self):
        doctor=self._selected_doctor()
        if not doctor:return
        try:self.app.set_doctor_active(int(doctor.id),not bool(doctor.active));self.load_doctor_management()
        except Exception as error:self.show_error(f"Não foi possível alterar o estado do médico:\n{error}")

    def _specialty_dialog(self, specialty=None):
        dialog=QDialog(self); dialog.setWindowTitle("Editar especialidade" if specialty else "Nova especialidade"); dialog.setModal(True)
        lay=QVBoxLayout(dialog); name=self._field("Nome da especialidade")
        if specialty:name.setText(str(specialty.name))
        lay.addWidget(self._label("Nome"));lay.addWidget(name)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel);buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject);lay.addWidget(buttons)
        if dialog.exec()!=QDialog.Accepted:return
        if not name.text().strip():self.show_error("Indique o nome da especialidade.");return
        try:
            if specialty:self.app.update_specialty(int(specialty.id),name.text().strip())
            else:self.app.create_specialty(name.text().strip())
            self.load_doctor_management()
        except Exception as error:self.show_error(f"Não foi possível guardar a especialidade:\n{error}")

    def _selected_specialty(self):
        if not hasattr(self,"specialties_management_table"):return None
        rows=self.specialties_management_table.selectionModel().selectedRows()
        if not rows:self.show_error("Seleccione uma especialidade primeiro.");return None
        idx=rows[0].row();return self._management_specialties[idx] if idx<len(getattr(self,"_management_specialties",[])) else None

    def _edit_selected_specialty(self):
        specialty=self._selected_specialty()
        if specialty:self._specialty_dialog(specialty)

    def _toggle_selected_specialty(self):
        specialty=self._selected_specialty()
        if not specialty:return
        try:self.app.set_specialty_active(int(specialty.id),not bool(specialty.active));self.load_doctor_management()
        except Exception as error:self.show_error(f"Não foi possível alterar o estado da especialidade:\n{error}")

    def _placeholder_page(self, icon_name, title, subtitle):
        scroll, col = self._scaffold()
        col.addWidget(self._page_header(icon_name, title, subtitle))
        card, lay = self._card((28, 40, 28, 40))
        msg = QLabel("Esta secção estará disponível em breve.")
        msg.setObjectName("cardDescription")
        msg.setAlignment(Qt.AlignCenter)
        lay.addWidget(msg)
        col.addWidget(card)
        col.addStretch(1)
        return scroll

    def show_page(self, index):
        self.content_stack.setCurrentIndex(index)
        for i, button in self.nav_buttons:
            button.set_active(i == index)

    # ------------------------------------------------------------------
    # Existing CORBA actions
    # ------------------------------------------------------------------
    def load_directory(self):
        try:
            self._directory_doctors = self.app.list_doctors()
            specialties = self.app.list_specialties()

            self.appointment_specialty_input.blockSignals(True)
            self.appointment_specialty_input.clear()
            for specialty in specialties:
                if getattr(specialty, "active", True):
                    self.appointment_specialty_input.addItem(specialty.name, specialty.id)
            self.appointment_specialty_input.setCurrentIndex(-1)
            self.appointment_specialty_input.blockSignals(False)

            self.filter_doctors_by_specialty(-1)
        except Exception as error:
            self.show_error(f"Não foi possível carregar médicos e especialidades:\n{error}")

    def filter_doctors_by_specialty(self, index):
        if not hasattr(self, "appointment_doctor_input"):
            return

        specialty_name = self.appointment_specialty_input.currentText().strip()
        self.appointment_doctor_input.blockSignals(True)
        self.appointment_doctor_input.clear()

        if self.appointment_specialty_input.currentData() is None or not specialty_name:
            self.appointment_doctor_input.addItem("Seleccione primeiro a especialidade")
            self.appointment_doctor_input.setEnabled(False)
        else:
            doctors = [
                doctor for doctor in getattr(self, "_directory_doctors", [])
                if getattr(doctor, "active", True) and getattr(doctor, "specialty", "") == specialty_name
            ]
            self.appointment_doctor_input.addItem("Seleccione o médico")
            for doctor in doctors:
                self.appointment_doctor_input.addItem(doctor.fullName, doctor.id)
            self.appointment_doctor_input.setEnabled(bool(doctors))
            if not doctors:
                self.appointment_doctor_input.setItemText(0, "Não existem médicos para esta especialidade")

        self.appointment_doctor_input.setCurrentIndex(0)
        self.appointment_doctor_input.blockSignals(False)

    def find_appointment_patient(self):
        patient_id_text = self.appointment_patient_id_input.text().strip()

        if not patient_id_text or not patient_id_text.isdigit():
            self.show_error("Introduza um ID de paciente válido.")
            return

        try:
            patient = self.app.find_patient_by_id(int(patient_id_text))
            self.appointment_patient_name_input.setText(patient.fullName)
        except Exception as error:
            self.appointment_patient_name_input.clear()
            self.show_error(f"Não foi possível encontrar o paciente:\n{error}")

    def register_patient(self):
        full_name = self.full_name_input.text().strip()
        birth_date = self.birth_date_input.text().strip()
        gender_index = self.gender_input.currentIndex()
        phone = self.phone_input.text().strip()

        address = self.address_input.text().strip()
        neighborhood = self.neighborhood_input.text().strip()
        city = self.city_input.text().strip()

        if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'’.-]+(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ'’.-]+)+", full_name):
            self.show_error("Introduza o nome completo correctamente, por exemplo: António Manuel.")
            return
        try:
            parsed_birth = QDateTime.fromString(birth_date, "yyyy-MM-dd")
            if not parsed_birth.isValid():
                raise ValueError
            if parsed_birth.date() >= QDateTime.currentDateTime().date():
                self.show_error("A data de nascimento deve ser uma data válida no passado.")
                return
        except ValueError:
            self.show_error("A data de nascimento deve estar no formato AAAA-MM-DD.")
            return
        if gender_index == 0:
            self.show_error("Seleccione o género do paciente.")
            return
        digits = "".join(ch for ch in phone if ch.isdigit())
        if not re.fullmatch(r"[+\d\s()\-]+", phone) or len(digits) < 7 or len(digits) > 15:
            self.show_error("Introduza um contacto telefónico válido.")
            return
        if len(address) < 5:
            self.show_error("Introduza uma morada válida.")
            return
        if len(neighborhood) < 2:
            self.show_error("Introduza o bairro.")
            return
        if len(city) < 2 or any(ch.isdigit() for ch in city):
            self.show_error("Introduza uma cidade válida.")
            return

        try:
            patient = self.app.register_patient(
                full_name, birth_date,
                self.gender_input.currentText(), phone,
                address, neighborhood, city
            )
            ResultDialog.success(
                self,
                "Paciente registado",
                "O paciente foi adicionado ao sistema com sucesso.",
                details=[
                    ("ID do paciente", f"#{patient.id}"),
                    ("Nome", patient.fullName),
                    ("Telefone", patient.phone),
                    ("Cidade", getattr(patient, "city", "—")),
                ],
                primary_text="Fechar",
            )
            self.clear_form()
            self.load_patients()
            self.show_page(3)
        except Exception as error:
            self.show_error(f"Não foi possível registar o paciente:\n{error}")

    def schedule_appointment(self):
        patient_id_text = self.appointment_patient_id_input.text().strip()
        doctor = self.appointment_doctor_input.currentText().strip()
        specialty = self.appointment_specialty_input.currentText().strip()
        appointment_time = self.appointment_time_input.currentText().strip()
        appointment_date = (self.appointment_date_input.date().toString("yyyy-MM-dd") + " " +
                            appointment_time)

        if not patient_id_text:
            self.show_error("Introduza o ID do paciente.")
            return
        if not patient_id_text.isdigit():
            self.show_error("O ID do paciente deve ser numérico.")
            return
        if not specialty:
            self.show_error("Seleccione primeiro a especialidade.")
            return
        if not doctor or doctor in {"Seleccione o médico", "Seleccione primeiro a especialidade", "Não existem médicos para esta especialidade"}:
            self.show_error("Seleccione um médico disponível para a especialidade escolhida.")
            return
        if appointment_time not in {f"{hour:02d}:{minute:02d}" for hour in range(24) for minute in (0, 30)}:
            self.show_error("Seleccione uma hora em intervalos de 30 minutos.")
            return

        try:
            appointment = self.app.schedule_appointment(
                int(patient_id_text), doctor, appointment_date, specialty
            )
            ResultDialog.success(
                self,
                "Consulta agendada",
                "A consulta foi criada com sucesso.",
                details=[
                    ("Consulta", f"#{appointment.id}"),
                    ("Paciente", patient_id_text),
                    ("Médico", doctor),
                    ("Especialidade", specialty),
                    ("Data e hora", appointment_date),
                    ("Estado", "AGENDADA"),
                ],
                primary_text="Fechar",
            )
            self.clear_appointment_form()
            self.load_appointments()
        except Exception as error:
            self.show_error(f"Não foi possível agendar a consulta:\n{error}")

    def confirm_selected_arrival(self):
        if not hasattr(self, "appointments_table"):
            return

        selected = self.appointments_table.selectionModel().selectedRows()
        if not selected:
            self.show_error("Seleccione uma consulta antes de confirmar a chegada.")
            return

        row = selected[0].row()
        id_item = self.appointments_table.item(row, 0)
        status_item = self.appointments_table.item(row, 5)
        if id_item is None or status_item is None:
            self.show_error("Não foi possível identificar a consulta seleccionada.")
            return

        appointment_id = int(id_item.text())
        status = status_item.text().strip().upper()
        if status != "AGENDADA":
            self.show_error(
                f"A consulta #{appointment_id} não pode confirmar presença no estado {status}."
            )
            return

        try:
            self.app.update_appointment_status(appointment_id, "CONFIRMADA")
            ResultDialog.success(
                self,
                "Presença confirmada",
                "A chegada do paciente foi registada.",
                details=[
                    ("Consulta", f"#{appointment_id}"),
                    ("Estado", "CONFIRMADA"),
                    ("Próximo passo", "Adicionar à fila"),
                ],
            )
            self.load_appointments()
        except Exception as error:
            self.show_error(
                f"Não foi possível confirmar a chegada da consulta #{appointment_id}:\n{error}"
            )

    def load_appointments(self):
        try:
            self._appointments_cache = list(self.app.list_appointments())
            self._refresh_appointment_filters()
            self.filter_appointments_table()
            if hasattr(self, "home_appointment_stat"):
                self.home_appointment_stat.value_label.setText(str(len(self._appointments_cache)))
        except Exception as error:
            self.show_error(f"Não foi possível carregar as consultas:\n{error}")

    def _refresh_appointment_filters(self):
        if not hasattr(self, "appointment_doctor_filter"):
            return

        doctors = sorted({str(a.doctor) for a in self._appointments_cache if getattr(a, "doctor", "")}, key=str.casefold)
        specialties = sorted({str(a.specialty) for a in self._appointments_cache if getattr(a, "specialty", "")}, key=str.casefold)

        for combo, values, default in (
            (self.appointment_doctor_filter, doctors, "Todos os médicos"),
            (self.appointment_specialty_filter, specialties, "Todas as especialidades"),
        ):
            current = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            combo.addItem(default)
            for value in values:
                combo.addItem(value)
            idx = combo.findText(current)
            combo.setCurrentIndex(idx if idx >= 0 else 0)
            combo.blockSignals(False)

    def filter_appointments_table(self, _index=None):
        if not hasattr(self, "appointments_table"):
            return

        query = self.appointment_search_input.text().strip().casefold() if hasattr(self, "appointment_search_input") else ""
        status = self.appointment_status_filter.currentText() if hasattr(self, "appointment_status_filter") else "Todos os estados"
        specialty = self.appointment_specialty_filter.currentText() if hasattr(self, "appointment_specialty_filter") else "Todas as especialidades"
        doctor = self.appointment_doctor_filter.currentText() if hasattr(self, "appointment_doctor_filter") else "Todos os médicos"

        appointments = []
        for appointment in getattr(self, "_appointments_cache", []):
            appointment_status = str(getattr(appointment, "status", "AGENDADA"))
            if status != "Todos os estados" and appointment_status != status:
                continue
            if specialty != "Todas as especialidades" and str(getattr(appointment, "specialty", "")) != specialty:
                continue
            if doctor != "Todos os médicos" and str(getattr(appointment, "doctor", "")) != doctor:
                continue
            if query:
                haystack = " ".join([
                    str(getattr(appointment, "id", "")),
                    str(getattr(appointment, "patientId", "")),
                    str(getattr(appointment, "doctor", "")),
                    str(getattr(appointment, "specialty", "")),
                    str(getattr(appointment, "appointmentDate", "")),
                    appointment_status,
                ]).casefold()
                if query not in haystack:
                    continue
            appointments.append(appointment)

        self.appointments_table.setRowCount(len(appointments))
        for row, appointment in enumerate(appointments):
            values = [
                appointment.id, appointment.patientId, appointment.doctor,
                appointment.appointmentDate, appointment.specialty,
                getattr(appointment, "status", "AGENDADA")
            ]
            for column, value in enumerate(values):
                self.appointments_table.setItem(row, column, QTableWidgetItem(str(value)))

    def _selected_appointment_data(self):
        if not hasattr(self, "appointments_table"):
            return None
        selected = self.appointments_table.selectionModel().selectedRows()
        if not selected:
            self.show_error("Seleccione uma consulta primeiro.")
            return None
        row = selected[0].row()
        id_item = self.appointments_table.item(row, 0)
        status_item = self.appointments_table.item(row, 5)
        if id_item is None or status_item is None:
            self.show_error("Não foi possível identificar a consulta seleccionada.")
            return None
        return int(id_item.text()), status_item.text().strip().upper()

    def reschedule_selected_appointment(self):
        selected = self._selected_appointment_data()
        if not selected:
            return
        appointment_id, status = selected
        if status != "AGENDADA":
            self.show_error("Só é possível reagendar consultas que ainda estejam AGENDADA.")
            return

        appointment = next((a for a in getattr(self, "_appointments_cache", []) if int(a.id) == appointment_id), None)
        if appointment is None:
            self.show_error("Consulta não encontrada.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Reagendar consulta #{appointment_id}")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)

        info = QLabel(f"Médico: {appointment.doctor}\nEspecialidade: {appointment.specialty}")
        info.setObjectName("cardDescription")
        layout.addWidget(info)

        date_input = QDateEdit(QDateTime.fromString(str(appointment.appointmentDate), "yyyy-MM-dd HH:mm").date())
        date_input.setCalendarPopup(True)
        date_input.setDisplayFormat("dd/MM/yyyy")
        layout.addWidget(QLabel("Nova data"))
        layout.addWidget(date_input)

        time_input = self._combo("clock")
        for hour in range(24):
            for minute in (0, 30):
                time_input.addItem(f"{hour:02d}:{minute:02d}")
        old_time = str(appointment.appointmentDate)[11:16]
        idx = time_input.findText(old_time)
        time_input.setCurrentIndex(idx if idx >= 0 else 0)
        layout.addWidget(QLabel("Nova hora"))
        layout.addWidget(time_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.Accepted:
            return

        new_date = date_input.date().toString("yyyy-MM-dd") + " " + time_input.currentText()
        try:
            self.app.reschedule_appointment(appointment_id, new_date)
            ResultDialog.success(
                self,
                "Consulta reagendada",
                "A data e hora da consulta foram actualizadas.",
                details=[("Consulta", f"#{appointment_id}"), ("Nova data e hora", new_date)],
            )
            self.load_appointments()
        except Exception as error:
            self.show_error(f"Não foi possível reagendar a consulta #{appointment_id}:\n{error}")

    def cancel_selected_appointment(self):
        selected = self._selected_appointment_data()
        if not selected:
            return
        appointment_id, status = selected
        if status not in {"AGENDADA", "CONFIRMADA", "AGUARDANDO"}:
            self.show_error(f"A consulta #{appointment_id} não pode ser cancelada no estado {status}.")
            return

        answer = QMessageBox.question(
            self, "Cancelar consulta",
            f"Tem a certeza de que pretende cancelar a consulta #{appointment_id}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if answer != QMessageBox.Yes:
            return

        try:
            self.app.update_appointment_status(appointment_id, "CANCELADA")
            ResultDialog.success(
                self,
                "Consulta cancelada",
                "A consulta foi cancelada com sucesso.",
                details=[("Consulta", f"#{appointment_id}"), ("Estado", "CANCELADA")],
            )
            self.load_appointments()
        except Exception as error:
            self.show_error(f"Não foi possível cancelar a consulta #{appointment_id}:\n{error}")

    def add_selected_appointment_to_queue(self):
        if not hasattr(self, "appointments_table"):
            return

        selected = self.appointments_table.selectionModel().selectedRows()
        if not selected:
            self.show_error("Seleccione uma consulta antes de a adicionar à fila.")
            return

        row = selected[0].row()
        id_item = self.appointments_table.item(row, 0)
        status_item = self.appointments_table.item(row, 5)
        if id_item is None or status_item is None:
            self.show_error("Não foi possível identificar a consulta seleccionada.")
            return

        appointment_id = int(id_item.text())
        status = status_item.text().strip().upper()
        if status != "CONFIRMADA":
            self.show_error(
                f"A consulta #{appointment_id} só pode entrar na fila depois de a presença ser confirmada. Estado actual: {status}."
            )
            return

        try:
            self.app.add_appointment_to_queue(appointment_id)
            ResultDialog.success(
                self,
                "Paciente adicionado à fila",
                "A consulta entrou na fila de atendimento.",
                details=[("Consulta", f"#{appointment_id}"), ("Estado", "AGUARDANDO")],
            )
            self.load_appointments()
        except Exception as error:
            self.show_error(f"Não foi possível adicionar a consulta à fila:\n{error}")

    def load_patients(self):
        try:
            patients = self.app.list_patients()
            self._patients_cache = list(patients)
            if hasattr(self, "home_patient_stat"):
                self.home_patient_stat.value_label.setText(str(len(patients)))
            self.filter_patients_table()
        except Exception as error:
            self.show_error(f"Não foi possível carregar os pacientes:\n{error}")

    def filter_patients_table(self, _text=None):
        if not hasattr(self, "patients_table"):
            return

        query = (self.patient_search_input.text() if hasattr(self, "patient_search_input") else "").strip().casefold()
        patients = getattr(self, "_patients_cache", [])

        if query:
            patients = [
                patient for patient in patients
                if query in str(patient.id).casefold()
                or query in str(patient.fullName).casefold()
                or query in str(patient.phone).casefold()
                or query in str(getattr(patient, "address", "")).casefold()
                or query in str(getattr(patient, "neighborhood", "")).casefold()
                or query in str(getattr(patient, "city", "")).casefold()
            ]

        self.patients_table.setRowCount(len(patients))
        for row, patient in enumerate(patients):
            values = [
                patient.id,
                patient.fullName,
                patient.birthDate,
                patient.gender,
                patient.phone,
                getattr(patient, "address", ""),
                getattr(patient, "neighborhood", ""),
                getattr(patient, "city", ""),
            ]
            for column, value in enumerate(values):
                self.patients_table.setItem(row, column, QTableWidgetItem(str(value)))

    def edit_selected_patient(self, *_args):
        if not hasattr(self, "patients_table"):
            return

        selected = self.patients_table.selectionModel().selectedRows()
        if not selected:
            self.show_error("Seleccione um paciente antes de editar.")
            return

        row = selected[0].row()
        id_item = self.patients_table.item(row, 0)
        if id_item is None:
            self.show_error("Não foi possível identificar o paciente seleccionado.")
            return

        try:
            patient = self.app.find_patient_by_id(int(id_item.text()))
            if not getattr(patient, "id", 0):
                self.show_error("Paciente não encontrado.")
                return
        except Exception as error:
            self.show_error(f"Não foi possível carregar o paciente:\n{error}")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Editar paciente #{patient.id}")
        dialog.setMinimumWidth(500)
        form = QVBoxLayout(dialog)
        form.setContentsMargins(24, 24, 24, 24)
        form.setSpacing(12)

        name_input = self._field("Nome completo")
        name_input.setText(patient.fullName)
        form.addLayout(self._form_row("Nome completo", name_input, LABEL_W_LONG))

        birth_input = self._field("AAAA-MM-DD")
        birth_input.setText(patient.birthDate)
        form.addLayout(self._form_row("Nascimento", birth_input, LABEL_W_LONG))

        gender_input = self._combo()
        gender_input.addItems(["Seleccione o género", "Masculino", "Feminino", "Outro"])
        index = gender_input.findText(patient.gender, Qt.MatchFixedString)
        gender_input.setCurrentIndex(index if index >= 0 else 0)
        form.addLayout(self._form_row("Género", gender_input, LABEL_W_LONG))

        phone_input = self._field("Contacto telefónico")
        phone_input.setText(patient.phone)
        form.addLayout(self._form_row("Telefone", phone_input, LABEL_W_LONG))

        address_input = self._field("Morada")
        address_input.setText(getattr(patient, "address", ""))
        form.addLayout(self._form_row("Morada", address_input, LABEL_W_LONG))

        neighborhood_input = self._field("Bairro")
        neighborhood_input.setText(getattr(patient, "neighborhood", ""))
        form.addLayout(self._form_row("Bairro", neighborhood_input, LABEL_W_LONG))

        city_input = self._field("Cidade")
        city_input.setText(getattr(patient, "city", ""))
        form.addLayout(self._form_row("Cidade", city_input, LABEL_W_LONG))

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addWidget(buttons)

        if dialog.exec() != QDialog.Accepted:
            return

        full_name = name_input.text().strip()
        birth_date = birth_input.text().strip()
        gender = gender_input.currentText().strip()
        phone = phone_input.text().strip()
        address = address_input.text().strip()
        neighborhood = neighborhood_input.text().strip()
        city = city_input.text().strip()

        if (
            len(full_name.split()) < 2
            or not birth_date
            or gender == "Seleccione o género"
            or len("".join(ch for ch in phone if ch.isdigit())) < 7
            or len(address) < 5
            or len(neighborhood) < 2
            or len(city) < 2
        ):
            self.show_error("Preencha correctamente todos os campos do paciente.")
            return

        try:
            self.app.update_patient(
                patient.id, full_name, birth_date, gender, phone,
                address, neighborhood, city
            )
            ResultDialog.success(
                self,
                "Paciente actualizado",
                "Os dados do paciente foram actualizados com sucesso.",
                details=[("Paciente", f"#{patient.id}"), ("Nome", patient.fullName), ("Cidade", getattr(patient, "city", "—"))],
            )
            self.load_patients()
        except Exception as error:
            self.show_error(f"Não foi possível actualizar o paciente:\n{error}")

    def clear_appointment_form(self):
        self.appointment_patient_id_input.clear()
        self.appointment_doctor_input.setCurrentIndex(0)
        self.appointment_specialty_input.setCurrentIndex(-1)
        self.appointment_specialty_input.clearEditText()
        self.appointment_patient_name_input.clear()
        self.appointment_date_input.setDate(QDateTime.currentDateTime().date())
        self.appointment_time_input.setCurrentIndex(0)

    def clear_form(self):
        self.full_name_input.clear()
        self.birth_date_input.clear()
        self.gender_input.setCurrentIndex(0)
        self.phone_input.clear()
        self.address_input.clear()
        self.neighborhood_input.clear()
        self.city_input.clear()

    def show_error(self, message):
        QMessageBox.critical(self, "Erro", message)
