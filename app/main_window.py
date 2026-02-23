from __future__ import annotations

import base64
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QMenu, QMessageBox, QPushButton, QStackedWidget, QToolButton, QVBoxLayout, QWidget

from app.pages.admin_machines_page import AdminMachinesPage
from app.pages.admin_catalog_pages import CompaniesPage, ExtraPage, ModemsPage, UsersPage
from app.pages.dashboard_page import DashboardPage
from app.pages.inventory_page import InventoryPage
from app.pages.monitor_page import MonitorPage
from app.pages.reports_page import ReportsPage
from app.session import session
from app.widgets.sidebar import Sidebar


def _to_initials(full_name: str) -> str:
    parts = full_name.split()
    if not parts:
        return ''
    surname = parts[0]
    initials = ''.join(f'{p[0]}.' for p in parts[1:] if p)
    return f'{surname} {initials}'.strip()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Личный кабинет франчайзера')
        self.resize(1855, 980)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        topbar = QFrame()
        topbar.setObjectName('topbar')
        top = QHBoxLayout(topbar)
        top.setContentsMargins(14, 0, 14, 0)
        logo_label = QLabel()
        logo_label.setFixedSize(28, 28)
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "app_logo2.png"
        if logo_path.exists():
            logo_pix = QPixmap(str(logo_path)).scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pix)

        menu_btn = QLabel('☰')
        menu_btn.setStyleSheet('color:#64748b;')
        brand = QLabel('ООО Торговые Автоматы')
        brand.setObjectName('brandLabel')
        crumb = QLabel('Главная')
        crumb.setObjectName('crumbLabel')
        self.crumb = crumb

        self.photo_label = QLabel()
        self.photo_label.setFixedSize(26, 26)
        self._fill_photo()

        profile_btn = QToolButton()
        profile_btn.setText(f"{_to_initials(session.full_name)}\n{session.role}")
        profile_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        profile_btn.setPopupMode(QToolButton.InstantPopup)
        profile_btn.setStyleSheet('color:#334155;font-size:10pt;border:none;')

        profile_menu = QMenu(profile_btn)
        profile_menu.addAction(QAction('Мой профиль', self, triggered=self._show_profile))
        profile_menu.addAction(QAction('Мои сессии', self, triggered=self._show_my_sessions))
        profile_menu.addSeparator()
        profile_menu.addAction(QAction('Выход', self, triggered=self.close))
        profile_btn.setMenu(profile_menu)

        top.addWidget(logo_label)
        top.addSpacing(8)
        top.addWidget(menu_btn)
        top.addSpacing(10)
        top.addWidget(brand)
        top.addStretch(1)
        top.addWidget(crumb)
        top.addSpacing(24)
        top.addWidget(self.photo_label)
        top.addWidget(profile_btn)
        layout.addWidget(topbar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.menu_selected.connect(self._on_menu)
        self.is_admin = session.role == 'admin'
        self.sidebar.set_admin_visible(self.is_admin)
        body.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.pages = {
            'dashboard': DashboardPage(),
            'monitor': MonitorPage(),
            'reports': ReportsPage(),
            'inventory': InventoryPage(),
            'admin_machines': AdminMachinesPage(),
            'admin_companies': CompaniesPage(),
            'admin_users': UsersPage(),
            'admin_modems': ModemsPage(),
            'admin_extra': ExtraPage(),
        }
        for page in self.pages.values():
            self.stack.addWidget(page)

        body.addWidget(self.stack, 1)
        holder = QWidget()
        holder.setLayout(body)
        layout.addWidget(holder, 1)

        self._on_menu('dashboard')

    def _fill_photo(self):
        placeholder = QPixmap(26, 26)
        placeholder.fill(Qt.lightGray)
        pix = placeholder
        raw = session.photo_base64
        if raw:
            try:
                payload = raw.split(',', 1)[1] if ',' in raw else raw
                decoded = base64.b64decode(payload)
                loaded = QPixmap()
                if loaded.loadFromData(decoded):
                    pix = loaded.scaled(26, 26, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            except Exception:
                pass
        self.photo_label.setPixmap(pix)

    def _on_menu(self, key: str):
        if key not in self.pages:
            return
        if key.startswith('admin_') and not self.is_admin:
            QMessageBox.warning(self, 'Доступ ограничен', 'Этот раздел доступен только администратору.')
            return
        self.stack.setCurrentWidget(self.pages[key])
        names = {
            'dashboard': 'Главная',
            'monitor': 'Монитор ТА',
            'reports': 'Детальные отчеты',
            'inventory': 'Учет ТМЦ',
            'admin_machines': 'Администрирование / Торговые автоматы',
            'admin_companies': 'Администрирование / Компании',
            'admin_users': 'Администрирование / Пользователи',
            'admin_modems': 'Администрирование / Модемы',
            'admin_extra': 'Администрирование / Дополнительные',
        }
        self.crumb.setText(names.get(key, ''))

    def _show_profile(self):
        QMessageBox.information(
            self,
            'Профиль сотрудника',
            f'ФИО: {session.full_name}\nEmail: {session.email}\nРоль: {session.role}',
        )

    def _show_my_sessions(self):
        QMessageBox.information(
            self,
            'Мои сессии',
            f'Текущая сессия:\n\nФИО: {session.full_name}\nEmail: {session.email}\nРоль: {session.role}',
        )
