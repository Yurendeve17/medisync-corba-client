from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
)

from gui.login_page import LoginPage
from gui.reception_dashboard import ReceptionDashboard
from gui.doctor_dashboard import DoctorDashboard


class MainWindow(QMainWindow):

    def __init__(self, app):
        super().__init__()

        self.setWindowTitle("MediSync")
        self.resize(1440, 900)
        self.setMinimumSize(1100, 700)

        self.app = app

        self.stack = QStackedWidget()

        self.login_page = LoginPage(app)

        self.reception_dashboard = ReceptionDashboard(
            app,
            self.stack,
        )

        self.doctor_dashboard = DoctorDashboard(
            app,
            self.stack,
        )

        self.stack.addWidget(
            self.login_page
        )

        self.stack.addWidget(
            self.reception_dashboard
        )

        self.stack.addWidget(
            self.doctor_dashboard
        )

        self.login_page.login_successful.connect(
            self.handle_login
        )

        self.setCentralWidget(self.stack)

    def handle_login(self, user):

        if user.role == "RECEPTION":
            self.stack.setCurrentWidget(
                self.reception_dashboard
            )

        elif user.role == "DOCTOR":
            self.stack.setCurrentWidget(
                self.doctor_dashboard
            )