from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QToolButton, QMenu,
)

from .icons import qicon



class DoctorDashboard(QWidget):
    def __init__(self, app, stack, logout_callback=None):
        super().__init__()

        self.app = app
        self.stack = stack
        self.logout_callback = logout_callback
        self.current_user = None

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            40,
            30,
            40,
            30,
        )

        main_layout.setSpacing(20)

        # -------------------------
        # Cabeçalho
        # -------------------------

        header_layout = QHBoxLayout()

        title_layout = QVBoxLayout()

        title = QLabel("Área do Médico")
        title.setObjectName("sectionTitle")

        subtitle = QLabel(
            "Gestão da fila e atendimento de pacientes"
        )
        subtitle.setObjectName("sectionSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        back_button = QPushButton("Voltar")
        back_button.setObjectName("secondaryButton")
        back_button.clicked.connect(
            lambda: self.stack.setCurrentIndex(0)
        )

        self.profile_button = QToolButton()
        self.profile_button.setObjectName("profileButton")
        self.profile_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.profile_button.setPopupMode(QToolButton.InstantPopup)
        self.profile_button.setIcon(qicon("user", "#24425c", 22))
        self.profile_button.setText("Utilizador\\nMédico")
        menu = QMenu(self.profile_button)
        menu.addAction(qicon("user", "#0ca466", 16), "Meu perfil").triggered.connect(self.show_profile)
        menu.addSeparator()
        menu.addAction(qicon("logout", "#d14d4d", 16), "Terminar sessão").triggered.connect(self.request_logout)
        self.profile_button.setMenu(menu)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(self.profile_button)
        header_layout.addWidget(back_button)

        main_layout.addLayout(header_layout)

        # -------------------------
        # Estado da fila
        # -------------------------

        queue_card = QFrame()
        queue_card.setObjectName("card")

        queue_layout = QVBoxLayout(queue_card)

        queue_layout.setContentsMargins(
            20,
            18,
            20,
            18,
        )

        queue_layout.setSpacing(10)

        queue_header = QHBoxLayout()

        queue_title = QLabel(
            "Fila de atendimento"
        )
        queue_title.setObjectName(
            "sectionTitle"
        )

        self.queue_size_label = QLabel(
            "Na fila: 0"
        )
        self.queue_size_label.setObjectName(
            "sectionSubtitle"
        )

        call_button = QPushButton(
            "Chamar próximo"
        )

        call_button.setObjectName(
            "successButton"
        )

        call_button.clicked.connect(
            self.call_next_patient
        )

        refresh_button = QPushButton(
            "Actualizar"
        )
        refresh_button.setObjectName(
            "secondaryButton"
        )
        refresh_button.clicked.connect(
            self.load_queue
        )

        queue_header.addWidget(queue_title)
        queue_header.addWidget(
            self.queue_size_label
        )
        queue_header.addStretch()
        queue_header.addWidget(
            call_button
        )
        queue_header.addWidget(
            refresh_button
        )

        queue_layout.addLayout(queue_header)

        # -------------------------
        # Próximo paciente
        # -------------------------

        next_patient_card = QFrame()
        next_patient_card.setObjectName(
            "roleCard"
        )

        next_patient_layout = QHBoxLayout(
            next_patient_card
        )

        next_patient_layout.setContentsMargins(
            20,
            15,
            20,
            15,
        )

        next_label = QLabel(
            "Próximo paciente"
        )
        next_label.setObjectName(
            "sectionSubtitle"
        )

        self.next_patient_value = QLabel(
            "—"
        )
        self.next_patient_value.setObjectName(
            "sectionTitle"
        )

        next_patient_layout.addWidget(
            next_label
        )

        next_patient_layout.addWidget(
            self.next_patient_value
        )

        next_patient_layout.addStretch()

        queue_layout.addWidget(
            next_patient_card
        )

        # -------------------------
        # Tabela da fila
        # -------------------------

        self.queue_table = QTableWidget()

        self.queue_table.setColumnCount(2)

        self.queue_table.setHorizontalHeaderLabels(
            [
                "Posição",
                "ID do paciente",
            ]
        )

        self.queue_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.queue_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.queue_table.horizontalHeader().setStretchLastSection(
            True
        )

        queue_layout.addWidget(
            self.queue_table
        )

        main_layout.addWidget(
            queue_card,
            1,
        )

        self.load_queue()

    def load_queue(self):
        try:
            queue_size = self.app.get_queue_size()

            self.queue_size_label.setText(
                f"Na fila: {queue_size}"
            )

            self.queue_table.setRowCount(0)

            if queue_size > 0:
                self.next_patient_value.setText(
                    str(self.app.peek_next_patient())
                )

            else:
                self.next_patient_value.setText(
                    "Nenhum paciente"
                )

        except Exception as error:
            print(
                "ERRO AO CARREGAR FILA:",
                type(error).__name__,
                repr(error),
                flush=True,
            )

            QMessageBox.critical(
                self,
                "Erro",
                (
                    "Não foi possível carregar a fila:\n"
                    f"{type(error).__name__}: {error}"
                ),
            )

    def set_current_user(self, user):
        self.current_user = user
        full_name = getattr(user, "fullName", "") or getattr(user, "username", "Utilizador")
        role = getattr(user, "role", "")
        role_label = {"RECEPTION": "Recepção", "DOCTOR": "Médico"}.get(role, role or "Utilizador")
        self.profile_button.setText(f"{full_name}\\n{role_label}")

    def show_profile(self):
        user = self.current_user or getattr(self.app, "current_user", None)
        if user is None:
            return
        role = getattr(user, "role", "")
        role_label = {"RECEPTION": "Recepção", "DOCTOR": "Médico"}.get(role, role or "Utilizador")
        QMessageBox.information(self, "Meu perfil", f"Nome: {getattr(user, 'fullName', '')}\\nUtilizador: {getattr(user, 'username', '')}\\nPerfil: {role_label}")

    def request_logout(self):
        if self.logout_callback:
            self.logout_callback()

    def call_next_patient(self):
        try:
            patient_id = self.app.get_next_patient()

            if patient_id == 0:
                QMessageBox.information(
                    self,
                    "Fila vazia",
                    "Não existem pacientes na fila.",
                )
                return

            self.next_patient_value.setText(
                str(patient_id)
            )

            self.load_queue()

            QMessageBox.information(
                self,
                "Paciente chamado",
                (
                    f"O paciente #{patient_id} "
                    "foi chamado para atendimento."
                ),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro",
                (
                    "Não foi possível chamar "
                    f"o próximo paciente:\n{error}"
                ),
            )