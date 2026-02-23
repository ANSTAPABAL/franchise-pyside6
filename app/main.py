from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from app.dialogs.login_dialog import LoginDialog
from app.main_window import MainWindow
from app.styles import APP_STYLESHEET
from core.logger import configure_logging


def run() -> int:
    configure_logging()

    # Needed on Windows so taskbar and title bar use app icon consistently.
    if sys.platform.startswith("win"):
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "PracticePyside6Rylov.DesktopApp"
            )
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    app.setFont(QFont('Segoe UI', 10))
    icon_path = Path(__file__).resolve().parent.parent / "assets" / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    login = LoginDialog()
    if not login.exec():
        return 0

    window = MainWindow()
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.show()
    return app.exec()
