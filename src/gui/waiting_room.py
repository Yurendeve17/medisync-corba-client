from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


class WaitingRoomWindow(QWidget):
    """Painel simples de chamadas recentes para um ecrã da sala de espera."""
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("MediSync · Chamadas")
        self.resize(1100, 720)
        self.setStyleSheet("background:#f5f8fb")
        layout = QVBoxLayout(self)
        title = QLabel("CHAMADAS PARA ATENDIMENTO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:34px;font-weight:900;color:#173653;padding:18px")
        layout.addWidget(title)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Paciente", "Médico", "Consultório"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(72)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet("font-size:24px;font-weight:700")
        layout.addWidget(self.table)
        self.timer = QTimer(self); self.timer.timeout.connect(self.refresh); self.timer.start(4000)
        self.refresh()

    def refresh(self):
        try:
            calls = sorted(self.app.list_notifications(), key=lambda item: int(item.id), reverse=True)[:12]
            self.table.setRowCount(len(calls))
            for row, item in enumerate(calls):
                name = getattr(item, "patientName", "") or f"Paciente #{item.patientId}"
                for col, value in enumerate((name, item.doctor, getattr(item, "clinicRoom", "") or "—")):
                    cell = QTableWidgetItem(str(value)); cell.setTextAlignment(Qt.AlignCenter); self.table.setItem(row, col, cell)
        except Exception:
            pass
