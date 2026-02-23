from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from services.reports_service import stock_report


class InventoryPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        title = QLabel('Учет ТМЦ')
        title.setObjectName('panelTitle')
        root.addWidget(title)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(['Автомат', 'Товар', 'Количество', 'Мин. запас', 'Нужно пополнение', 'machine_id'])
        root.addWidget(self.table)
        self.refresh()

    def refresh(self):
        rows = stock_report(500)
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            vals = [row['machine_name'], row['product_name'], row['quantity_available'], row['min_stock'], row['need_refill'], row['machine_id']]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                if c == 4 and row['need_refill']:
                    item.setBackground(QColor('#ffd2d2'))
                self.table.setItem(r, c, item)
