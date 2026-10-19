import csv

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QDialogButtonBox, QFileDialog, QFormLayout,
    QHBoxLayout, QInputDialog, QLabel, QLineEdit, QMessageBox, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QStackedWidget, QFrame,
)

from .icons import pixmap, qicon, illustration
from .waiting_room import WaitingRoomWindow
from .reception_dashboard import Sidebar, NavItem, SIDEBAR_W


class AdminDashboard(QWidget):
    def __init__(self, app, logout_callback=None):
        super().__init__()
        self.app = app
        self.logout_callback = logout_callback
        self.current_user = None
        self._users = []
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
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
        for icon, label, index in (("users", "Utilizadores", 0), ("stethoscope", "Medicos", 1), ("clipboard", "Auditoria", 2), ("settings", "Configuracoes", 3), ("bar-chart", "Estatisticas", 4)):
            item = NavItem(icon, label)
            item.clicked.connect(lambda _=False, i=index: self.show_page(i))
            side.addWidget(item)
            self.nav_buttons.append((index, item))
        side.addStretch(1)
        footer = QLabel("Gestao segura do MediSync")
        footer.setObjectName("sidebarFooter")
        side.addWidget(footer)
        root.addWidget(sidebar)
        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        
        header = QFrame()
        header.setObjectName("topbar")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(28, 8, 28, 8)
        title = QLabel("Administracao MediSync")
        title.setObjectName("pageTitle")
        self.user_label = QLabel()
        
        self.user_label.setObjectName("userName")
        profile = QPushButton("Meu perfil / palavra-passe")
        profile.setObjectName("secondaryButton")
        profile.clicked.connect(self.change_password)
        logout = QPushButton("Terminar sess?o")
        logout.setObjectName("secondaryButton")
        logout.clicked.connect(self.request_logout)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.user_label)
        header_layout.addWidget(profile)
        header_layout.addWidget(logout)

        
        content.addWidget(header)
        self.pages = QStackedWidget()
        for page in (self._users_page(), self._doctors_page(), self._audit_page(), self._settings_page(), self._reports_page()):
            self.pages.addWidget(page)
        content.addWidget(self.pages, 1)
        root.addLayout(content, 1)

    def _sidebar_divider(self):
        line = QFrame()
        line.setObjectName("sidebarDivider")
        line.setFixedHeight(1)
        return line

    def _users_page(self):
        page = QWidget(); layout = QVBoxLayout(page)
        actions = QHBoxLayout()
        for label, callback in (("Novo utilizador", self.create_user), ("Activar / desactivar", self.toggle_user), ("Repor palavra-passe", self.reset_password), ("Actualizar", self.load_users)):
            button = QPushButton(label); button.clicked.connect(callback); actions.addWidget(button)
        actions.addStretch(); layout.addLayout(actions)
        self.users_table = QTableWidget(0, 5)
        self.users_table.setHorizontalHeaderLabels(["ID", "Utilizador", "Nome", "Perfil", "Estado"])
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.users_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.users_table)
        return page

    def _reports_page(self):
        page = QWidget(); layout = QVBoxLayout(page)
        controls = QHBoxLayout()
        self.report_date = QDateEdit(QDate.currentDate()); self.report_date.setCalendarPopup(True); self.report_date.setDisplayFormat("yyyy-MM-dd")
        self.from_date = QDateEdit(QDate.currentDate().addDays(-30)); self.from_date.setCalendarPopup(True); self.from_date.setDisplayFormat("yyyy-MM-dd")
        self.to_date = QDateEdit(QDate.currentDate()); self.to_date.setCalendarPopup(True); self.to_date.setDisplayFormat("yyyy-MM-dd")
        refresh = QPushButton("Actualizar relatórios"); refresh.clicked.connect(self.load_reports)
        export = QPushButton("Exportar CSV"); export.clicked.connect(self.export_csv)
        controls.addWidget(QLabel("Dia")); controls.addWidget(self.report_date)
        controls.addSpacing(14); controls.addWidget(QLabel("Período")); controls.addWidget(self.from_date); controls.addWidget(self.to_date)
        controls.addWidget(refresh); controls.addWidget(export); controls.addStretch()
        layout.addLayout(controls)
        self.summary_label = QLabel("Seleccione um período para carregar indicadores.")
        self.summary_label.setWordWrap(True); self.summary_label.setStyleSheet("font-size:15px;font-weight:700;padding:12px")
        layout.addWidget(self.summary_label)
        self.times_table = QTableWidget(0, 4)
        self.times_table.setHorizontalHeaderLabels(["Médico", "Espera média (min)", "Atendimento médio (min)", "Concluídas"])
        self.times_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.times_table)
        self.specialties_table = QTableWidget(0, 4)
        self.specialties_table.setHorizontalHeaderLabels(["Especialidade", "Consultas", "Faltas", "Cancelamentos"])
        self.specialties_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.specialties_table)
        return page

    def _doctors_page(self):
        page = QWidget(); layout = QVBoxLayout(page)
        doctor_actions = QHBoxLayout()
        for label, callback in (("Novo médico", self.create_doctor), ("Editar seleccionado", self.edit_doctor), ("Activar / desactivar", self.toggle_doctor), ("Actualizar", self.load_doctors)):
            button = QPushButton(label); button.clicked.connect(callback); doctor_actions.addWidget(button)
        doctor_actions.addStretch(); layout.addLayout(doctor_actions)
        self.doctors_table = QTableWidget(0, 7); self.doctors_table.setHorizontalHeaderLabels(["ID", "Médico", "Especialidade", "Activo", "Consultório", "Dias", "Horário"])
        self.doctors_table.setSelectionBehavior(QTableWidget.SelectRows); self.doctors_table.setEditTriggers(QTableWidget.NoEditTriggers); self.doctors_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.doctors_table)
        room_row = QHBoxLayout(); self.room_input = QLineEdit(); self.room_input.setPlaceholderText("Consultório / sala")
        room_save = QPushButton("Guardar consultório"); room_save.clicked.connect(self.save_doctor_room)
        room_row.addWidget(self.room_input); room_row.addWidget(room_save); layout.addLayout(room_row)
        spec_actions = QHBoxLayout()
        add_spec = QPushButton("Nova especialidade"); add_spec.clicked.connect(self.create_specialty)
        edit_spec = QPushButton("Editar especialidade"); edit_spec.clicked.connect(self.edit_specialty)
        toggle_spec = QPushButton("Activar / desactivar especialidade"); toggle_spec.clicked.connect(self.toggle_specialty)
        spec_actions.addWidget(add_spec); spec_actions.addWidget(edit_spec); spec_actions.addWidget(toggle_spec); spec_actions.addStretch(); layout.addLayout(spec_actions)
        self.specialties_table = QTableWidget(0, 3); self.specialties_table.setHorizontalHeaderLabels(["ID", "Especialidade", "Activa"])
        self.specialties_table.setSelectionBehavior(QTableWidget.SelectRows); self.specialties_table.setEditTriggers(QTableWidget.NoEditTriggers); self.specialties_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.specialties_table)
        waiting_room = QPushButton("Abrir painel da sala de espera")
        waiting_room.clicked.connect(self.open_waiting_room)
        layout.addWidget(waiting_room)
        return page

    def show_page(self, index):
        self.pages.setCurrentIndex(index)
        for page_index, item in self.nav_buttons:
            item.set_active(page_index == index)
        if index == 0: self.load_users()
        elif index == 1: self.load_doctors()
        elif index == 2: self.load_audit_logs()
        elif index == 3: self.load_settings()
        elif index == 4: self.load_reports()

    def _audit_page(self):
        page = QWidget(); layout = QVBoxLayout(page)
        controls = QHBoxLayout()
        self.audit_from = QDateEdit(QDate.currentDate().addDays(-30)); self.audit_from.setCalendarPopup(True); self.audit_from.setDisplayFormat("yyyy-MM-dd")
        self.audit_to = QDateEdit(QDate.currentDate()); self.audit_to.setCalendarPopup(True); self.audit_to.setDisplayFormat("yyyy-MM-dd")
        refresh = QPushButton("Actualizar auditoria"); refresh.setObjectName("secondaryButton"); refresh.clicked.connect(self.load_audit_logs)
        controls.addWidget(QLabel("De")); controls.addWidget(self.audit_from); controls.addWidget(QLabel("Ate")); controls.addWidget(self.audit_to); controls.addWidget(refresh); controls.addStretch()
        layout.addLayout(controls)
        self.audit_table = QTableWidget(0, 7); self.audit_table.setHorizontalHeaderLabels(["ID", "Data", "Utilizador", "Acao", "Entidade", "ID entidade", "Detalhes"])
        self.audit_table.setEditTriggers(QTableWidget.NoEditTriggers); self.audit_table.setSelectionBehavior(QTableWidget.SelectRows); self.audit_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.audit_table)
        return page

    def _settings_page(self):
        page = QWidget(); layout = QVBoxLayout(page)
        form = QHBoxLayout(); self.setting_key = QLineEdit(); self.setting_key.setPlaceholderText("Chave, ex.: appointment.duration_minutes")
        self.setting_value = QLineEdit(); self.setting_value.setPlaceholderText("Valor")
        save = QPushButton("Guardar configuracao"); save.setObjectName("successButton"); save.clicked.connect(self.save_setting)
        form.addWidget(self.setting_key); form.addWidget(self.setting_value); form.addWidget(save); layout.addLayout(form)
        self.settings_table = QTableWidget(0, 2); self.settings_table.setHorizontalHeaderLabels(["Chave", "Valor"])
        self.settings_table.setEditTriggers(QTableWidget.NoEditTriggers); self.settings_table.horizontalHeader().setStretchLastSection(True); layout.addWidget(self.settings_table)
        return page

    def load_audit_logs(self):
        try:
            items = self.app.audit_logs(self.audit_from.date().toString("yyyy-MM-dd"), self.audit_to.date().toString("yyyy-MM-dd"))
            self.audit_table.setRowCount(len(items))
            for row, item in enumerate(items):
                values = (item.id, item.createdAt, item.username, item.action, item.entityType, item.entityId, item.details)
                for col, value in enumerate(values): self.audit_table.setItem(row, col, QTableWidgetItem(str(value)))
        except Exception as error: QMessageBox.critical(self, "Auditoria", str(error))

    def load_settings(self):
        try:
            items = self.app.system_settings(); self.settings_table.setRowCount(len(items))
            for row, item in enumerate(items):
                self.settings_table.setItem(row, 0, QTableWidgetItem(item.key)); self.settings_table.setItem(row, 1, QTableWidgetItem(item.value))
        except Exception as error: QMessageBox.critical(self, "Configuracoes", str(error))

    def save_setting(self):
        try:
            self.app.set_system_setting(self.setting_key.text().strip(), self.setting_value.text().strip())
            self.setting_key.clear(); self.setting_value.clear(); self.load_settings()
        except Exception as error: QMessageBox.critical(self, "Configuracoes", str(error))

    def set_current_user(self, user):
        self.current_user = user
        self.user_label.setText(getattr(user, "fullName", "Administrador"))
        self.show_page(0)

    def open_waiting_room(self):
        self.waiting_room_window = WaitingRoomWindow(self.app)
        self.waiting_room_window.showMaximized()

    def request_logout(self):
        if self.logout_callback: self.logout_callback()

    def change_password(self):
        current, ok = QInputDialog.getText(self, "Alterar palavra-passe", "Palavra-passe actual:", QLineEdit.Password)
        if not ok: return
        new, ok = QInputDialog.getText(self, "Alterar palavra-passe", "Nova palavra-passe (mínimo 10 caracteres):", QLineEdit.Password)
        if not ok: return
        try:
            self.app.change_own_password(current, new)
            QMessageBox.information(self, "Palavra-passe alterada", "A palavra-passe foi actualizada.")
        except Exception as error: QMessageBox.critical(self, "Erro", str(error))

    def load_users(self):
        try:
            self._users = self.app.list_users()
            self.users_table.setRowCount(len(self._users))
            for row, user in enumerate(self._users):
                for col, value in enumerate((user.id, user.username, user.fullName, user.role, "Activo" if user.active else "Inactivo")):
                    self.users_table.setItem(row, col, QTableWidgetItem(str(value)))
        except Exception as error: QMessageBox.critical(self, "Erro ao carregar utilizadores", str(error))

    def _selected_user(self):
        rows = self.users_table.selectionModel().selectedRows()
        if not rows: QMessageBox.warning(self, "Utilizadores", "Seleccione um utilizador."); return None
        return self._users[rows[0].row()]

    def create_user(self):
        dialog = QDialog(self); dialog.setWindowTitle("Novo utilizador")
        form = QFormLayout(dialog)
        username = QLineEdit(); full_name = QLineEdit(); role = QComboBox(); role.addItems(["RECEPTION", "DOCTOR", "ADMIN"])
        password = QLineEdit(); password.setEchoMode(QLineEdit.Password)
        form.addRow("Utilizador", username); form.addRow("Nome completo", full_name); form.addRow("Perfil", role); form.addRow("Palavra-passe inicial", password)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel); buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject); form.addRow(buttons)
        if dialog.exec() != QDialog.Accepted: return
        try:
            self.app.create_user(username.text(), full_name.text(), role.currentText(), password.text()); self.load_users()
        except Exception as error: QMessageBox.critical(self, "Erro ao criar utilizador", str(error))

    def toggle_user(self):
        user = self._selected_user()
        if user is None: return
        try: self.app.set_user_active(int(user.id), not bool(user.active)); self.load_users()
        except Exception as error: QMessageBox.critical(self, "Erro ao alterar utilizador", str(error))

    def reset_password(self):
        user = self._selected_user()
        if user is None: return
        password, ok = QInputDialog.getText(self, "Repor palavra-passe", f"Nova palavra-passe para {user.username}:", QLineEdit.Password)
        if not ok: return
        try: self.app.reset_user_password(int(user.id), password); QMessageBox.information(self, "Palavra-passe reposta", "A nova palavra-passe foi guardada.")
        except Exception as error: QMessageBox.critical(self, "Erro", str(error))

    def load_doctors(self):
        try:
            self._doctors = self.app.list_all_doctors(); self._specialties = self.app.list_all_specialties()
            self.doctors_table.setRowCount(len(self._doctors))
            for row, item in enumerate(self._doctors):
                vals = (item.id, item.fullName, item.specialty, "Sim" if item.active else "Não", getattr(item, "clinicRoom", ""), getattr(item, "workingDays", ""), f"{getattr(item, 'startTime', '')}-{getattr(item, 'endTime', '')}".strip("-"))
                for col, value in enumerate(vals): self.doctors_table.setItem(row, col, QTableWidgetItem(str(value)))
            self.specialties_table.setRowCount(len(self._specialties))
            for row, item in enumerate(self._specialties):
                for col, value in enumerate((item.id, item.name, "Sim" if item.active else "Não")):
                    self.specialties_table.setItem(row, col, QTableWidgetItem(str(value)))
        except Exception as error: QMessageBox.critical(self, "Erro ao carregar médicos", str(error))

    def _selected_doctor(self):
        rows = self.doctors_table.selectionModel().selectedRows()
        if not rows: QMessageBox.warning(self, "Médicos", "Seleccione um médico."); return None
        return self._doctors[rows[0].row()]

    def _doctor_dialog(self, doctor=None):
        dialog = QDialog(self); dialog.setWindowTitle("Editar médico" if doctor else "Novo médico")
        form = QFormLayout(dialog); name = QLineEdit(getattr(doctor, "fullName", "")); room = QLineEdit(getattr(doctor, "clinicRoom", "")); specialty = QComboBox()
        days = QLineEdit(getattr(doctor, "workingDays", "")); days.setPlaceholderText("MON,TUE,WED,THU,FRI,SAT,SUN")
        start = QLineEdit(getattr(doctor, "startTime", "")); start.setPlaceholderText("08:00")
        end = QLineEdit(getattr(doctor, "endTime", "")); end.setPlaceholderText("17:00")
        active = [item for item in self._specialties if item.active]
        for item in active: specialty.addItem(item.name, item.id)
        if doctor:
            index = specialty.findText(doctor.specialty)
            if index >= 0: specialty.setCurrentIndex(index)
        form.addRow("Nome", name); form.addRow("Especialidade", specialty); form.addRow("Consultório", room)
        form.addRow("Dias (opcional)", days); form.addRow("Início (HH:mm)", start); form.addRow("Fim (HH:mm)", end)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel); buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject); form.addRow(buttons)
        if dialog.exec() != QDialog.Accepted: return
        try:
            if doctor:
                self.app.update_doctor(int(doctor.id), name.text(), int(specialty.currentData()))
                self.app.set_doctor_room(int(doctor.id), room.text())
                self.app.set_doctor_schedule(int(doctor.id), days.text(), start.text(), end.text())
            else:
                new_doctor = self.app.create_doctor(name.text(), int(specialty.currentData()))
                if room.text().strip(): self.app.set_doctor_room(int(new_doctor.id), room.text())
                if days.text().strip(): self.app.set_doctor_schedule(int(new_doctor.id), days.text(), start.text(), end.text())
            self.load_doctors()
        except Exception as error: QMessageBox.critical(self, "Erro ao guardar médico", str(error))

    def create_doctor(self): self._doctor_dialog()
    def edit_doctor(self):
        doctor = self._selected_doctor()
        if doctor: self._doctor_dialog(doctor)
    def toggle_doctor(self):
        doctor = self._selected_doctor()
        if doctor:
            try: self.app.set_doctor_active(int(doctor.id), not bool(doctor.active)); self.load_doctors()
            except Exception as error: QMessageBox.critical(self, "Erro", str(error))
    def save_doctor_room(self):
        doctor = self._selected_doctor()
        if doctor:
            try: self.app.set_doctor_room(int(doctor.id), self.room_input.text()); self.load_doctors()
            except Exception as error: QMessageBox.critical(self, "Erro", str(error))
    def create_specialty(self):
        name, ok = QInputDialog.getText(self, "Nova especialidade", "Nome:")
        if ok:
            try: self.app.create_specialty(name); self.load_doctors()
            except Exception as error: QMessageBox.critical(self, "Erro", str(error))
    def edit_specialty(self):
        rows = self.specialties_table.selectionModel().selectedRows()
        if not rows: QMessageBox.warning(self, "Especialidades", "Seleccione uma especialidade."); return
        item = self._specialties[rows[0].row()]
        name, ok = QInputDialog.getText(self, "Editar especialidade", "Nome:", text=item.name)
        if ok:
            try: self.app.update_specialty(int(item.id), name); self.load_doctors()
            except Exception as error: QMessageBox.critical(self, "Erro", str(error))
    def toggle_specialty(self):
        rows = self.specialties_table.selectionModel().selectedRows()
        if not rows: QMessageBox.warning(self, "Especialidades", "Seleccione uma especialidade."); return
        item = self._specialties[rows[0].row()]
        try: self.app.set_specialty_active(int(item.id), not bool(item.active)); self.load_doctors()
        except Exception as error: QMessageBox.critical(self, "Erro", str(error))

    def load_reports(self):
        try:
            day = self.report_date.date().toString("yyyy-MM-dd")
            summary = self.app.daily_summary(day)
            self.summary_label.setText(f"{day}  ·  Registadas: {summary.appointmentsRegistered}  ·  Em espera/atendimento: {summary.waiting}  ·  Atendidas: {summary.attended}  ·  Faltas: {summary.absences}  ·  Canceladas: {summary.cancellations}")
            start = self.from_date.date().toString("yyyy-MM-dd"); end = self.to_date.date().toString("yyyy-MM-dd")
            times = self.app.average_times(start, end); volumes = self.app.specialty_volumes(start, end)
            self.times_table.setRowCount(len(times))
            for row, item in enumerate(times):
                for col, value in enumerate((item.doctor, item.averageWaitMinutes, item.averageServiceMinutes, item.completedCount)):
                    self.times_table.setItem(row, col, QTableWidgetItem(str(value)))
            self.specialties_table.setRowCount(len(volumes))
            for row, item in enumerate(volumes):
                for col, value in enumerate((item.specialty, item.appointments, item.absences, item.cancellations)):
                    self.specialties_table.setItem(row, col, QTableWidgetItem(str(value)))
        except Exception as error: QMessageBox.critical(self, "Erro ao gerar relatórios", str(error))

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar relatório", "medisync_relatorio.csv", "CSV (*.csv)")
        if not path: return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as stream:
                writer = csv.writer(stream, delimiter=";")
                writer.writerow(["Resumo diário", self.report_date.date().toString("yyyy-MM-dd"), self.summary_label.text()])
                writer.writerow([])
                writer.writerow(["Médico", "Espera média (min)", "Atendimento médio (min)", "Concluídas"])
                for row in range(self.times_table.rowCount()): writer.writerow([self.times_table.item(row, col).text() if self.times_table.item(row, col) else "" for col in range(4)])
                writer.writerow([]); writer.writerow(["Especialidade", "Consultas", "Faltas", "Cancelamentos"])
                for row in range(self.specialties_table.rowCount()): writer.writerow([self.specialties_table.item(row, col).text() if self.specialties_table.item(row, col) else "" for col in range(4)])
            QMessageBox.information(self, "Exportação concluída", f"Relatório guardado em {path}")
        except Exception as error: QMessageBox.critical(self, "Erro ao exportar CSV", str(error))
