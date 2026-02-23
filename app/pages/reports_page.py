from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QHeaderView, QLabel, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from app.session import session
from services.reports_service import sales_report


def _excel_datetime(val):
    """Приводит datetime к виду без timezone для Excel."""
    if val is None:
        return None
    if hasattr(val, 'tzinfo') and getattr(val, 'tzinfo', None) is not None:
        return val.replace(tzinfo=None)
    return val


def _export_reports_xlsx(rows: list, path: Path) -> None:
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = 'Отчёты'
    headers = ['ID', 'Дата', 'Сумма', 'Кол-во', 'Товар', 'Автомат', 'Оплата']
    ws.append(headers)
    for r in rows:
        ws.append([
            r.get('id'),
            _excel_datetime(r.get('sold_at')),
            r.get('amount'), r.get('quantity'),
            r.get('product_name'), r.get('machine_name'), r.get('payment_method'),
        ])
    wb.save(path)


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self._last_rows: list = []
        root = QVBoxLayout(self)
        title = QLabel('Детальные отчеты')
        title.setObjectName('panelTitle')
        root.addWidget(title)

        self.exp_btn = QPushButton('Скачать Excel')
        self.exp_btn.clicked.connect(self._export_xlsx)
        self.exp_btn.setVisible(session.role != 'viewer')
        root.addWidget(self.exp_btn)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(['ID', 'Дата', 'Сумма', 'Кол-во', 'Товар', 'Автомат', 'Оплата'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table)
        self.refresh()

    def refresh(self):
        self._last_rows = sales_report(300)
        rows = self._last_rows
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            vals = [row['id'], row['sold_at'], row['amount'], row['quantity'], row['product_name'], row['machine_name'], row['payment_method']]
            for c, val in enumerate(vals):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))

    def refresh_for_session(self):
        self.exp_btn.setVisible(session.role != 'viewer')

    def _export_xlsx(self):
        if not self._last_rows:
            QMessageBox.information(self, 'Экспорт', 'Нет данных для экспорта.')
            return
        path, _ = QFileDialog.getSaveFileName(self, 'Скачать Excel', 'reports.xlsx', 'Excel (*.xlsx)')
        if not path:
            return
        try:
            _export_reports_xlsx(self._last_rows, Path(path))
            QMessageBox.information(self, 'Экспорт', f'Файл сохранён: {path}')
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', str(exc))
