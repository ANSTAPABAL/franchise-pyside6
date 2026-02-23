from __future__ import annotations

import csv
from pathlib import Path

from PySide6.QtGui import QColor, QIcon, QPageLayout, QPageSize, QPdfWriter
from PySide6.QtWidgets import QComboBox, QFileDialog, QHeaderView, QHBoxLayout, QInputDialog, QLabel, QListWidget, QMessageBox, QPushButton, QStackedLayout, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from app.dialogs.machine_form_dialog import MachineFormDialog
from services.vending_service import delete_machine, list_company_folders, list_machines, unbind_modem


class AdminMachinesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.offset = 0
        self.total = 0
        self.rows: list[dict] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)

        title = QLabel('Торговые автоматы')
        title.setObjectName('panelTitle')
        root.addWidget(title)

        controls = QHBoxLayout()
        self.view_mode = QComboBox()
        self.view_mode.addItems(['table', 'tile'])
        self.view_mode.currentTextChanged.connect(self._switch_view)

        self.limit_combo = QComboBox()
        self.limit_combo.addItems(['10', '20', '50'])
        self.limit_combo.setCurrentText('20')

        self.search = QComboBox()
        self.search.setEditable(True)
        self.search.lineEdit().setPlaceholderText('Фильтр')

        self.company_filter = QComboBox()
        self.company_filter.addItem('Все', '')
        try:
            for item in list_company_folders():
                self.company_filter.addItem(item['name'], item['id'])
        except Exception:
            pass

        apply_btn = QPushButton('Применить')
        add_btn = QPushButton('+ Добавить')
        exp_btn = QPushButton('Экспорт')
        apply_btn.clicked.connect(self.refresh)
        add_btn.clicked.connect(self._add_machine)
        exp_btn.clicked.connect(self._export_menu)

        self.count_label = QLabel('0 из 0')
        for w in [QLabel('Показать'), self.limit_combo, QLabel('записей'), self.search, self.company_filter, apply_btn, add_btn, exp_btn, self.count_label]:
            controls.addWidget(w)
        root.addLayout(controls)

        self.stack = QStackedLayout()
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(['ID', 'Название автомата', 'Модель', 'Компания', 'Модем', 'Адрес / Место', 'В работе с', 'Статус', 'Действия'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.tiles = QListWidget()

        table_holder = QWidget(); table_holder.setLayout(QVBoxLayout()); table_holder.layout().addWidget(self.table)
        tile_holder = QWidget(); tile_holder.setLayout(QVBoxLayout()); tile_holder.layout().addWidget(self.tiles)
        self.stack.addWidget(table_holder)
        self.stack.addWidget(tile_holder)

        stack_widget = QWidget()
        stack_widget.setLayout(self.stack)
        root.addWidget(stack_widget)

        self._empty_label = QLabel('Нет торговых автоматов по заданному фильтру')
        self._empty_label.setObjectName('emptyStateLabel')
        self._empty_label.setVisible(False)
        root.addWidget(self._empty_label)

        pager = QHBoxLayout()
        prev_btn = QPushButton('<')
        next_btn = QPushButton('>')
        prev_btn.setProperty('variant', 'ghost')
        next_btn.setProperty('variant', 'ghost')
        prev_btn.clicked.connect(self._prev)
        next_btn.clicked.connect(self._next)
        pager.addStretch(1)
        pager.addWidget(prev_btn)
        pager.addWidget(next_btn)
        root.addLayout(pager)

        self.refresh()

    def _icon(self, filename: str) -> QIcon:
        path = Path(__file__).resolve().parents[2] / "assets" / "icons" / "other" / filename
        return QIcon(str(path)) if path.exists() else QIcon()

    def _switch_view(self, val: str):
        self.stack.setCurrentIndex(0 if val == 'table' else 1)

    def _limit(self) -> int:
        return int(self.limit_combo.currentText())

    def _prev(self):
        self.offset = max(0, self.offset - self._limit())
        self.refresh()

    def _next(self):
        if self.offset + self._limit() < self.total:
            self.offset += self._limit()
        self.refresh()

    def refresh(self):
        try:
            search_text = self.search.lineEdit().text().strip() if self.search.isEditable() else self.search.currentText().strip()
            self.total, self.rows = list_machines(
                search=search_text,
                limit=self._limit(),
                offset=self.offset,
                company_folder_id=self.company_filter.currentData() or None,
            )
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', str(exc))
            return

        self.count_label.setText(f"Всего найдено {self.total} шт.")
        self._empty_label.setVisible(self.total == 0)
        self._render_table()
        self._render_tiles()

    def _render_table(self):
        self.table.setRowCount(len(self.rows))
        for r, row in enumerate(self.rows):
            vals = [
                row['id'], row['name'], row.get('model') or '', row.get('company_name') or '',
                row.get('modem_uid') or '—', row.get('location') or '', str(row.get('commissioned_date') or ''), row.get('status') or ''
            ]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                if r % 2 == 1:
                    item.setBackground(QColor('#f7fbff'))
                self.table.setItem(r, c, item)

            actions = QWidget()
            lay = QHBoxLayout(actions); lay.setContentsMargins(0, 0, 0, 0)
            e = QPushButton(''); d = QPushButton(''); u = QPushButton('')
            e.setIcon(self._icon('Details.png'))
            d.setIcon(self._icon('Service.png'))
            u.setIcon(self._icon('Commands.png'))
            e.setProperty('variant', 'ghost'); d.setProperty('variant', 'ghost'); u.setProperty('variant', 'ghost')
            e.clicked.connect(lambda _, rec=row: self._edit_machine(rec))
            d.clicked.connect(lambda _, rec=row: self._delete_machine(rec['id']))
            u.clicked.connect(lambda _, rec=row: self._unbind(rec['id']))
            lay.addWidget(e); lay.addWidget(d); lay.addWidget(u)
            self.table.setCellWidget(r, 8, actions)

    def _render_tiles(self):
        self.tiles.clear()
        for row in self.rows:
            self.tiles.addItem(f"{row['name']}\n{row.get('model') or ''}\n{row.get('company_name') or ''}\nМодем: {row.get('modem_uid') or '—'}")

    def _add_machine(self):
        dlg = MachineFormDialog()
        if dlg.exec():
            self.refresh()

    def _edit_machine(self, row: dict):
        dlg = MachineFormDialog(payload=row)
        if dlg.exec():
            self.refresh()

    def _delete_machine(self, machine_id: str):
        if QMessageBox.question(self, 'Подтверждение', 'Удалить выбранный торговый автомат?') != QMessageBox.Yes:
            return
        try:
            delete_machine(machine_id)
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', str(exc)); return
        self.refresh()

    def _unbind(self, machine_id: str):
        if QMessageBox.question(self, 'Подтверждение', 'Отвязать модем от ТА?') != QMessageBox.Yes:
            return
        try:
            unbind_modem(machine_id)
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', str(exc)); return
        QMessageBox.information(self, 'Готово', 'Модем отвязан. Поле модема примет значение -1.')
        self.refresh()

    def _export_menu(self):
        fmt, ok = QInputDialog.getItem(self, 'Экспорт', 'Формат', ['xlsx', 'csv', 'pdf', 'html'], 0, False)
        if not ok:
            return
        self._export(fmt)

    def _export(self, fmt: str):
        out, _ = QFileDialog.getSaveFileName(self, 'Экспорт', f'machines.{fmt}')
        if not out:
            return
        path = Path(out)
        if fmt == 'xlsx':
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = 'Торговые автоматы'
            headers = ['id', 'name', 'model', 'company_name', 'modem_uid', 'location', 'commissioned_date', 'status']
            ws.append(headers)
            for r in self.rows:
                cd = r.get('commissioned_date')
                if hasattr(cd, 'tzinfo') and getattr(cd, 'tzinfo', None) is not None:
                    cd = cd.replace(tzinfo=None)
                ws.append([r.get('id'), r.get('name'), r.get('model'), r.get('company_name'), r.get('modem_uid') or '—', r.get('location'), cd, r.get('status')])
            wb.save(path)
        elif fmt == 'csv':
            with path.open('w', newline='', encoding='utf-8-sig') as file:
                writer = csv.DictWriter(file, fieldnames=['id', 'name', 'model', 'company_name', 'modem_uid', 'location', 'commissioned_date', 'status'])
                writer.writeheader()
                for r in self.rows:
                    writer.writerow({k: (v if k != 'modem_uid' else (v or '—')) for k, v in r.items()})
        elif fmt == 'html':
            rows = ''.join(
                f"<tr><td>{r['id']}</td><td>{r['name']}</td><td>{r.get('model') or ''}</td><td>{r.get('company_name') or ''}</td></tr>"
                for r in self.rows
            )
            path.write_text(
                '<html><body><table border=1><tr><th>ID</th><th>Название</th><th>Модель</th><th>Компания</th></tr>' + rows + '</table></body></html>',
                encoding='utf-8',
            )
        else:
            writer = QPdfWriter(str(path))
            writer.setPageSize(QPageSize(QPageSize.A4))
            writer.setPageOrientation(QPageLayout.Landscape)
            content = [
                '<h2>Торговые автоматы</h2>',
                '<table border="1" cellspacing="0" cellpadding="4">',
                '<tr><th>ID</th><th>Название</th><th>Модель</th><th>Компания</th><th>Модем</th><th>Адрес</th><th>Статус</th></tr>',
            ]
            for r in self.rows:
                content.append(
                    f"<tr><td>{r['id']}</td><td>{r['name']}</td><td>{r.get('model') or ''}</td>"
                    f"<td>{r.get('company_name') or ''}</td><td>{r.get('modem_uid') or '—'}</td>"
                    f"<td>{r.get('location') or ''}</td><td>{r.get('status') or ''}</td></tr>"
                )
            content.append('</table>')
            from PySide6.QtGui import QTextDocument

            doc = QTextDocument()
            doc.setHtml(''.join(content))
            doc.print(writer)
        QMessageBox.information(self, 'Экспорт', f'Файл сохранен: {path}')
