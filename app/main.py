"""главная точка запуска gui-приложения.

что тут происходит по порядку:
1. настраивается логирование;
2. на windows регистрируется app user model id (иконка в taskbar);
3. создаётся QApplication — это обязательный объект Qt, должен быть ровно один;
4. применяются глобальные стили и шрифт;
5. показывается окно логина — пока не войдёшь, главное окно не открывается;
6. после успешного входа открывается MainWindow.
"""

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
    """запускает приложение и возвращает код завершения процесса.

    возвращаемое значение передаётся в sys.exit() — 0 означает нормальное завершение.
    """
    configure_logging()

    # на windows фиксируем app user model id, чтобы иконка в панели задач
    # и заголовок окна отображались корректно
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "PracticePyside6Rylov.DesktopApp"
            )
        except Exception:
            pass  # если не удалось — просто игнорируем, это не критично

    # QApplication должен быть ровно один на всё приложение
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)   # глобальная qss-тема
    app.setFont(QFont('Segoe UI', 10))  # единый шрифт для всех виджетов

    # ищем иконку приложения в папке assets/
    icon_path = Path(__file__).resolve().parent.parent / "assets" / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # показываем окно логина; если пользователь закрыл его — выходим
    login = LoginDialog()
    if not login.exec():
        return 0

    # логин прошёл — открываем главное окно
    window = MainWindow()
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.show()
    return app.exec()  # запускаем event loop qt; выходим когда закроют окно
