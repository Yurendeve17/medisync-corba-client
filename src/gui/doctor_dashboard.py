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
)


class DoctorDashboard(QWidget):
    def __init__(self, app, stack):
        super().__init__()

        self.app = app
        self.stack = stack

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

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
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
                    str(self.app.get_next_patient())
                )

            else:
                self.next_patient_value.setText(
                    "Nenhum paciente"
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro",
                (
                    "Não foi possível carregar "
                    f"a fila:\n{error}"
                ),
            )