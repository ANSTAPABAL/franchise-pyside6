"""страница «монитор та».

пользователь фильтрует автоматы по состоянию, типу связи и доп. статусу,
видит таблицу с оперативными показателями и может скачать её в excel.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QHeaderView, QHBoxLayout, QLabel,
    QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from app.session import session
from services.monitor_service import monitor_rows


def _export_monitor_xlsx(rows: list, path: Path) -> None:
    """экспортирует текущую таблицу монитора в excel-файл.

    openpyxl импортируется внутри функции — не грузим библиотеку при старте,
    только когда реально нужен экспорт.
    """
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = 'Монитор ТА'
    headers = ['№', 'Торговый автомат', 'Связь', 'Загрузка', 'Денежные средства',
               'События', 'Оборудование', 'Информация', 'Доп.']
    ws.append(headers)
    for r in rows:
        ws.append([
            r.get('num'), r.get('tp'), r.get('connection'), r.get('load'),
            r.get('cash'), r.get('events'), r.get('equipment'), r.get('info'), r.get('extra'),
        ])
    wb.save(path)


class MonitorPage(QWidget):
    """экран мониторинга: фильтры, итоги и таблица состояния автоматов."""
    def __init__(self):
        super().__init__()
        self._last_rows: list = []  # сохраняем последние данные для экспорта
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)

        title = QLabel('Монитор торговых автоматов')
        title.setObjectName('panelTitle')
        root.addWidget(title)

        # строка фильтров
        filters = QHBoxLayout()
        self.state = QComboBox()
        self.state.addItem('Общее состояние', '')  # userData='' — значит фильтр не активен
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
        self.exp_btn = QPushButton('Скачать Excel')
        clear_btn.setProperty('variant', 'ghost')
        apply_btn.clicked.connect(self.refresh)
        clear_btn.clicked.connect(self._clear)
        self.exp_btn.clicked.connect(self._export_xlsx)
        # кнопка экспорта скрыта для роли viewer
        self.exp_btn.setVisible(session.role != 'viewer')

        for w in [self.state, self.conn_type, self.extra, self.sort, apply_btn, clear_btn, self.exp_btn]:
            filters.addWidget(w)
        root.addLayout(filters)

        # строка итогов под фильтрами
        totals = QHBoxLayout()
        self.total_label = QLabel('Итого автоматов: 0')
        self.money_label = QLabel('Денег в автоматах: 0.00')
        totals.addWidget(self.total_label)
        totals.addWidget(self.money_label)
        totals.addStretch(1)
        root.addLayout(totals)

        # таблица с 9 колонками
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels([
            '#', 'Торговый автомат', 'Связь', 'Загрузка',
            'Денежные средства', 'События', 'Оборудование', 'Информация', 'Доп.',
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table)

        # метка «нет данных» (скрыта пока есть строки)
        self.empty_label = QLabel('')
        self.empty_label.setObjectName('emptyStateLabel')
        root.addWidget(self.empty_label)

        self.refresh()

    def _clear(self):
        """сбрасывает все фильтры на «показать всё» и обновляет таблицу."""
        self.state.setCurrentIndex(0)
        self.conn_type.setCurrentIndex(0)
        self.extra.setCurrentIndex(0)
        self.refresh()

    def refresh(self):
        """запрашивает данные монитора с учётом фильтров и обновляет таблицу.

        currentData() — возвращает userData комбобокса, не отображаемый текст.
        для пустого элемента 'Общее состояние' userData='' → None в сервис передаётся '',
        что означает «без фильтра».
        """
        try:
            rows, totals = monitor_rows(
                self.state.currentData(),
                self.conn_type.currentData(),
                self.extra.currentData(),
            )
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
            values = [
                row['num'], row['tp'], row['connection'], row['load'],
                row['cash'], row['events'], row['equipment'], row['info'], row['extra'],
            ]
            for c, val in enumerate(values):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))

    def refresh_for_session(self):
        """обновляет элементы при смене пользователя (видимость кнопки экспорта)."""
        self.exp_btn.setVisible(session.role != 'viewer')

    def _export_xlsx(self):
        """сохраняет текущие строки монитора в .xlsx через диалог выбора файла."""
        if not self._last_rows:
            QMessageBox.information(self, 'Экспорт', 'Нет данных для экспорта.')
            return
        # QFileDialog.getSaveFileName возвращает (путь, выбранный_фильтр)
        path, _ = QFileDialog.getSaveFileName(self, 'Скачать Excel', 'monitor_ta.xlsx', 'Excel (*.xlsx)')
        if not path:
            return  # пользователь нажал «отмена»
        try:
            _export_monitor_xlsx(self._last_rows, Path(path))
            QMessageBox.information(self, 'Экспорт', f'Файл сохранён: {path}')
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', str(exc))
