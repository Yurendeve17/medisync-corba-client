from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QMessageBox,
    QPlainTextEdit, QTableWidget, QTableWidgetItem, QVBoxLayout,
)


class ConsultationDialog(QDialog):
    def __init__(self, app, appointment, patient_name: str, parent=None):
        super().__init__(parent)
        self.app = app
        self.appointment = appointment
        self.setWindowTitle(f"Registo clínico · {patient_name}")
        self.resize(900, 720)
        root = QVBoxLayout(self)
        intro = QLabel(f"Consulta #{appointment.id} · {appointment.appointmentDate} · {appointment.specialty}")
        intro.setObjectName("pageSubtitle")
        root.addWidget(intro)
        root.addWidget(QLabel("Histórico clínico anterior"))
        self.history = QTableWidget(0, 7)
        self.history.setHorizontalHeaderLabels(["Data", "Medico", "Diagnostico", "Observacoes", "Prescricao", "Sinais vitais", "Plano clinico"])
        self.history.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history.setSelectionBehavior(QTableWidget.SelectRows)
        self.history.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.history, 1)
        form = QFormLayout()
        self.diagnosis = QLineEdit()
        self.diagnosis.setMaxLength(500)
        self.observations = QPlainTextEdit()
        self.observations.setMaximumHeight(100)
        self.prescription = QPlainTextEdit()
        self.prescription.setMaximumHeight(90)
        self.vital_signs = QPlainTextEdit()
        self.vital_signs.setMaximumHeight(70)
        self.vital_signs.setPlaceholderText("Pressao arterial, temperatura, pulso, peso")
        self.care_plan = QPlainTextEdit()
        self.care_plan.setMaximumHeight(90)
        form.addRow("Diagnóstico", self.diagnosis)
        form.addRow("Observações", self.observations)
        form.addRow("Prescrição", self.prescription)
        form.addRow("Sinais vitais", self.vital_signs)
        form.addRow("Plano clinico / seguimento", self.care_plan)
        root.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close)
        buttons.button(QDialogButtonBox.Save).setObjectName("successButton")
        buttons.button(QDialogButtonBox.Save).setEnabled(getattr(appointment, "status", "") in {"EM_ATENDIMENTO", "CONCLUIDA"})
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)
        self._load_history()

    def _load_history(self):
        try:
            notes = self.app.doctor_patient_history(int(self.appointment.patientId))
            self.history.setRowCount(len(notes))
            for row, note in enumerate(notes):
                values = (note.appointmentDate, note.doctor, note.diagnosis, note.observations, note.prescription, note.vitalSigns, note.carePlan)
                for col, value in enumerate(values):
                    self.history.setItem(row, col, QTableWidgetItem(str(value or "")))
                if int(note.appointmentId) == int(self.appointment.id):
                    self.diagnosis.setText(str(note.diagnosis or ""))
                    self.observations.setPlainText(str(note.observations or ""))
                    self.prescription.setPlainText(str(note.prescription or ""))
                    self.vital_signs.setPlainText(str(note.vitalSigns or ""))
                    self.care_plan.setPlainText(str(note.carePlan or ""))
        except Exception as error:
            QMessageBox.critical(self, "Histórico clínico", str(error))

    def save(self):
        if not self.diagnosis.text().strip():
            QMessageBox.warning(self, "Registo clínico", "O diagnóstico é obrigatório.")
            return
        try:
            self.app.save_clinical_note_extended(
                int(self.appointment.id), self.diagnosis.text().strip(),
                self.observations.toPlainText().strip(), self.prescription.toPlainText().strip(),
                self.vital_signs.toPlainText().strip(), self.care_plan.toPlainText().strip(),
            )
            self.accept()
        except Exception as error:
            QMessageBox.critical(self, "Não foi possível guardar", str(error))
