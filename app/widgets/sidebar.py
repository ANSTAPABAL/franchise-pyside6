from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QLabel, QStyle, QToolButton, QVBoxLayout, QWidget


class Sidebar(QFrame):
    menu_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName('sidebar')
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(2)

        title = QLabel('Навигация')
        title.setObjectName('sidebarTitle')
        root.addWidget(title)

        self.main_btn = self._mk_btn('Главная', 'dashboard', icon_file='Commands.png')
        self.monitor_btn = self._mk_btn('Монитор ТА', 'monitor', icon_file='Details.png')
        self.reports_btn = self._mk_btn('Детальные отчеты', 'reports', icon_file='Details2.png')
        self.inventory_btn = self._mk_btn('Учет ТМЦ', 'inventory', icon_file='Fillup.png')

        self.admin_root_btn = self._mk_btn('Администрирование', 'noop', icon_file='Service.png')
        self.admin_root_btn.setCheckable(True)
        self.admin_root_btn.clicked.connect(self._toggle_admin)

        self.admin_group = QWidget()
        admin_layout = QVBoxLayout(self.admin_group)
        admin_layout.setContentsMargins(26, 0, 0, 0)
        admin_layout.setSpacing(0)
        for text, key in [
            ('Торговые автоматы', 'admin_machines'),
            ('Компании', 'admin_companies'),
            ('Пользователи', 'admin_users'),
            ('Модемы', 'admin_modems'),
            ('Дополнительные', 'admin_extra'),
        ]:
            icon_map = {
                'admin_machines': 'Commands.png',
                'admin_companies': 'FiscalOk.png',
                'admin_users': 'ServiceEncashmentFillup.png',
                'admin_modems': 'Cash.png',
                'admin_extra': 'Encashment.png',
            }
            btn = self._mk_btn(text, key, icon_file=icon_map.get(key))
            btn.setStyleSheet("QToolButton{padding-left:18px;}")
            admin_layout.addWidget(btn)
        self.admin_group.setVisible(False)

        for btn in [self.main_btn, self.monitor_btn, self.reports_btn, self.inventory_btn, self.admin_root_btn]:
            root.addWidget(btn)
        root.addWidget(self.admin_group)
        root.addStretch(1)

    def _mk_btn(self, text: str, key: str, icon_file: str | None = None) -> QToolButton:
        btn = QToolButton()
        btn.setObjectName('menuButton')
        btn.setText(text)
        btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        if icon_file:
            icon_path = Path(__file__).resolve().parents[2] / "assets" / "icons" / "other" / icon_file
            if icon_path.exists():
                btn.setIcon(QIcon(str(icon_path)))
        if btn.icon().isNull():
            btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogInfoView))
        if key != 'noop':
            btn.clicked.connect(lambda: self.menu_selected.emit(key))
        return btn

    def _toggle_admin(self):
        is_open = self.admin_root_btn.isChecked()
        self.admin_group.setVisible(is_open)
        self.admin_root_btn.setArrowType(Qt.UpArrow if is_open else Qt.DownArrow)

    def set_admin_visible(self, visible: bool):
        self.admin_root_btn.setVisible(visible)
        if not visible:
            self.admin_group.setVisible(False)
