from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .icons import qicon
from .profile_dialog import ProfileDialog
from .result_dialog import ResultDialog
from application.medisync_app import normalize_doctor_name

REFRESH_MS = 20_000
ROLE_LABELS = {"RECEPTION": "Recepção", "DOCTOR": "Médico"}


class DoctorDashboard(QWidget):
    def __init__(self, app, stack, logout_callback=None):
        super().__init__()

        self.app = app
        self.stack = stack
        self.logout_callback = logout_callback
        self.current_user = None
        self._called_appointments = set()

        self.setObjectName("doctorDashboard")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        main_layout.addLayout(self._build_header())
        main_layout.addWidget(self._build_patients_card(), 3)
        main_layout.addWidget(self._build_queue_card(), 2)

        self.load_queue()

        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._auto_refresh)
        self._refresh_timer.start(REFRESH_MS)

    # ------------------------------------------------------------------
    # Construção da interface
    # ------------------------------------------------------------------
    def _build_header(self):
        header = QHBoxLayout()

        titles = QVBoxLayout()
        titles.setSpacing(2)
        title = QLabel("Área do Médico")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Os seus pacientes e a fila de atendimento")
        subtitle.setObjectName("pageSubtitle")
        titles.addWidget(title)
        titles.addWidget(subtitle)

        back_button = QPushButton("Voltar")
        back_button.setObjectName("secondaryButton")
        back_button.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.profile_button = QToolButton()
        self.profile_button.setObjectName("profileButton")
        self.profile_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.profile_button.setPopupMode(QToolButton.InstantPopup)
        self.profile_button.setIcon(qicon("user", "#24425c", 22))
        self.profile_button.setText("Utilizador · Médico")
        menu = QMenu(self.profile_button)
        menu.setObjectName("profileMenu")
        menu.addAction(qicon("user", "#0ca466", 16), "Meu perfil").triggered.connect(self.show_profile)
        menu.addSeparator()
        menu.addAction(qicon("logout", "#d14d4d", 16), "Terminar sessão").triggered.connect(self.request_logout)
        self.profile_button.setMenu(menu)

        header.addLayout(titles)
        header.addStretch()
        header.addWidget(self.profile_button)
        header.addWidget(back_button)
        return header

    def _build_patients_card(self):
        card = QFrame()
        card.setObjectName("modernCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 18, 22, 20)
        layout.setSpacing(12)

        top = QHBoxLayout()
        title = QLabel("Meus pacientes")
        title.setObjectName("cardTitle")
        self.patients_count_label = QLabel("0 consultas")
        self.patients_count_label.setObjectName("cardDescription")

        refresh = QPushButton("Actualizar")
        refresh.setObjectName("secondaryButton")
        refresh.setFixedHeight(44)
        refresh.clicked.connect(self.load_patients)

        top.addWidget(title)
        top.addSpacing(10)
        top.addWidget(self.patients_count_label)
        top.addStretch()
        top.addWidget(refresh)
        layout.addLayout(top)

        self.call_status_label = QLabel()
        self.call_status_label.setObjectName("callStatus")
        self.call_status_label.hide()
        layout.addWidget(self.call_status_label)

        self.patients_table = QTableWidget()
        self.patients_table.setColumnCount(6)
        self.patients_table.setHorizontalHeaderLabels(
            ["Paciente", "ID", "Data e hora", "Especialidade", "Estado", ""]
        )
        self.patients_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.patients_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.patients_table.setAlternatingRowColors(True)
        self.patients_table.verticalHeader().setVisible(False)
        self.patients_table.verticalHeader().setDefaultSectionSize(54)
        header = self.patients_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.patients_table.setColumnWidth(4, 170)
        layout.addWidget(self.patients_table, 1)

        self.empty_label = QLabel("Ainda não tem consultas agendadas.")
        self.empty_label.setObjectName("cardDescription")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.hide()
        layout.addWidget(self.empty_label)
        return card

    def _build_queue_card(self):
        card = QFrame()
        card.setObjectName("modernCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 18, 22, 20)
        layout.setSpacing(12)

        top = QHBoxLayout()
        title = QLabel("Fila de atendimento")
        title.setObjectName("cardTitle")
        self.queue_size_label = QLabel("Na fila: 0")
        self.queue_size_label.setObjectName("cardDescription")

        call_button = QPushButton("Chamar próximo")
        call_button.setObjectName("successButton")
        call_button.clicked.connect(self.call_next_patient)

        refresh = QPushButton("Actualizar")
        refresh.setObjectName("secondaryButton")
        refresh.clicked.connect(self.load_queue)

        top.addWidget(title)
        top.addSpacing(10)
        top.addWidget(self.queue_size_label)
        top.addStretch()
        top.addWidget(call_button)
        top.addWidget(refresh)
        layout.addLayout(top)

        box = QFrame()
        box.setObjectName("nextPatientBox")
        box_layout = QHBoxLayout(box)
        box_layout.setContentsMargins(18, 12, 18, 12)
        next_label = QLabel("Próximo paciente")
        next_label.setObjectName("cardDescription")
        self.next_patient_value = QLabel("—")
        self.next_patient_value.setObjectName("cardTitle")
        box_layout.addWidget(next_label)
        box_layout.addWidget(self.next_patient_value)
        box_layout.addStretch()
        layout.addWidget(box)
        layout.addStretch()
        return card

    # ------------------------------------------------------------------
    # Utilizador
    # ------------------------------------------------------------------
    def _display_name(self):
        user = self.current_user or getattr(self.app, "current_user", None)
        if user is None:
            return ""
        return getattr(user, "fullName", "") or getattr(user, "username", "")

    def set_current_user(self, user):
        self.current_user = user
        self._called_appointments.clear()
        self.call_status_label.hide()

        role = getattr(user, "role", "")
        role_label = ROLE_LABELS.get(role, role or "Utilizador")
        self.profile_button.setText(f"{self._display_name() or 'Utilizador'}  ·  {role_label}")

        self.load_patients()

    def show_profile(self):
        user = self.current_user or getattr(self.app, "current_user", None)
        if user is None:
            return
        role = getattr(user, "role", "")
        role_label = ROLE_LABELS.get(role, role or "Utilizador")
        ProfileDialog(user, self).exec()

    def request_logout(self):
        if self.logout_callback:
            self.logout_callback()

    # ------------------------------------------------------------------
    # Meus pacientes
    # ------------------------------------------------------------------
    def _auto_refresh(self):
        if self.current_user is not None and self.isVisible():
            self.load_patients(silent=True)

    def load_patients(self, silent=False):
        name = self._display_name()
        if not name:
            return

        try:
            appointments = self.app.list_appointments_for_doctor(name)
            names = {p.id: p.fullName for p in self.app.list_patients()}
        except Exception as error:
            if not silent:
                ResultDialog.error(
                    self,
                    "Não foi possível carregar os pacientes",
                    f"O sistema não conseguiu carregar as consultas deste médico.\n\n{type(error).__name__}: {error}",
                )
            return

        appointments.sort(key=lambda a: a.appointmentDate)

        self.patients_table.setRowCount(len(appointments))
        for row, appointment in enumerate(appointments):
            patient_name = names.get(appointment.patientId, f"Paciente #{appointment.patientId}")
            values = [patient_name, appointment.patientId, appointment.appointmentDate, appointment.specialty, getattr(appointment, "status", "AGENDADA")]
            for column, value in enumerate(values):
                self.patients_table.setItem(row, column, QTableWidgetItem(str(value)))

            already_called = appointment.id in self._called_appointments
            status = getattr(appointment, "status", "AGENDADA")
            if status == "EM_ATENDIMENTO":
                button = QPushButton("Concluir atendimento")
                button.clicked.connect(lambda _checked=False, aid=appointment.id: self.finish_appointment(aid))
            elif status == "CHAMADA":
                button = QPushButton("Iniciar atendimento")
                button.clicked.connect(lambda _checked=False, aid=appointment.id: self.start_appointment(aid))
            elif status == "AGUARDANDO":
                button = QPushButton("Chamar novamente" if already_called else "Chamar paciente")
            elif status == "CONFIRMADA":
                button = QPushButton("Presença confirmada")
                button.setEnabled(False)
            elif status == "AGENDADA":
                button = QPushButton("Aguardando chegada")
                button.setEnabled(False)
            elif status in {"CONCLUIDA", "CANCELADA", "FALTOU"}:
                button = QPushButton(status.replace("_", " ").title())
                button.setEnabled(False)
            else:
                button = QPushButton(status.replace("_", " ").title())
                button.setEnabled(False)
            button.setObjectName("tableActionButton")
            button.setProperty("appointmentStatus", status)
            button.setCursor(Qt.PointingHandCursor)
            button.setFixedHeight(36)
            if status == "AGUARDANDO":
                button.clicked.connect(
                    lambda _checked=False, a=appointment, n=patient_name, b=button: self.call_patient(a, n, b)
                )
            holder = QWidget()
            holder_layout = QHBoxLayout(holder)
            holder_layout.setContentsMargins(6, 0, 6, 0)
            holder_layout.addWidget(button)
            self.patients_table.setCellWidget(row, 4, holder)

        total = len(appointments)
        self.patients_count_label.setText(f"{total} consulta" + ("" if total == 1 else "s"))
        self.empty_label.setVisible(total == 0)
        self.patients_table.setVisible(total > 0)

    def call_patient(self, appointment, patient_name, button):
        button.setEnabled(False)
        try:
            self.app.update_appointment_status(appointment.id, "CHAMADA")
            self.app.call_patient(appointment, patient_name)
        except Exception as error:
            ResultDialog.error(
                self,
                "Não foi possível chamar o paciente",
                "Confirme que o serviço de notificações está activo no servidor.\n\n"
                f"{type(error).__name__}: {error}",
            )
            return
        finally:
            button.setEnabled(True)

        self._called_appointments.add(appointment.id)
        button.setText("Chamar novamente")
        self.call_status_label.setText(
            f"✓ {patient_name} foi chamado às {datetime.now():%H:%M}. Estado: CHAMADA. A recepção foi notificada."
        )
        self.call_status_label.show()
        ResultDialog.success(
            self,
            "Paciente chamado",
            "O paciente foi chamado e a recepção foi notificada.",
            details=[("Paciente", patient_name), ("Consulta", f"#{appointment.id}"), ("Estado", "CHAMADA")],
        )

    def start_appointment(self, appointment_id):
        try:
            self.app.update_appointment_status(appointment_id, "EM_ATENDIMENTO")
            self.load_patients(silent=True)
            ResultDialog.success(self, "Atendimento iniciado", "O atendimento foi iniciado com sucesso.", details=[("Consulta", f"#{appointment_id}"), ("Estado", "EM_ATENDIMENTO")])
        except Exception as error:
            ResultDialog.error(self, "Não foi possível iniciar o atendimento", str(error))

    def finish_appointment(self, appointment_id):
        try:
            self.app.update_appointment_status(appointment_id, "CONCLUIDA")
            self.load_patients(silent=True)
            ResultDialog.success(self, "Atendimento concluído", "O atendimento foi concluído e o estado foi guardado.", details=[("Consulta", f"#{appointment_id}"), ("Estado", "CONCLUIDA")])
        except Exception as error:
            ResultDialog.error(self, "Não foi possível concluir o atendimento", str(error))

    # ------------------------------------------------------------------
    # Fila de atendimento (já existente)
    # ------------------------------------------------------------------
    def load_queue(self):
        doctor_name = self._display_name()
        if not doctor_name:
            return

        try:
            waiting_entries = [
                entry
                for entry in self.app.list_queue()
                if getattr(entry, "status", "") == "AGUARDANDO"
                and normalize_doctor_name(getattr(entry, "doctor", ""))
                == normalize_doctor_name(doctor_name)
            ]

            queue_size = len(waiting_entries)
            self.queue_size_label.setText(f"Na sua fila: {queue_size}")

            if queue_size > 0:
                entry = self.app.peek_next_queue_entry_for_doctor(doctor_name)
                if getattr(entry, "id", 0) == 0:
                    self.next_patient_value.setText("Nenhum paciente")
                else:
                    label = f"#{entry.patientId} — {entry.patientName}"
                    if entry.appointmentId:
                        label += f"  · Consulta #{entry.appointmentId}"
                    self.next_patient_value.setText(label)
            else:
                self.next_patient_value.setText("Nenhum paciente")

        except Exception as error:
            print(
                "ERRO AO CARREGAR FILA:",
                type(error).__name__,
                repr(error),
                flush=True,
            )

            ResultDialog.error(
                self,
                "Não foi possível carregar a fila",
                f"O sistema não conseguiu carregar a fila.\n\n{type(error).__name__}: {error}",
            )

    def call_next_patient(self):
        doctor_name = self._display_name()
        if not doctor_name:
            return

        try:
            entry = self.app.get_next_queue_entry_for_doctor(doctor_name)

            if getattr(entry, "id", 0) == 0:
                ResultDialog.info(
                    self,
                    "Fila vazia",
                    "Não existem pacientes aguardando na sua fila.",
                )
                return

            self.next_patient_value.setText(f"#{entry.patientId} — {entry.patientName}")

            if entry.appointmentId:
                appointment = self.app.find_appointment_by_id(entry.appointmentId)
                self.app.call_patient(appointment, entry.patientName)
                self._called_appointments.add(entry.appointmentId)

            self.load_queue()

            ResultDialog.success(
                self,
                "Paciente chamado",
                "O próximo paciente foi chamado para atendimento.",
                details=[
                    ("Paciente", f"{entry.patientName} (#{entry.patientId})"),
                    ("Consulta", f"#{entry.appointmentId}" if entry.appointmentId else "Sem consulta"),
                    ("Estado", "CHAMADA"),
                    ("Recepção", "Notificada" if entry.appointmentId else "—"),
                ],
            )

        except Exception as error:
            ResultDialog.error(
                self,
                "Não foi possível chamar o próximo paciente",
                str(error),
            )
