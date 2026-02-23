from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFileDialog, QHeaderView, QLabel, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from services.reports_service import stock_report


def _export_inventory_xlsx(rows: list, path: Path) -> None:
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = 'Учёт ТМЦ'
    headers = ['Автомат', 'Товар', 'Количество', 'Мин. запас', 'Нужно пополнение', 'machine_id']
    ws.append(headers)
    for r in rows:
        ws.append([r.get('machine_name'), r.get('product_name'), r.get('quantity_available'), r.get('min_stock'), r.get('need_refill'), r.get('machine_id')])
    wb.save(path)


class InventoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self._last_rows: list = []
        root = QVBoxLayout(self)
        title = QLabel('Учет ТМЦ')
        title.setObjectName('panelTitle')
        root.addWidget(title)

        exp_btn = QPushButton('Скачать Excel')
        exp_btn.clicked.connect(self._export_xlsx)
        root.addWidget(exp_btn)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(['Автомат', 'Товар', 'Количество', 'Мин. запас', 'Нужно пополнение', 'machine_id'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table)
        self.refresh()

    def refresh(self):
        self._last_rows = stock_report(500)
        rows = self._last_rows
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            vals = [row['machine_name'], row['product_name'], row['quantity_available'], row['min_stock'], row['need_refill'], row['machine_id']]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                if c == 4 and row['need_refill']:
                    item.setBackground(QColor('#ffd2d2'))
                self.table.setItem(r, c, item)

    def _export_xlsx(self):
        if not self._last_rows:
            QMessageBox.information(self, 'Экспорт', 'Нет данных для экспорта.')
            return
        path, _ = QFileDialog.getSaveFileName(self, 'Скачать Excel', 'inventory.xlsx', 'Excel (*.xlsx)')
        if not path:
            return
        try:
            _export_inventory_xlsx(self._last_rows, Path(path))
            QMessageBox.information(self, 'Экспорт', f'Файл сохранён: {path}')
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', str(exc))
