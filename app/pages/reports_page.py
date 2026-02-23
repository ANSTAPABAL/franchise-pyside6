from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from services.reports_service import sales_report


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        title = QLabel('Детальные отчеты')
        title.setObjectName('panelTitle')
        root.addWidget(title)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(['ID', 'Дата', 'Сумма', 'Кол-во', 'Товар', 'Автомат', 'Оплата'])
        root.addWidget(self.table)
        self.refresh()

    def refresh(self):
        rows = sales_report(300)
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            vals = [row['id'], row['sold_at'], row['amount'], row['quantity'], row['product_name'], row['machine_name'], row['payment_method']]
            for c, val in enumerate(vals):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))
