from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from services.monitor_service import monitor_rows


class MonitorPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)

        title = QLabel('Монитор торговых автоматов')
        title.setObjectName('panelTitle')
        root.addWidget(title)

        filters = QHBoxLayout()
        self.state = QComboBox()
        self.state.addItem('Общее состояние', '')
        self.state.addItems(['working', 'broken', 'maintenance'])

        self.conn_type = QComboBox()
        self.conn_type.addItem('Подключение', '')
        self.conn_type.addItems(['gsm', 'wifi', 'ethernet'])

        self.extra = QComboBox()
        self.extra.addItem('Дополнительные статусы', '')
        self.extra.addItems(['attention', 'warning', 'critical'])

        self.sort = QComboBox()
        self.sort.addItems(['По состоянию ТА'])

        apply_btn = QPushButton('Применить')
        clear_btn = QPushButton('Очистить')
        clear_btn.setProperty('variant', 'ghost')
        apply_btn.clicked.connect(self.refresh)
        clear_btn.clicked.connect(self._clear)

        for w in [self.state, self.conn_type, self.extra, self.sort, apply_btn, clear_btn]:
            filters.addWidget(w)
        root.addLayout(filters)

        totals = QHBoxLayout()
        self.total_label = QLabel('Итого автоматов: 0')
        self.money_label = QLabel('Денег в автоматах: 0.00')
        totals.addWidget(self.total_label)
        totals.addWidget(self.money_label)
        totals.addStretch(1)
        root.addLayout(totals)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(['#', 'Торговый автомат', 'Связь', 'Загрузка', 'Денежные средства', 'События', 'Оборудование', 'Информация', 'Доп.'])
        root.addWidget(self.table)

        self.empty_label = QLabel('')
        self.empty_label.setStyleSheet('font-size:22px;color:#505050;padding:8px;')
        root.addWidget(self.empty_label)

        self.refresh()

    def _clear(self):
        self.state.setCurrentIndex(0)
        self.conn_type.setCurrentIndex(0)
        self.extra.setCurrentIndex(0)
        self.refresh()

    def refresh(self):
        try:
            rows, totals = monitor_rows(self.state.currentData(), self.conn_type.currentData(), self.extra.currentData())
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', str(exc))
            return

        self.total_label.setText(f"Итого автоматов: {totals['machines']}")
        self.money_label.setText(f"Денег в автоматах: {totals['money']:.2f}")
        self.empty_label.setText('')

        if not rows:
            self.empty_label.setText('Нет активных торговых автоматов, соответствующих заданному фильтру')

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            values = [row['num'], row['tp'], row['connection'], row['load'], row['cash'], row['events'], row['equipment'], row['info'], row['extra']]
            for c, val in enumerate(values):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))
