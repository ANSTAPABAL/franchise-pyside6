from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QCheckBox, QComboBox, QDateEdit, QDialog, QFormLayout, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QTextEdit, QVBoxLayout

from services.vending_service import upsert_machine


class MachineFormDialog(QDialog):
    def __init__(self, payload: dict | None = None):
        super().__init__()
        self.payload = payload or {}
        self.result_id: str | None = None
        self.setWindowTitle('Создание торгового автомата')
        self.resize(980, 860)

        root = QVBoxLayout(self)
        title = QLabel('Создание торгового автомата')
        title.setObjectName('panelTitle')
        root.addWidget(title)

        grid = QGridLayout()

        self.name = QLineEdit(self.payload.get('name', ''))
        self.manufacturer = QLineEdit(self.payload.get('manufacturer', 'Necta'))
        self.model = QLineEdit(self.payload.get('model', ''))
        self.machine_type = QComboBox()
        self.machine_type.addItems(['mixed', 'card', 'cash'])
        self.location = QLineEdit(self.payload.get('location', ''))
        self.serial = QLineEdit(self.payload.get('serial_number', ''))
        self.inventory = QLineEdit(self.payload.get('inventory_number', ''))
        self.timezone = QComboBox()
        self.timezone.addItems(['UTC+3', 'UTC+5', 'UTC+7'])
        self.country = QLineEdit(self.payload.get('production_country', 'Россия'))
        self.status = QComboBox()
        self.status.addItems(['working', 'broken', 'maintenance'])
        self.resource_hours = QLineEdit(str(self.payload.get('resource_hours', 10000)))
        self.interval = QLineEdit(str(self.payload.get('verification_interval_months', 12)))

        self.manufacture_date = QDateEdit(QDate.currentDate())
        self.commissioned_date = QDateEdit(QDate.currentDate())
        self.last_verification = QDateEdit(QDate.currentDate())
        self.next_service = QDateEdit(QDate.currentDate().addDays(10))
        self.inventory_date = QDateEdit(QDate.currentDate())
        for d in [self.manufacture_date, self.commissioned_date, self.last_verification, self.next_service, self.inventory_date]:
            d.setCalendarPopup(True)

        self.payment_cash = QCheckBox('Монетопр.')
        self.payment_cash.setChecked(True)
        self.payment_bill = QCheckBox('Купюропр.')
        self.payment_qr = QCheckBox('QR-платежи')

        self.notes = QTextEdit()
        self.notes.setPlaceholderText('Примечания')
        self.company_id = QLineEdit(self.payload.get('company_id', ''))

        fields = [
            ('Название ТА *', self.name, 0, 0),
            ('Производитель ТА *', self.manufacturer, 0, 1),
            ('Модель ТА *', self.model, 0, 2),
            ('Режим работы *', self.machine_type, 1, 0),
            ('Адрес *', self.location, 1, 1),
            ('Номер автомата *', self.serial, 1, 2),
            ('Инвентарный номер *', self.inventory, 2, 0),
            ('Часовой пояс *', self.timezone, 2, 1),
            ('Страна', self.country, 2, 2),
            ('Статус', self.status, 3, 0),
            ('Ресурс (ч)', self.resource_hours, 3, 1),
            ('Интервал поверки (мес)', self.interval, 3, 2),
            ('Дата изготовления', self.manufacture_date, 4, 0),
            ('Дата ввода', self.commissioned_date, 4, 1),
            ('Дата поверки', self.last_verification, 4, 2),
            ('Следующее обслуживание', self.next_service, 5, 0),
            ('Дата инвентаризации', self.inventory_date, 5, 1),
            ('Компания (UUID)', self.company_id, 5, 2),
        ]
        for label, widget, row, col in fields:
            block = QFormLayout()
            block.addRow(label, widget)
            holder = QVBoxLayout()
            holder.addLayout(block)
            wrap = QVBoxLayout()
            wrap.addLayout(block)
            cell = QLabel()
            dummy = QVBoxLayout()
            dummy.addLayout(block)
            container = QLabel()
            del holder, wrap, cell, dummy, container
            grid.addLayout(block, row, col)

        payments = QHBoxLayout()
        payments.addWidget(self.payment_cash)
        payments.addWidget(self.payment_bill)
        payments.addWidget(self.payment_qr)
        pay_form = QFormLayout()
        pay_form.addRow('Платежные системы *', payments)
        grid.addLayout(pay_form, 6, 0, 1, 3)

        notes_form = QFormLayout()
        notes_form.addRow('Примечания', self.notes)
        grid.addLayout(notes_form, 7, 0, 1, 3)

        root.addLayout(grid)

        buttons = QHBoxLayout()
        save_btn = QPushButton('Создать')
        cancel_btn = QPushButton('Отменить')
        cancel_btn.setProperty('variant', 'ghost')
        save_btn.clicked.connect(self._save)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        buttons.addStretch(1)
        root.addLayout(buttons)

    def _iso(self, value: QDate) -> str:
        return date(value.year(), value.month(), value.day()).isoformat()

    def _save(self):
        try:
            payload = {
                'id': self.payload.get('id'),
                'name': self.name.text().strip(),
                'location': self.location.text().strip(),
                'model': self.model.text().strip() or 'Unknown',
                'machine_type': self.machine_type.currentText(),
                'total_income': float(self.payload.get('total_income', 0) or 0),
                'serial_number': self.serial.text().strip(),
                'inventory_number': self.inventory.text().strip() or f"INV-{self.serial.text().strip()}",
                'manufacturer': self.manufacturer.text().strip() or 'Unknown',
                'manufacture_date': self._iso(self.manufacture_date.date()),
                'commissioned_date': self._iso(self.commissioned_date.date()),
                'last_verification_date': self._iso(self.last_verification.date()),
                'verification_interval_months': int(self.interval.text().strip() or '12'),
                'resource_hours': int(self.resource_hours.text().strip() or '10000'),
                'next_service_date': self._iso(self.next_service.date()),
                'service_duration_hours': 4,
                'status': self.status.currentText(),
                'production_country': self.country.text().strip() or 'Россия',
                'inventory_date': self._iso(self.inventory_date.date()),
                'last_verifier_user_id': None,
                'company_id': self.company_id.text().strip() or None,
            }
        except ValueError:
            QMessageBox.warning(self, 'Ошибка', 'Проверьте числовые поля (ресурс/интервал).')
            return

        if not payload['name'] or not payload['serial_number']:
            QMessageBox.warning(self, 'Ошибка', 'Название и номер автомата обязательны.')
            return

        try:
            self.result_id = upsert_machine(payload)
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', str(exc))
            return
        self.accept()
