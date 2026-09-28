from PySide6.QtCore import Qt, QDateTime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QMessageBox,
    QStackedWidget, QDateTimeEdit, QSizePolicy
)


class ReceptionDashboard(QWidget):
    """Interface moderna da recepção, mantendo os serviços CORBA existentes."""

    def __init__(self, app, stack):
        super().__init__()
        self.app = app
        self.stack = stack
        self.setObjectName("receptionDashboard")

        self.content_stack = QStackedWidget()
        self.nav_buttons = []

        self._build_shell()
        self._build_pages()

        self.show_page(0)
        self.load_patients()
        self.load_appointments()

    # ------------------------------------------------------------------
    # Shell
    # ------------------------------------------------------------------
    def _build_shell(self):
        shell = QHBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(238)

        side = QVBoxLayout(sidebar)
        side.setContentsMargins(16, 20, 16, 18)
        side.setSpacing(7)

        logo = QLabel("♥  MediSync")
        logo.setObjectName("logo")
        logo_sub = QLabel("Sistema Hospitalar")
        logo_sub.setObjectName("logoSubtitle")
        side.addWidget(logo)
        side.addWidget(logo_sub)
        side.addSpacing(22)

        side.addWidget(self._nav("⌂", "Início", 0))
        side.addWidget(self._nav("♙", "Recepção", 0, parent=True))
        side.addWidget(self._nav("▣", "Agendar consulta", 1))
        side.addWidget(self._nav("♙", "Registar paciente", 2))
        side.addWidget(self._nav("▤", "Pacientes", 3))
        side.addWidget(self._nav("□", "Consultas", 4))
        side.addWidget(self._nav("♧", "Médicos", 5))
        side.addWidget(self._nav("▥", "Relatórios", 6))
        side.addWidget(self._nav("⚙", "Configurações", 7))
        side.addStretch()

        footer_icon = QLabel("〰")
        footer_icon.setObjectName("sidebarPulse")
        footer_text = QLabel("Cuidando de pessoas,\ntodos os dias.")
        footer_text.setObjectName("sidebarFooter")
        side.addWidget(footer_icon)
        side.addWidget(footer_text)

        shell.addWidget(sidebar)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        header = QFrame()
        header.setObjectName("topbar")
        header.setFixedHeight(76)
        h = QHBoxLayout(header)
        h.setContentsMargins(28, 14, 28, 14)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("globalSearch")
        self.search_input.setPlaceholderText(
            "Pesquisar paciente, consulta, médico..."
        )
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMaximumWidth(620)
        h.addWidget(self.search_input)
        h.addStretch()

        bell = QLabel("♧  ³")
        bell.setObjectName("topIcon")
        h.addWidget(bell)
        calendar = QLabel("▣")
        calendar.setObjectName("topIcon")
        h.addWidget(calendar)
        theme = QLabel("☼")
        theme.setObjectName("topIcon")
        h.addWidget(theme)

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setObjectName("topSeparator")
        h.addWidget(separator)

        user = QLabel("  Yuren Deve\n  Recepção")
        user.setObjectName("userProfile")
        h.addWidget(user)

        back = QPushButton("←  Voltar")
        back.setObjectName("backButton")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        h.addWidget(back)

        right.addWidget(header)
        right.addWidget(self.content_stack, 1)
        shell.addLayout(right, 1)

    def _nav(self, icon, text, index, parent=False):
        button = QPushButton(f"{icon}   {text}")
        button.setObjectName("navButton")
        if parent:
            button.setObjectName("navSection")
        else:
            button.clicked.connect(lambda _, i=index: self.show_page(i))
            self.nav_buttons.append((index, button))
        return button

    # ------------------------------------------------------------------
    # Pages
    # ------------------------------------------------------------------
    def _build_pages(self):
        self.content_stack.addWidget(self._home_page())
        self.content_stack.addWidget(self._appointment_page())
        self.content_stack.addWidget(self._register_page())
        self.content_stack.addWidget(self._patients_page())
        self.content_stack.addWidget(self._appointments_page())

    def _page_header(self, icon, title, subtitle):
        wrapper = QFrame()
        wrapper.setObjectName("pageHero")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(30, 26, 30, 18)

        icon_box = QLabel(icon)
        icon_box.setObjectName("heroIcon")
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setFixedSize(62, 62)

        texts = QVBoxLayout()
        texts.setSpacing(3)
        t = QLabel(title)
        t.setObjectName("pageTitle")
        s = QLabel(subtitle)
        s.setObjectName("pageSubtitle")
        texts.addWidget(t)
        texts.addWidget(s)

        layout.addWidget(icon_box)
        layout.addSpacing(16)
        layout.addLayout(texts)
        layout.addStretch()
        return wrapper

    def _home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 26, 30, 30)
        layout.setSpacing(20)

        layout.addWidget(self._page_header(
            "♙", "Área da Recepção",
            "Gestão de pacientes e atendimento hospitalar"
        ))

        grid = QHBoxLayout()
        grid.setSpacing(18)

        grid.addWidget(self._action_card(
            "▣", "Agendar consulta",
            "Marque uma consulta para um paciente já cadastrado.",
            "Agendar consulta", 1, "successButton"
        ))
        grid.addWidget(self._action_card(
            "♙+", "Registar paciente",
            "Adicione um novo paciente ao sistema.",
            "Registar paciente", 2, "blueButton"
        ))
        layout.addLayout(grid)

        stats = QHBoxLayout()
        stats.setSpacing(18)
        self.home_patient_stat = self._stat_card("♙", "Pacientes", "0")
        self.home_appointment_stat = self._stat_card("▣", "Consultas", "0")
        stats.addWidget(self.home_patient_stat)
        stats.addWidget(self.home_appointment_stat)
        layout.addLayout(stats)

        layout.addStretch()
        return page

    def _action_card(self, icon, title, desc, button_text, page_index, button_style):
        card = QFrame()
        card.setObjectName("modernCard")
        card.setMinimumHeight(230)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 22, 24, 22)
        lay.setSpacing(12)

        ic = QLabel(icon)
        ic.setObjectName("cardIcon")
        ic.setAlignment(Qt.AlignCenter)
        ic.setFixedSize(52, 52)
        lay.addWidget(ic, alignment=Qt.AlignLeft)

        t = QLabel(title)
        t.setObjectName("cardTitle")
        d = QLabel(desc)
        d.setObjectName("cardDescription")
        d.setWordWrap(True)
        lay.addWidget(t)
        lay.addWidget(d)
        lay.addStretch()

        b = QPushButton(button_text)
        b.setObjectName(button_style)
        b.clicked.connect(lambda: self.show_page(page_index))
        b.setMinimumHeight(42)
        lay.addWidget(b)
        return card

    def _stat_card(self, icon, title, value):
        card = QFrame()
        card.setObjectName("statCard")
        lay = QHBoxLayout(card)
        lay.setContentsMargins(20, 15, 20, 15)
        ic = QLabel(icon)
        ic.setObjectName("statIcon")
        lay.addWidget(ic)
        texts = QVBoxLayout()
        v = QLabel(value)
        v.setObjectName("statValue")
        v.setProperty("stat", True)
        l = QLabel(title)
        l.setObjectName("statLabel")
        texts.addWidget(v)
        texts.addWidget(l)
        lay.addLayout(texts)
        return card

    def _appointment_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 24, 30, 30)
        layout.setSpacing(16)
        layout.addWidget(self._page_header(
            "▣", "Agendar consulta",
            "Marque uma consulta para um paciente já cadastrado no sistema."
        ))

        card = QFrame()
        card.setObjectName("modernCard")
        form = QVBoxLayout(card)
        form.setContentsMargins(26, 22, 26, 24)
        form.setSpacing(12)

        form.addWidget(self._section_label("♙", "Dados do paciente"))

        self.appointment_patient_id_input = self._field(
            "ID do paciente", "Ex.: 1202"
        )
        self.appointment_patient_id_input.setObjectName("appointmentPatientId")
        form.addWidget(self._labeled("ID do paciente", self.appointment_patient_id_input))

        self.appointment_doctor_input = QComboBox()
        self.appointment_doctor_input.addItems(
            ["Seleccione o médico", "Yuren", "Médico de serviço"]
        )
        form.addWidget(self._labeled("Médico", self.appointment_doctor_input))

        form.addSpacing(8)
        form.addWidget(self._section_label("▣", "Detalhes da consulta"))

        date_row = QHBoxLayout()
        self.appointment_date_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.appointment_date_input.setCalendarPopup(True)
        self.appointment_date_input.setDisplayFormat("dd/MM/yyyy HH:mm")
        date_row.addWidget(self._labeled("Data e hora", self.appointment_date_input), 1)

        self.appointment_specialty_input = QComboBox()
        self.appointment_specialty_input.setEditable(True)
        self.appointment_specialty_input.addItems(
            ["Clínica Geral", "Cardiologia", "Pediatria", "Medicina Dentária", "Outra"]
        )
        date_row.addWidget(self._labeled("Especialidade", self.appointment_specialty_input), 1)
        form.addLayout(date_row)

        actions = QHBoxLayout()
        schedule = QPushButton("▣   Agendar consulta")
        schedule.setObjectName("successButton")
        schedule.clicked.connect(self.schedule_appointment)
        clear = QPushButton("Limpar")
        clear.setObjectName("secondaryButton")
        clear.clicked.connect(self.clear_appointment_form)
        actions.addWidget(schedule)
        actions.addWidget(clear)
        actions.addStretch()
        form.addLayout(actions)

        layout.addWidget(card)
        layout.addStretch()
        return page

    def _register_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 24, 30, 30)
        layout.setSpacing(16)
        layout.addWidget(self._page_header(
            "♙+", "Registar paciente",
            "Adicione um novo paciente ao sistema."
        ))

        card = QFrame()
        card.setObjectName("modernCard")
        form = QVBoxLayout(card)
        form.setContentsMargins(26, 22, 26, 24)
        form.setSpacing(12)

        form.addWidget(self._section_label("♙", "Dados pessoais"))

        self.full_name_input = self._field(
            "Nome completo do paciente"
        )
        form.addWidget(self._labeled("Nome completo", self.full_name_input))

        row = QHBoxLayout()
        self.birth_date_input = self._field("Ex.: 2000-05-20")
        row.addWidget(self._labeled("Data de nascimento", self.birth_date_input), 1)
        self.gender_input = QComboBox()
        self.gender_input.addItems(
            ["Seleccione o género", "Masculino", "Feminino", "Outro"]
        )
        row.addWidget(self._labeled("Género", self.gender_input), 1)
        form.addLayout(row)

        self.phone_input = self._field("Contacto telefónico")
        form.addWidget(self._labeled("Telefone", self.phone_input))

        form.addSpacing(8)
        form.addWidget(self._section_label("⌖", "Contacto"))

        contact_note = QLabel(
            "O contacto telefónico é utilizado para identificação e comunicação com o paciente."
        )
        contact_note.setObjectName("helperText")
        contact_note.setWordWrap(True)
        form.addWidget(contact_note)

        actions = QHBoxLayout()
        register = QPushButton("♙+   Registar paciente")
        register.setObjectName("successButton")
        register.clicked.connect(self.register_patient)
        clear = QPushButton("Limpar")
        clear.setObjectName("secondaryButton")
        clear.clicked.connect(self.clear_form)
        actions.addWidget(register)
        actions.addWidget(clear)
        actions.addStretch()
        form.addLayout(actions)

        layout.addWidget(card)
        layout.addStretch()
        return page

    def _patients_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 24, 30, 30)
        layout.setSpacing(16)
        layout.addWidget(self._page_header(
            "♙", "Pacientes",
            "Consulte os pacientes registados e adicione-os à fila."
        ))

        card = QFrame()
        card.setObjectName("modernCard")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(22, 20, 22, 22)

        actions = QHBoxLayout()
        title = QLabel("Pacientes registados")
        title.setObjectName("cardTitle")
        actions.addWidget(title)
        actions.addStretch()
        queue = QPushButton("Adicionar à fila")
        queue.setObjectName("successButton")
        queue.clicked.connect(self.add_selected_patient_to_queue)
        refresh = QPushButton("Actualizar")
        refresh.setObjectName("secondaryButton")
        refresh.clicked.connect(self.load_patients)
        actions.addWidget(queue)
        actions.addWidget(refresh)
        lay.addLayout(actions)

        self.patients_table = self._table(
            ["ID", "Nome completo", "Nascimento", "Género", "Telefone"]
        )
        lay.addWidget(self.patients_table)
        layout.addWidget(card, 1)
        return page

    def _appointments_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 24, 30, 30)
        layout.setSpacing(16)
        layout.addWidget(self._page_header(
            "▣", "Consultas",
            "Consulte e actualize as consultas agendadas."
        ))

        card = QFrame()
        card.setObjectName("modernCard")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(22, 20, 22, 22)

        actions = QHBoxLayout()
        title = QLabel("Consultas agendadas")
        title.setObjectName("cardTitle")
        actions.addWidget(title)
        actions.addStretch()
        refresh = QPushButton("Actualizar")
        refresh.setObjectName("secondaryButton")
        refresh.clicked.connect(self.load_appointments)
        actions.addWidget(refresh)
        lay.addLayout(actions)

        self.appointments_table = self._table(
            ["ID", "Paciente", "Médico", "Data e hora", "Especialidade"]
        )
        lay.addWidget(self.appointments_table)
        layout.addWidget(card, 1)
        return page

    # ------------------------------------------------------------------
    # Small UI helpers
    # ------------------------------------------------------------------
    def _section_label(self, icon, text):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 3, 0, 3)
        l.setSpacing(8)
        i = QLabel(icon)
        i.setObjectName("sectionIcon")
        t = QLabel(text)
        t.setObjectName("formSection")
        l.addWidget(i)
        l.addWidget(t)
        l.addStretch()
        return w

    def _field(self, placeholder):
        e = QLineEdit()
        e.setPlaceholderText(placeholder)
        e.setMinimumHeight(42)
        return e

    def _labeled(self, label, widget):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(5)
        t = QLabel(label)
        t.setObjectName("fieldLabel")
        l.addWidget(t)
        l.addWidget(widget)
        return w

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

    def show_page(self, index):
        # Home is 0; nav indices 1..4 map to the stacked pages.
        self.content_stack.setCurrentIndex(index)
        for i, button in self.nav_buttons:
            button.setProperty("active", i == index)
            button.style().unpolish(button)
            button.style().polish(button)

    # ------------------------------------------------------------------
    # Existing CORBA actions
    # ------------------------------------------------------------------
    def register_patient(self):
        full_name = self.full_name_input.text().strip()
        birth_date = self.birth_date_input.text().strip()
        gender_index = self.gender_input.currentIndex()
        phone = self.phone_input.text().strip()

        if not full_name:
            self.show_error("Introduza o nome completo do paciente.")
            return
        if not birth_date:
            self.show_error("Introduza a data de nascimento.")
            return
        if gender_index == 0:
            self.show_error("Seleccione o género do paciente.")
            return
        if not phone:
            self.show_error("Introduza o contacto telefónico.")
            return

        try:
            patient = self.app.register_patient(
                full_name, birth_date,
                self.gender_input.currentText(), phone
            )
            QMessageBox.information(
                self, "Sucesso",
                f"Paciente registado com sucesso.\n\nID atribuído: {patient.id}"
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
        appointment_date = self.appointment_date_input.dateTime().toString("yyyy-MM-dd HH:mm")

        if not patient_id_text:
            self.show_error("Introduza o ID do paciente.")
            return
        if not patient_id_text.isdigit():
            self.show_error("O ID do paciente deve ser numérico.")
            return
        if not doctor or doctor == "Seleccione o médico":
            self.show_error("Seleccione o médico.")
            return
        if not specialty:
            self.show_error("Introduza a especialidade.")
            return

        try:
            appointment = self.app.schedule_appointment(
                int(patient_id_text), doctor, appointment_date, specialty
            )
            QMessageBox.information(
                self, "Sucesso",
                f"Consulta agendada com sucesso.\n\nID da consulta: {appointment.id}"
            )
            self.clear_appointment_form()
            self.load_appointments()
        except Exception as error:
            self.show_error(f"Não foi possível agendar a consulta:\n{error}")

    def load_appointments(self):
        try:
            appointments = self.app.list_appointments()
            if hasattr(self, "appointments_table"):
                self.appointments_table.setRowCount(len(appointments))
                for row, appointment in enumerate(appointments):
                    values = [
                        appointment.id, appointment.patientId,
                        appointment.doctor, appointment.appointmentDate,
                        appointment.specialty
                    ]
                    for column, value in enumerate(values):
                        self.appointments_table.setItem(row, column, QTableWidgetItem(str(value)))
                self.appointments_table.resizeColumnsToContents()
            if hasattr(self, "home_appointment_stat"):
                self.home_appointment_stat.findChildren(QLabel)[0].setText(str(len(appointments)))
        except Exception as error:
            self.show_error(f"Não foi possível carregar as consultas:\n{error}")

    def add_selected_patient_to_queue(self):
        selected = self.patients_table.selectionModel().selectedRows()
        if not selected:
            self.show_error("Seleccione um paciente antes de o adicionar à fila.")
            return
        item = self.patients_table.item(selected[0].row(), 0)
        if item is None:
            self.show_error("Não foi possível obter o ID do paciente.")
            return
        patient_id = int(item.text())
        try:
            self.app.add_patient_to_queue(patient_id)
            QMessageBox.information(self, "Sucesso", f"O paciente #{patient_id} foi adicionado à fila.")
        except Exception as error:
            self.show_error(f"Não foi possível adicionar o paciente à fila:\n{error}")

    def load_patients(self):
        try:
            patients = self.app.list_patients()
            if hasattr(self, "patients_table"):
                self.patients_table.setRowCount(len(patients))
                for row, patient in enumerate(patients):
                    values = [patient.id, patient.fullName, patient.birthDate, patient.gender, patient.phone]
                    for column, value in enumerate(values):
                        self.patients_table.setItem(row, column, QTableWidgetItem(str(value)))
                self.patients_table.resizeColumnsToContents()
            if hasattr(self, "home_patient_stat"):
                self.home_patient_stat.findChildren(QLabel)[0].setText(str(len(patients)))
        except Exception as error:
            self.show_error(f"Não foi possível carregar os pacientes:\n{error}")

    def clear_appointment_form(self):
        self.appointment_patient_id_input.clear()
        self.appointment_doctor_input.setCurrentIndex(0)
        self.appointment_specialty_input.setCurrentIndex(0)
        self.appointment_date_input.setDateTime(QDateTime.currentDateTime())

    def clear_form(self):
        self.full_name_input.clear()
        self.birth_date_input.clear()
        self.gender_input.setCurrentIndex(0)
        self.phone_input.clear()

    def show_error(self, message):
        QMessageBox.critical(self, "Erro", message)
