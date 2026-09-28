from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LoginPage(QWidget):

    login_successful = Signal(object)

    def __init__(self, app):
        super().__init__()

        self.app = app

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(80, 60, 80, 60)

        main_layout.addStretch()

        title = QLabel("MediSync")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel(
            "Sistema de Gestão de Atendimento Hospitalar"
        )
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(30)

        card = QFrame()
        card.setObjectName("card")
        card.setMaximumWidth(420)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 35, 35, 35)
        card_layout.setSpacing(14)

        card_title = QLabel("Iniciar sessão")
        card_title.setObjectName("sectionTitle")
        card_title.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nome de utilizador")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(
            QLineEdit.Password
        )

        self.login_button = QPushButton("Entrar")
        self.login_button.clicked.connect(self.login)

        self.error_label = QLabel()
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        self.password_input.returnPressed.connect(
            self.login
        )

        card_layout.addWidget(card_title)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.error_label)
        card_layout.addSpacing(5)
        card_layout.addWidget(self.login_button)

        wrapper_layout = QVBoxLayout()
        wrapper_layout.addWidget(
            card,
            alignment=Qt.AlignCenter,
        )

        main_layout.addLayout(wrapper_layout)
        main_layout.addStretch()

        self.username_input.setFocus()

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.show_error(
                "Preencha o nome de utilizador e a password."
            )
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
            self.show_error(
                "Nome de utilizador ou password inválidos."
            )

        finally:
            self.login_button.setEnabled(True)

    def show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()