import sys
from pathlib import Path


from PySide6.QtWidgets import QApplication

from application.medisync_app import MediSyncApp
from gui.main_window import MainWindow
from gui.theme import load_stylesheet


def main():
    app = QApplication(sys.argv)

    style_path = (
        Path(__file__).resolve().parent
        / "gui"
        / "style.qss"
    )

    app.setStyleSheet(load_stylesheet(style_path))

    medisync_app = MediSyncApp()

    try:
        window = MainWindow(medisync_app)
        window.showMaximized()

        sys.exit(app.exec())

    finally:
        medisync_app.close()


if __name__ == "__main__":
    main()