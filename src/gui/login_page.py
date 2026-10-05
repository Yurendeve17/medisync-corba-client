from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .icons import pixmap, qicon

# Foto opcional do hospital para o painel esquerdo.
# Se existir, é usada no lugar da ilustração desenhada em código.
BACKGROUND_PHOTO = Path(__file__).resolve().parent / "assets" / "login_bg.jpg"

CARD_RADIUS = 28
ACCENT = "#2ad4a6"

TEXTS = {
    "pt": {
        "brand_sub": "Sistema Hospitalar",
        "headline_1": "Cuidando de pessoas,",
        "headline_2": "todos os dias.",
        "lead": "Gestão integrada de pacientes, consultas e atendimento hospitalar.",
        "f1_title": "Atendimento eficiente",
        "f1_text": "Pacientes no centro do cuidado",
        "f2_title": "Agenda organizada",
        "f2_text": "Consultas e médicos integrados",
        "f3_title": "Dados seguros",
        "f3_text": "Privacidade e confiabilidade",
        "welcome": "Bem-vindo ao MediSync",
        "welcome_sub": "Faça login para aceder ao sistema",
        "user_label": "Utilizador",
        "user_ph": "Digite o seu utilizador",
        "pass_label": "Senha",
        "pass_ph": "Digite a sua senha",
        "forgot": "Esqueceu a sua senha?",
        "enter": "Entrar",
        "or": "ou",
        "create": "Criar uma nova conta",
        "err_empty": "Preencha o utilizador e a senha.",
        "err_invalid": "Utilizador ou senha inválidos.",
        "forgot_msg": "Para redefinir a senha, contacte o administrador do sistema.",
        "create_msg": "A criação de novas contas ainda não está disponível neste cliente.",
    },
    "en": {
        "brand_sub": "Hospital System",
        "headline_1": "Caring for people,",
        "headline_2": "every single day.",
        "lead": "Integrated management of patients, appointments and hospital care.",
        "f1_title": "Efficient care",
        "f1_text": "Patients at the centre of care",
        "f2_title": "Organised schedule",
        "f2_text": "Appointments and doctors in sync",
        "f3_title": "Secure data",
        "f3_text": "Privacy and reliability",
        "welcome": "Welcome to MediSync",
        "welcome_sub": "Sign in to access the system",
        "user_label": "Username",
        "user_ph": "Enter your username",
        "pass_label": "Password",
        "pass_ph": "Enter your password",
        "forgot": "Forgot your password?",
        "enter": "Sign in",
        "or": "or",
        "create": "Create a new account",
        "err_empty": "Please enter your username and password.",
        "err_invalid": "Invalid username or password.",
        "forgot_msg": "To reset your password, please contact the system administrator.",
        "create_msg": "Creating new accounts is not available in this client yet.",
    },
}


class LoginCard(QWidget):
    """Cartão branco com cantos arredondados que contém os dois painéis."""

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#ffffff"))
        painter.drawRoundedRect(self.rect(), CARD_RADIUS, CARD_RADIUS)


class BrandPanel(QWidget):
    """Painel esquerdo: fundo verde com edifício, arredondado só à esquerda."""

    def __init__(self):
        super().__init__()
        self._photo = QPixmap(str(BACKGROUND_PHOTO)) if BACKGROUND_PHOTO.exists() else None

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()

        # cantos arredondados apenas à esquerda (o lado direito sai do widget)
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(0, 0, w + CARD_RADIUS, h), CARD_RADIUS, CARD_RADIUS)
        painter.setClipPath(clip)

        if self._photo is not None and not self._photo.isNull():
            scaled = self._photo.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )
            painter.drawPixmap((w - scaled.width()) // 2, (h - scaled.height()) // 2, scaled)
        else:
            self._paint_scene(painter, w, h)

        # véu verde para dar contraste ao texto (mais forte à esquerda)
        veil = QLinearGradient(0, 0, w, 0)
        veil.setColorAt(0.0, QColor(6, 62, 48, 238))
        veil.setColorAt(0.55, QColor(8, 74, 58, 196))
        veil.setColorAt(1.0, QColor(8, 74, 58, 96))
        painter.fillRect(self.rect(), veil)

        fade = QLinearGradient(0, h * 0.55, 0, h)
        fade.setColorAt(0.0, QColor(4, 40, 31, 0))
        fade.setColorAt(1.0, QColor(4, 40, 31, 150))
        painter.fillRect(self.rect(), fade)

    @staticmethod
    def _paint_scene(p, w, h):
        # céu
        sky = QLinearGradient(0, 0, 0, h)
        sky.setColorAt(0.0, QColor("#12695a"))
        sky.setColorAt(0.6, QColor("#0d5646"))
        sky.setColorAt(1.0, QColor("#093d31"))
        p.fillRect(QRectF(0, 0, w, h), sky)

        # brilho suave e círculos decorativos
        glow = QRadialGradient(QPointF(w * 0.86, h * 0.28), w * 0.6)
        glow.setColorAt(0.0, QColor(150, 210, 190, 90))
        glow.setColorAt(1.0, QColor(150, 210, 190, 0))
        p.fillRect(QRectF(0, 0, w, h), glow)

        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 14))
        p.drawEllipse(QPointF(w * 0.98, h * 0.32), w * 0.42, w * 0.42)

        # edifício
        base = h * 0.92
        top = h * 0.60
        bx, bw = w * 0.36, w * 0.70

        p.setBrush(QColor(178, 200, 194, 150))
        p.drawRect(QRectF(w * 0.52, h * 0.50, w * 0.5, top - h * 0.50 + 2))
        p.setBrush(QColor(206, 222, 217, 170))
        p.drawRect(QRectF(bx, top, bw, base - top))

        cols, rows = 8, 3
        pad = 20
        cell_w = (bw - pad * 2) / cols
        cell_h = (base - top - 46) / rows
        for r in range(rows):
            for c in range(cols):
                lit = (r * 3 + c * 5) % 4 != 0
                p.setBrush(QColor(255, 216, 146, 200) if lit else QColor(42, 96, 86, 170))
                p.drawRoundedRect(
                    QRectF(bx + pad + c * cell_w, top + 20 + r * cell_h, cell_w - 10, cell_h - 12),
                    2,
                    2,
                )

        # chão e arbustos
        p.setBrush(QColor(5, 42, 33, 235))
        p.drawRect(QRectF(0, base, w, h - base))
        p.setBrush(QColor(10, 70, 52, 230))
        for i in range(7):
            p.drawEllipse(QPointF(w * (0.06 + i * 0.15), base + 2), w * 0.10, h * 0.035)


class LoginPage(QWidget):

    login_successful = Signal(object)
    forgot_password_requested = Signal()
    register_requested = Signal()

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.lang = "pt"

        self.setObjectName("loginPage")

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(40, 30, 40, 30)

        self.card = LoginCard()
        self.card.setMinimumSize(980, 640)
        self.card.setMaximumSize(1320, 800)

        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(70)
        shadow.setOffset(0, 18)
        shadow.setColor(QColor(16, 52, 62, 60))
        self.card.setGraphicsEffect(shadow)

        card_layout = QHBoxLayout(self.card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        card_layout.addWidget(self._build_brand_panel(), 53)
        card_layout.addWidget(self._build_form_panel(), 47)

        page_layout.addWidget(self.card)

        self.password_input.returnPressed.connect(self.login)
        self.username_input.returnPressed.connect(self.password_input.setFocus)

        self.retranslate()
        self.username_input.setFocus()

    # ------------------------------------------------------------------
    # Fundo da página
    # ------------------------------------------------------------------
    def paintEvent(self, _event):
        painter = QPainter(self)
        bg = QLinearGradient(0, 0, self.width(), self.height())
        bg.setColorAt(0.0, QColor("#dbe8f0"))
        bg.setColorAt(0.5, QColor("#eef4f8"))
        bg.setColorAt(1.0, QColor("#dfeaf1"))
        painter.fillRect(self.rect(), bg)

    # ------------------------------------------------------------------
    # Painel esquerdo
    # ------------------------------------------------------------------
    def _build_brand_panel(self):
        panel = BrandPanel()

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(64, 64, 40, 56)
        layout.setSpacing(0)

        # logótipo
        brand_row = QHBoxLayout()
        brand_row.setSpacing(14)

        logo_icon = QLabel()
        logo_icon.setPixmap(pixmap("logo", "#1fd3a5", 60))
        logo_icon.setFixedSize(60, 60)
        logo_icon.setStyleSheet("background: transparent;")

        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)

        brand = QLabel(f'<span style="color:#ffffff;">Medi</span><span style="color:{ACCENT};">Sync</span>')
        brand.setObjectName("loginBrand")
        brand.setTextFormat(Qt.RichText)

        self.brand_sub = QLabel()
        self.brand_sub.setObjectName("loginBrandSub")

        brand_text.addWidget(brand)
        brand_text.addWidget(self.brand_sub)

        brand_row.addWidget(logo_icon)
        brand_row.addLayout(brand_text)
        brand_row.addStretch()

        layout.addLayout(brand_row)
        layout.addSpacing(40)

        self.headline = QLabel()
        self.headline.setObjectName("loginHeadline")
        self.headline.setTextFormat(Qt.RichText)
        self.headline.setWordWrap(True)
        layout.addWidget(self.headline)
        layout.addSpacing(18)

        self.lead = QLabel()
        self.lead.setObjectName("loginLead")
        self.lead.setWordWrap(True)
        self.lead.setMaximumWidth(460)
        layout.addWidget(self.lead)
        layout.addSpacing(34)

        self.feature_titles = []
        self.feature_texts = []
        for icon in ("users", "calendar", "shield"):
            layout.addLayout(self._feature_row(icon))
            layout.addSpacing(16)

        layout.addStretch()
        return panel

    def _feature_row(self, icon_name):
        row = QHBoxLayout()
        row.setSpacing(18)

        icon = QLabel()
        icon.setObjectName("loginFeatureIcon")
        icon.setFixedSize(56, 56)
        icon.setAlignment(Qt.AlignCenter)
        icon.setPixmap(pixmap(icon_name, "#e4f6f0", 26))

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        title = QLabel()
        title.setObjectName("loginFeatureTitle")
        text = QLabel()
        text.setObjectName("loginFeatureText")

        text_col.addStretch()
        text_col.addWidget(title)
        text_col.addWidget(text)
        text_col.addStretch()

        row.addWidget(icon)
        row.addLayout(text_col)
        row.addStretch()

        self.feature_titles.append(title)
        self.feature_texts.append(text)
        return row

    # ------------------------------------------------------------------
    # Painel direito (formulário)
    # ------------------------------------------------------------------
    def _build_form_panel(self):
        panel = QWidget()

        outer = QVBoxLayout(panel)
        outer.setContentsMargins(40, 28, 32, 36)
        outer.setSpacing(0)

        outer.addStretch(1)

        holder = QHBoxLayout()
        holder.addStretch(1)
        holder.addWidget(self._build_form(), 10)
        holder.addStretch(1)
        outer.addLayout(holder)

        outer.addStretch(1)
        return panel

    def _build_form(self):
        form = QWidget()
        form.setMaximumWidth(520)

        layout = QVBoxLayout(form)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.welcome = QLabel()
        self.welcome.setObjectName("loginWelcome")
        self.welcome_sub = QLabel()
        self.welcome_sub.setObjectName("loginWelcomeSub")

        layout.addWidget(self.welcome)
        layout.addSpacing(6)
        layout.addWidget(self.welcome_sub)
        layout.addSpacing(32)

        # utilizador
        self.user_label = QLabel()
        self.user_label.setObjectName("loginFieldLabel")
        self.username_input = QLineEdit()
        self.username_input.setObjectName("loginInput")
        self.username_input.addAction(qicon("user", "#5b7387", 20), QLineEdit.LeadingPosition)

        layout.addWidget(self.user_label)
        layout.addSpacing(8)
        layout.addWidget(self.username_input)
        layout.addSpacing(20)

        # senha
        self.pass_label = QLabel()
        self.pass_label.setObjectName("loginFieldLabel")
        self.password_input = QLineEdit()
        self.password_input.setObjectName("loginInput")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.addAction(qicon("lock", "#5b7387", 20), QLineEdit.LeadingPosition)
        self._eye_action = self.password_input.addAction(
            qicon("eye-off", "#5b7387", 20), QLineEdit.TrailingPosition
        )
        self._eye_action.triggered.connect(self.toggle_password)

        layout.addWidget(self.pass_label)
        layout.addSpacing(8)
        layout.addWidget(self.password_input)

        # erro + "esqueceu a senha"
        self.error_label = QLabel()
        self.error_label.setObjectName("loginError")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addSpacing(8)
        layout.addWidget(self.error_label)

        self.forgot_button = QPushButton()
        self.forgot_button.setObjectName("loginLink")
        self.forgot_button.setCursor(Qt.PointingHandCursor)
        self.forgot_button.setFlat(True)
        self.forgot_button.clicked.connect(self.on_forgot_password)

        forgot_row = QHBoxLayout()
        forgot_row.addStretch()
        forgot_row.addWidget(self.forgot_button)
        layout.addLayout(forgot_row)
        layout.addSpacing(14)

        # entrar
        self.login_button = QPushButton()
        self.login_button.setObjectName("loginPrimary")
        self.login_button.setIcon(qicon("arrow-right", "#ffffff", 20))
        self.login_button.setIconSize(QSize(20, 20))
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)
        layout.addSpacing(22)

        return form

    # ------------------------------------------------------------------
    # Idioma
    # ------------------------------------------------------------------
    def _t(self, key):
        return TEXTS[self.lang][key]

    def set_language(self, code):
        self.lang = code
        self.error_label.hide()
        self.retranslate()

    def retranslate(self):
        t = self._t

        self.brand_sub.setText(t("brand_sub"))
        self.headline.setText(
            f'{t("headline_1")}<br><span style="color:{ACCENT};">{t("headline_2")}</span>'
        )
        self.lead.setText(t("lead"))

        for i, key in enumerate(("f1", "f2", "f3")):
            self.feature_titles[i].setText(t(f"{key}_title"))
            self.feature_texts[i].setText(t(f"{key}_text"))

        self.welcome.setText(t("welcome"))
        self.welcome_sub.setText(t("welcome_sub"))
        self.user_label.setText(t("user_label"))
        self.username_input.setPlaceholderText(t("user_ph"))
        self.pass_label.setText(t("pass_label"))
        self.password_input.setPlaceholderText(t("pass_ph"))
        self.forgot_button.setText(t("forgot"))
        self.login_button.setText(f"  {t('enter')}")

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------
    def toggle_password(self):
        hidden = self.password_input.echoMode() == QLineEdit.Password
        self.password_input.setEchoMode(QLineEdit.Normal if hidden else QLineEdit.Password)
        self._eye_action.setIcon(qicon("eye" if hidden else "eye-off", "#5b7387", 20))

    def reset_form(self):
        """Limpa o formulário (usado ao terminar sessão)."""
        self.username_input.clear()
        self.password_input.clear()
        self.password_input.setEchoMode(QLineEdit.Password)
        self._eye_action.setIcon(qicon("eye-off", "#5b7387", 20))
        self.error_label.hide()

    def on_forgot_password(self):
        self.forgot_password_requested.emit()
        QMessageBox.information(self, "MediSync", self._t("forgot_msg"))

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.show_error(self._t("err_empty"))
            return

        self.login_button.setEnabled(False)

        try:
            user = self.app.login(
                username,
                password,
            )

            self.error_label.hide()

            self.login_successful.emit(user)

        except Exception:
            self.show_error(self._t("err_invalid"))

        finally:
            self.login_button.setEnabled(True)

    def show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()
