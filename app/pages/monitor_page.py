from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QLabel, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from services.monitor_service import monitor_rows


def _export_monitor_xlsx(rows: list, path: Path) -> None:
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = 'Монитор ТА'
    headers = ['№', 'Торговый автомат', 'Связь', 'Загрузка', 'Денежные средства', 'События', 'Оборудование', 'Информация', 'Доп.']
    ws.append(headers)
    for r in rows:
        ws.append([r.get('num'), r.get('tp'), r.get('connection'), r.get('load'), r.get('cash'), r.get('events'), r.get('equipment'), r.get('info'), r.get('extra')])
    wb.save(path)


class MonitorPage(QWidget):
    def __init__(self):
        super().__init__()
        self._last_rows: list = []
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)

        title = QLabel('Монитор торговых автоматов')
        title.setObjectName('panelTitle')
        root.addWidget(title)

        filters = QHBoxLayout()
        self.state = QComboBox()
        self.state.addItem('Общее состояние', '')
        for v in ['working', 'broken', 'maintenance']:
            self.state.addItem(v, v)

        self.conn_type = QComboBox()
        self.conn_type.addItem('Подключение', '')
        for v in ['gsm', 'wifi', 'ethernet']:
            self.conn_type.addItem(v, v)

        self.extra = QComboBox()
        self.extra.addItem('Дополнительные статусы', '')
        for v in ['attention', 'warning', 'critical']:
            self.extra.addItem(v, v)

        self.sort = QComboBox()
        self.sort.addItems(['По состоянию ТА'])

        apply_btn = QPushButton('Применить')
        clear_btn = QPushButton('Очистить')
        exp_btn = QPushButton('Скачать Excel')
        clear_btn.setProperty('variant', 'ghost')
        apply_btn.clicked.connect(self.refresh)
        clear_btn.clicked.connect(self._clear)
        exp_btn.clicked.connect(self._export_xlsx)

        for w in [self.state, self.conn_type, self.extra, self.sort, apply_btn, clear_btn, exp_btn]:
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

        self._last_rows = rows
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            values = [row['num'], row['tp'], row['connection'], row['load'], row['cash'], row['events'], row['equipment'], row['info'], row['extra']]
            for c, val in enumerate(values):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))

    def _export_xlsx(self):
        if not self._last_rows:
            QMessageBox.information(self, 'Экспорт', 'Нет данных для экспорта.')
            return
        path, _ = QFileDialog.getSaveFileName(self, 'Скачать Excel', 'monitor_ta.xlsx', 'Excel (*.xlsx)')
        if not path:
            return
        try:
            _export_monitor_xlsx(self._last_rows, Path(path))
            QMessageBox.information(self, 'Экспорт', f'Файл сохранён: {path}')
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', str(exc))
