import sys
from PySide6.QtWidgets import QApplication

from application.medisync_app import MediSyncApp
from gui.main_window import MainWindow
from gui.theme import apply_theme


def main():
    app = QApplication(sys.argv)

    apply_theme(app, dark=False)

    medisync_app = MediSyncApp()

    try:
        window = MainWindow(medisync_app)
        window.showMaximized()

        sys.exit(app.exec())

    finally:
        medisync_app.close()


if __name__ == "__main__":
    main()