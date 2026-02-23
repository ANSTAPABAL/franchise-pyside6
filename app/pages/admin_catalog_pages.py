from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QHeaderView, QHBoxLayout, QInputDialog, QLabel, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from services.admin_service import (
    add_company,
    add_modem,
    add_news,
    add_user,
    delete_company,
    delete_modem,
    delete_news,
    delete_user,
    list_companies,
    list_modems,
    list_news,
    list_users,
    update_user,
)


class CompaniesPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        title = QLabel('Компании')
        title.setObjectName('panelTitle')
        root.addWidget(title)

        controls = QHBoxLayout()
        add_btn = QPushButton('+ Добавить компанию')
        del_btn = QPushButton('Удалить выбранную')
        del_btn.setProperty('variant', 'ghost')
        add_btn.clicked.connect(self._add)
        del_btn.clicked.connect(self._delete)
        controls.addWidget(add_btn); controls.addWidget(del_btn); controls.addStretch(1)
        root.addLayout(controls)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['id', 'name', 'created_at'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table)
        self.refresh()

    def refresh(self):
        rows = list_companies()
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, key in enumerate(['id', 'name', 'created_at']):
                self.table.setItem(r, c, QTableWidgetItem(str(row[key])))

    def _add(self):
        text, ok = QInputDialog.getText(self, 'Новая компания', 'Название:')
        if ok and text.strip():
            add_company(text.strip())
            self.refresh()

    def _delete(self):
        row = self.table.currentRow()
        if row < 0:
            return
        rec_id = self.table.item(row, 0).text()
        if QMessageBox.question(self, 'Подтверждение', 'Удалить компанию?') == QMessageBox.Yes:
            delete_company(rec_id)
            self.refresh()


# admin — доступ в Администрирование, всё остальное; operator — без админки, с экспортом Excel; viewer — только просмотр, без кнопок экспорта
ROLES = ('admin', 'operator', 'viewer')


class UsersPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        title = QLabel('Пользователи')
        title.setObjectName('panelTitle')
        root.addWidget(title)

        controls = QHBoxLayout()
        add_btn = QPushButton('+ Добавить пользователя')
        del_btn = QPushButton('Удалить выбранного')
        del_btn.setProperty('variant', 'ghost')
        add_btn.clicked.connect(self._add)
        del_btn.clicked.connect(self._delete)
        controls.addWidget(add_btn); controls.addWidget(del_btn); controls.addStretch(1)
        root.addLayout(controls)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(['id', 'ФИО', 'email', 'phone', 'role', 'active', 'Пароль'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemChanged.connect(self._on_item_changed)
        self._rows_cache: list[dict] = []
        self._skip_item_changed = False
        root.addWidget(self.table)
        self.refresh()

    def refresh(self):
        self._skip_item_changed = True
        try:
            self._rows_cache = list_users()
            self.table.setRowCount(len(self._rows_cache))
            cols = ['id', 'full_name', 'email', 'phone', 'role', 'is_active', 'password_plain']
            for r, row in enumerate(self._rows_cache):
                for c, key in enumerate(cols):
                    if c == 4:  # role — выпадающий список
                        combo = QComboBox()
                        combo.addItems(ROLES)
                        idx = combo.findText(str(row[key]))
                        combo.setCurrentIndex(max(0, idx))
                        combo.currentTextChanged.connect(lambda val, rr=r: self._on_role_changed(rr, val))
                        self.table.setCellWidget(r, c, combo)
                    else:
                        self.table.setItem(r, c, QTableWidgetItem(str(row.get(key, ''))))
        finally:
            self._skip_item_changed = False

    def _on_role_changed(self, row: int, role: str):
        if self._skip_item_changed or row >= len(self._rows_cache):
            return
        rec = self._rows_cache[row]
        try:
            update_user(
                rec['id'],
                rec['full_name'],
                rec['email'],
                rec.get('phone') or '',
                role,
                rec.get('is_active', True),
            )
            self._rows_cache[row] = {**rec, 'role': role}
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', str(exc))

    def _on_item_changed(self, item: QTableWidgetItem):
        if self._skip_item_changed or item.column() == 4 or item.column() == 6:
            return
        row = item.row()
        if row >= len(self._rows_cache):
            return
        rec = dict(self._rows_cache[row])
        cols = ['id', 'full_name', 'email', 'phone', 'role', 'is_active', 'password_plain']
        key = cols[item.column()]
        new_val = item.text()
        if key == 'is_active':
            rec['is_active'] = new_val.strip().lower() in ('1', 'true', 'да', 'yes')
        else:
            rec[key] = new_val
        role_w = self.table.cellWidget(row, 4)
        rec['role'] = role_w.currentText() if role_w else rec.get('role', 'operator')
        try:
            update_user(
                rec['id'],
                rec['full_name'],
                rec['email'],
                rec.get('phone') or '',
                rec['role'],
                rec.get('is_active', True),
            )
            self._rows_cache[row] = rec
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', str(exc))

    def _add(self):
        full_name, ok = QInputDialog.getText(self, 'Пользователь', 'ФИО:')
        if not (ok and full_name.strip()):
            return
        email, ok = QInputDialog.getText(self, 'Пользователь', 'Email:')
        if not (ok and email.strip()):
            return
        add_user(full_name.strip(), email.strip(), '', 'operator')
        self.refresh()

    def _delete(self):
        row = self.table.currentRow()
        if row < 0:
            return
        rec_id = self.table.item(row, 0).text()
        if QMessageBox.question(self, 'Подтверждение', 'Удалить пользователя?') == QMessageBox.Yes:
            delete_user(rec_id)
            self.refresh()


class ModemsPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        title = QLabel('Модемы')
        title.setObjectName('panelTitle')
        root.addWidget(title)

        controls = QHBoxLayout()
        add_btn = QPushButton('+ Добавить модем')
        del_btn = QPushButton('Удалить выбранный')
        del_btn.setProperty('variant', 'ghost')
        add_btn.clicked.connect(self._add)
        del_btn.clicked.connect(self._delete)
        controls.addWidget(add_btn); controls.addWidget(del_btn); controls.addStretch(1)
        root.addLayout(controls)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['id', 'modem_uid', 'provider', 'connection_type', 'created_at'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table)
        self.refresh()

    def refresh(self):
        rows = list_modems()
        cols = ['id', 'modem_uid', 'provider', 'connection_type', 'created_at']
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, key in enumerate(cols):
                self.table.setItem(r, c, QTableWidgetItem(str(row[key])))

    def _add(self):
        uid, ok = QInputDialog.getText(self, 'Модем', 'UID:')
        if not (ok and uid.strip()):
            return
        add_modem(uid.strip(), 'Provider', 'gsm')
        self.refresh()

    def _delete(self):
        row = self.table.currentRow()
        if row < 0:
            return
        rec_id = self.table.item(row, 0).text()
        if QMessageBox.question(self, 'Подтверждение', 'Удалить модем?') == QMessageBox.Yes:
            delete_modem(rec_id)
            self.refresh()


class ExtraPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        title = QLabel('Дополнительные')
        title.setObjectName('panelTitle')
        root.addWidget(title)

        controls = QHBoxLayout()
        add_btn = QPushButton('+ Добавить новость')
        del_btn = QPushButton('Удалить выбранную')
        del_btn.setProperty('variant', 'ghost')
        add_btn.clicked.connect(self._add)
        del_btn.clicked.connect(self._delete)
        controls.addWidget(add_btn); controls.addWidget(del_btn); controls.addStretch(1)
        root.addLayout(controls)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['id', 'title', 'body', 'created_at'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table)
        self.refresh()

    def refresh(self):
        rows = list_news()
        self.table.setRowCount(len(rows))
        cols = ['id', 'title', 'body', 'created_at']
        for r, row in enumerate(rows):
            for c, key in enumerate(cols):
                self.table.setItem(r, c, QTableWidgetItem(str(row[key])))

    def _add(self):
        title, ok = QInputDialog.getText(self, 'Новость', 'Заголовок:')
        if not (ok and title.strip()):
            return
        body, ok = QInputDialog.getMultiLineText(self, 'Новость', 'Текст:')
        if not ok:
            return
        add_news(title.strip(), body.strip())
        self.refresh()

    def _delete(self):
        row = self.table.currentRow()
        if row < 0:
            return
        rec_id = self.table.item(row, 0).text()
        if QMessageBox.question(self, 'Подтверждение', 'Удалить новость?') == QMessageBox.Yes:
            delete_news(rec_id)
            self.refresh()
