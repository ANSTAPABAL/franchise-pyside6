"""окно авторизации пользователя.

первый экран, который видит пользователь. модальный диалог — пока не закроешь,
главное окно не откроется.
"""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from app.session import session
from services.auth_service import authenticate


class LoginDialog(QDialog):
    """модальное окно входа с полями email и пароль.

    фишка: QDialog.exec() блокирует выполнение до закрытия окна и возвращает
    1 (Accepted) или 0 (Rejected). в app/main.py проверяем:
    if not login.exec(): return 0  — если закрыли без входа, приложение не запускается.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Авторизация')
        self.setModal(True)      # блокирует остальные окна пока открыт
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        form = QFormLayout()     # QFormLayout — удобная разметка «метка: поле»

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText('admin@franchise.local')

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)  # скрывает символы звёздочками
        self.password_edit.setPlaceholderText('Введите пароль')

        form.addRow('Email', self.email_edit)
        form.addRow('Пароль', self.password_edit)
        layout.addLayout(form)

        login_btn = QPushButton('Войти')
        login_btn.clicked.connect(self._login)  # нажатие → вызов _login
        layout.addWidget(login_btn)

    def _login(self):
        """проверяет введённые данные, выполняет вход и заполняет объект session.

        как работает:
        - strip() убирает пробелы в начале/конце — частая ошибка при вводе;
        - вызываем authenticate() из сервиса — он лезет в бд;
        - если вернулся None — логин/пароль неверный;
        - если вернулся dict — заполняем session и закрываем диалог через accept().
        """
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()
        if not email or not password:
            QMessageBox.warning(self, 'Ошибка', 'Введите email и пароль.')
            return

        try:
            user = authenticate(email, password)
        except Exception as exc:
            # ошибка соединения с бд или другая непредвиденная ошибка
            QMessageBox.critical(self, 'Ошибка БД', str(exc))
            return

        if not user:
            QMessageBox.warning(self, 'Доступ запрещен', 'Неверный email или пароль.')
            return

        # заполняем глобальный объект сессии данными вошедшего пользователя
        session.user_id = user['id']
        session.full_name = user['full_name']
        session.email = user['email']
        session.role = user['role']
        session.token = user['token']
        session.photo_base64 = user.get('photo_base64')
        self.accept()  # закрываем диалог с кодом Accepted (1)
