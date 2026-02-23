from __future__ import annotations

from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from app.session import session
from services.auth_service import authenticate


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Авторизация')
        self.setModal(True)
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText('admin@franchise.local')
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText('Введите пароль')

        form.addRow('Email', self.email_edit)
        form.addRow('Пароль', self.password_edit)
        layout.addLayout(form)

        login_btn = QPushButton('Войти')
        login_btn.clicked.connect(self._login)
        layout.addWidget(login_btn)

    def _login(self):
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()
        if not email or not password:
            QMessageBox.warning(self, 'Ошибка', 'Введите email и пароль.')
            return

        try:
            user = authenticate(email, password)
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка БД', str(exc))
            return

        if not user:
            QMessageBox.warning(self, 'Доступ запрещен', 'Неверный email или пароль.')
            return

        session.user_id = user['id']
        session.full_name = user['full_name']
        session.email = user['email']
        session.role = user['role']
        session.token = user['token']
        session.photo_base64 = user.get('photo_base64')
        self.accept()
