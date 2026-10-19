import sys
from PySide6.QtWidgets import QApplication, QMessageBox

from application.medisync_app import MediSyncApp
from gui.main_window import MainWindow
from gui.theme import apply_theme


def main():
    app = QApplication(sys.argv)

    apply_theme(app, dark=False)

    while True:
        try:
            medisync_app = MediSyncApp()
            break
        except Exception as error:
            retry = QMessageBox.critical(
                None,
                "Ligacao ao servidor MediSync",
                f"Nao foi possivel iniciar a ligacao CORBA.\n\n{error}\n\n"
                "Corrija a ligacao ao servidor e escolha Tentar novamente.",
                QMessageBox.Retry | QMessageBox.Cancel,
                QMessageBox.Retry,
            )
            if retry != QMessageBox.Retry:
                return

    try:
        window = MainWindow(medisync_app)
        window.showMaximized()

        sys.exit(app.exec())

    finally:
        medisync_app.close()


if __name__ == "__main__":
    main()
