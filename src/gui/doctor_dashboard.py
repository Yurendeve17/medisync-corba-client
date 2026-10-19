from datetime import datetime
import csv

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDateEdit,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)
from PySide6.QtCore import QDate

from .icons import pixmap, qicon, illustration
from .icons import qicon
from .profile_dialog import ProfileDialog
from .result_dialog import ResultDialog
from application.medisync_app import normalize_doctor_name
from .reception_dashboard import Sidebar, NavItem, SIDEBAR_W
from .consultation_dialog import ConsultationDialog

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
        self._all_appointments = []

        self.setObjectName("doctorDashboard")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
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

        self.nav_buttons = []
        for icon, label, index in (("home", "Início", 0), ("users", "Consultas", 0), ("bar-chart", "Estatísticas", 1)):
            item = NavItem(icon, label)
            item.clicked.connect(lambda _=False, i=index: self.show_page(i))
            side.addWidget(item)
            self.nav_buttons.append((index, item))
        side.addStretch(1)
        footer = QLabel("Cuidando de pessoas,\ntodos os dias.")
        footer.setObjectName("sidebarFooter")
        side.addWidget(footer)
        main_layout.addWidget(sidebar)
        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(28, 8, 28, 8)
        topbar_layout.addLayout(self._build_header())
        content.addWidget(topbar)
        self.pages = QStackedWidget()
        self.pages.addWidget(self._overview_page())
        self.pages.addWidget(self._statistics_page())
        content.addWidget(self.pages, 1)
        main_layout.addLayout(content, 1)

        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._auto_refresh)
        self._refresh_timer.start(REFRESH_MS)

    def _sidebar_divider(self):
        line = QFrame()
        line.setObjectName("sidebarDivider")
        line.setFixedHeight(1)
        return line

    def _overview_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 18, 32, 24)
        layout.setSpacing(16)
        layout.addWidget(self._build_patients_card(), 3)
        layout.addWidget(self._build_queue_card(), 2)
        return page

    def _statistics_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 26, 32, 28)
        title = QLabel("Estatísticas clínicas")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        filters = QHBoxLayout()
        self.stats_from = QDateEdit(QDate.currentDate().addDays(-30))
        self.stats_to = QDateEdit(QDate.currentDate())
        for control in (self.stats_from, self.stats_to):
            control.setCalendarPopup(True)
            control.setDisplayFormat("yyyy-MM-dd")
        refresh = QPushButton("Actualizar")
        refresh.setObjectName("successButton")
        refresh.clicked.connect(self.load_statistics)
        export = QPushButton("Exportar CSV")
        export.setObjectName("secondaryButton")
        export.clicked.connect(self.export_statistics)
        filters.addWidget(QLabel("De")); filters.addWidget(self.stats_from)
        filters.addWidget(QLabel("Até")); filters.addWidget(self.stats_to)
        filters.addWidget(refresh); filters.addWidget(export); filters.addStretch(1)
        layout.addLayout(filters)
        self.stats_summary = QLabel("Consultas concluídas hoje: — · este mês: — · atendimento médio: — min")
        self.stats_summary.setObjectName("statValue")
        layout.addWidget(self.stats_summary)
        self.stats_period_summary = QLabel("Indicadores do período: —")
        self.stats_period_summary.setObjectName("cardDescription")
        layout.addWidget(self.stats_period_summary)
        card = QFrame(); card.setObjectName("modernCard")
        card_layout = QVBoxLayout(card)
        card_layout.addWidget(QLabel("Distribuição por diagnóstico"))
        self.diagnoses_table = QTableWidget(0, 2)
        self.diagnoses_table.setHorizontalHeaderLabels(["Diagnóstico", "Consultas"])
        self.diagnoses_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.diagnoses_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        card_layout.addWidget(self.diagnoses_table)
        layout.addWidget(card, 1)
        return page

    def show_page(self, index):
        self.pages.setCurrentIndex(index)
        for page_index, item in self.nav_buttons:
            item.set_active(page_index == index)
        if index == 1:
            self.load_statistics()

    def load_statistics(self):
        try:
            start = self.stats_from.date().toString("yyyy-MM-dd")
            end = self.stats_to.date().toString("yyyy-MM-dd")
            stats = self.app.doctor_statistics(start, end)
            self._last_stats = stats
            period_appointments = [a for a in self._all_appointments if start <= str(a.appointmentDate)[:10] <= end]
            completed = sum(getattr(a, "status", "") == "CONCLUIDA" for a in period_appointments)
            absences = sum(getattr(a, "status", "") == "FALTOU" for a in period_appointments)
            cancellations = sum(getattr(a, "status", "") == "CANCELADA" for a in period_appointments)
            self.stats_period_summary.setText(f"No período: {completed} concluídas · {absences} faltas · {cancellations} canceladas · {len(period_appointments)} consultas")
            self.stats_summary.setText(
                f"Consultas concluídas hoje: {stats.consultationsToday} · este mês: {stats.consultationsMonth} · atendimento médio: {stats.averageServiceMinutes:g} min"
            )
            rows = self.app.doctor_diagnosis_volumes(start, end)
            self.diagnoses_table.setRowCount(len(rows))
            for row, item in enumerate(rows):
                self.diagnoses_table.setItem(row, 0, QTableWidgetItem(str(item.diagnosis)))
                self.diagnoses_table.setItem(row, 1, QTableWidgetItem(str(item.consultations)))
        except Exception as error:
            ResultDialog.error(self, "Estatísticas indisponíveis", str(error))

    # ------------------------------------------------------------------
    # Construção da interface
    # ------------------------------------------------------------------
    def export_statistics(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar estatisticas", "estatisticas_medico.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            start = self.stats_from.date().toString("yyyy-MM-dd")
            end = self.stats_to.date().toString("yyyy-MM-dd")
            with open(path, "w", newline="", encoding="utf-8-sig") as output:
                writer = csv.writer(output, delimiter=";")
                writer.writerow(["Metrica", "Valor"])
                writer.writerow(["Periodo", f"{start} a {end}"])
                for label, status in (("Concluidas", "CONCLUIDA"), ("Faltas", "FALTOU"), ("Canceladas", "CANCELADA")):
                    total = sum(getattr(a, "status", "") == status and start <= str(a.appointmentDate)[:10] <= end for a in self._all_appointments)
                    writer.writerow([f"{label} no periodo", total])
                writer.writerow(["Atendimento medio (minutos)", getattr(getattr(self, "_last_stats", None), "averageServiceMinutes", "")])
                writer.writerow([])
                writer.writerow(["Diagnostico", "Consultas"])
                for row in range(self.diagnoses_table.rowCount()):
                    writer.writerow([self.diagnoses_table.item(row, 0).text(), self.diagnoses_table.item(row, 1).text()])
            ResultDialog.success(self, "Exportacao concluida", f"O ficheiro foi guardado em {path}")
        except Exception as error:
            ResultDialog.error(self, "Nao foi possivel exportar", str(error))

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

        filters = QHBoxLayout()
        self.patient_search = QLineEdit()
        self.patient_search.setPlaceholderText("Pesquisar paciente, ID ou especialidade")
        self.patient_search.textChanged.connect(self._apply_appointment_filters)
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Todos os estados", "AGENDADA", "CONFIRMADA", "AGUARDANDO", "CHAMADA", "EM_ATENDIMENTO", "CONCLUIDA", "CANCELADA", "FALTOU"])
        self.status_filter.currentIndexChanged.connect(self._apply_appointment_filters)
        self.date_from_filter = QDateEdit(QDate.currentDate().addMonths(-12))
        self.date_to_filter = QDateEdit(QDate.currentDate().addYears(5))
        for control in (self.date_from_filter, self.date_to_filter):
            control.setCalendarPopup(True)
            control.setDisplayFormat("yyyy-MM-dd")
            control.dateChanged.connect(self._apply_appointment_filters)
        filters.addWidget(self.patient_search, 2)
        filters.addWidget(QLabel("De")); filters.addWidget(self.date_from_filter)
        filters.addWidget(QLabel("Até")); filters.addWidget(self.date_to_filter)
        filters.addWidget(self.status_filter, 1)
        layout.addLayout(filters)

        self.call_status_label = QLabel()
        self.call_status_label.setObjectName("callStatus")
        self.call_status_label.hide()
        layout.addWidget(self.call_status_label)

        self.patients_table = QTableWidget()
        self.patients_table.setColumnCount(7)
        self.patients_table.setHorizontalHeaderLabels(
            ["Paciente", "ID", "Data e hora", "Especialidade", "Estado", "Atendimento", "Registo clínico"]
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
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
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
        self.load_queue()

    def show_profile(self):
        user = self.current_user or getattr(self.app, "current_user", None)
        if user is None:
            return
        role = getattr(user, "role", "")
        role_label = ROLE_LABELS.get(role, role or "Utilizador")
        ProfileDialog(user, self, self.app).exec()

    def request_logout(self):
        if self.logout_callback:
            self.logout_callback()

    # ------------------------------------------------------------------
    # Meus pacientes
    # ------------------------------------------------------------------
    def _auto_refresh(self):
        if self.current_user is not None and self.isVisible():
            self.load_patients(silent=True)
            self.load_queue(silent=True)

    def load_patients(self, silent=False):
        name = self._display_name()
        if not name:
            return

        try:
            appointments = self.app.list_appointments_for_doctor(name)
        except Exception as error:
            if not silent:
                ResultDialog.error(
                    self,
                    "Não foi possível carregar os pacientes",
                    f"O sistema não conseguiu carregar as consultas deste médico.\n\n{type(error).__name__}: {error}",
                )
            return

        appointments.sort(key=lambda a: a.appointmentDate)
        self._all_appointments = appointments
        self._apply_appointment_filters()

    def _apply_appointment_filters(self, *_):
        if not hasattr(self, "patient_search"):
            return
        query = self.patient_search.text().strip().casefold()
        selected = self.status_filter.currentText()
        selected_status = "" if selected == "Todos os estados" else selected
        start = self.date_from_filter.date().toString("yyyy-MM-dd")
        end = self.date_to_filter.date().toString("yyyy-MM-dd")
        appointments = [a for a in self._all_appointments
                        if start <= str(a.appointmentDate)[:10] <= end
                        and (not selected_status or getattr(a, "status", "") == selected_status)
                        and (not query or query in f"{a.patientName} {a.patientId} {a.specialty}".casefold())]
        self.patients_table.setRowCount(len(appointments))
        for row, appointment in enumerate(appointments):
            patient_name = getattr(appointment, "patientName", "") or f"Paciente #{appointment.patientId}"
            values = [patient_name, appointment.patientId, appointment.appointmentDate, appointment.specialty, getattr(appointment, "status", "AGENDADA")]
            for column, value in enumerate(values):
                self.patients_table.setItem(row, column, QTableWidgetItem(str(value)))
            status = getattr(appointment, "status", "AGENDADA")
            self.patients_table.setItem(row, 4, QTableWidgetItem(status.replace("_", " ").title()))
            action = QPushButton("Iniciar atendimento" if status == "CHAMADA" else "Registar e concluir" if status == "EM_ATENDIMENTO" else "-")
            action.setObjectName("tableActionButton")
            action.setEnabled(status in {"CHAMADA", "EM_ATENDIMENTO"})
            if status == "CHAMADA":
                action.clicked.connect(lambda _checked=False, aid=appointment.id: self.start_appointment(aid))
            elif status == "EM_ATENDIMENTO":
                action.clicked.connect(lambda _checked=False, a=appointment, n=patient_name: self.finish_appointment(a, n))
            self.patients_table.setCellWidget(row, 5, action)
            history = QPushButton("Historico / notas")
            history.setObjectName("secondaryButton")
            history.setFixedHeight(36)
            history.clicked.connect(lambda _checked=False, a=appointment, n=patient_name: self.open_consultation(a, n))
            self.patients_table.setCellWidget(row, 6, history)
        total = len(self._all_appointments)
        self.patients_count_label.setText(f"{len(appointments)} de {total} consultas")
        self.empty_label.setText("Ainda nao tem consultas agendadas." if total == 0 else "Nenhuma consulta corresponde aos filtros.")
        self.empty_label.setVisible(len(appointments) == 0)
        self.patients_table.setVisible(bool(appointments))

    def open_consultation(self, appointment, patient_name):
        dialog = ConsultationDialog(self.app, appointment, patient_name, self)
        if dialog.exec():
            self.load_patients(silent=True)

    def start_appointment(self, appointment_id):
        try:
            self.app.update_my_appointment_status(appointment_id, "EM_ATENDIMENTO")
            self.load_patients(silent=True)
            ResultDialog.success(self, "Atendimento iniciado", "O atendimento foi iniciado com sucesso.", details=[("Consulta", f"#{appointment_id}"), ("Estado", "EM_ATENDIMENTO")])
        except Exception as error:
            ResultDialog.error(self, "Não foi possível iniciar o atendimento", str(error))

    def finish_appointment(self, appointment, patient_name):
        appointment_id = int(appointment.id)
        try:
            dialog = ConsultationDialog(self.app, appointment, patient_name, self)
            if not dialog.exec():
                return
            self.app.update_my_appointment_status(appointment_id, "CONCLUIDA")
            self.load_patients(silent=True)
            ResultDialog.success(self, "Atendimento concluído", "O atendimento foi concluído e o estado foi guardado.", details=[("Consulta", f"#{appointment_id}"), ("Estado", "CONCLUIDA")])
        except Exception as error:
            ResultDialog.error(self, "Não foi possível concluir o atendimento", str(error))

    # ------------------------------------------------------------------
    # Fila de atendimento (já existente)
    # ------------------------------------------------------------------
    def load_queue(self, silent=False):
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
            if queue_size:
                wait_minutes = self.app.estimated_wait_minutes(int(waiting_entries[0].id))
                self.queue_size_label.setText(f"Na sua fila: {queue_size} · espera estimada para o próximo: {wait_minutes:g} min")
            else:
                self.queue_size_label.setText("Na sua fila: 0")

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

            if not silent:
                ResultDialog.error(
                    self,
                    "Nao foi possivel carregar a fila",
                    f"O sistema nao conseguiu carregar a fila.\n\n{type(error).__name__}: {error}",
                )

    def call_next_patient(self):
        doctor_name = self._display_name()
        if not doctor_name:
            return

        try:
            entry = self.app.call_next_queue_entry_for_doctor(doctor_name)

            if getattr(entry, "id", 0) == 0:
                ResultDialog.info(
                    self,
                    "Fila vazia",
                    "Não existem pacientes aguardando na sua fila.",
                )
                return

            self.next_patient_value.setText(f"#{entry.patientId} — {entry.patientName}")

            if entry.appointmentId:
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
                    ("Recepção", "Notificada atomicamente" if entry.appointmentId else "—"),
                ],
            )

        except Exception as error:
            ResultDialog.error(
                self,
                "Não foi possível chamar o próximo paciente",
                str(error),
            )
