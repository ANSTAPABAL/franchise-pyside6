"""главное окно приложения.

собирает весь интерфейс после успешного входа:
- верхняя панель (лого, название, профиль, выход);
- левое меню навигации (sidebar);
- стек страниц (переключается при нажатии пункта меню).
"""

from __future__ import annotations

import base64
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow,
    QMenu, QMessageBox, QPushButton, QStackedWidget, QToolButton,
    QVBoxLayout, QWidget,
)

from app.pages.admin_machines_page import AdminMachinesPage
from app.pages.admin_catalog_pages import CompaniesPage, ExtraPage, ModemsPage, UsersPage
from app.pages.dashboard_page import DashboardPage
from app.pages.inventory_page import InventoryPage
from app.pages.monitor_page import MonitorPage
from app.pages.reports_page import ReportsPage
from app.session import session
from app.widgets.sidebar import Sidebar


def _to_initials(full_name: str) -> str:
    """форматирует фио в вид «фамилия и.о.» для кнопки профиля.

    пример: «Иванов Иван Иванович» → «Иванов И.И.»
    """
    parts = full_name.split()
    if not parts:
        return ''
    surname = parts[0]
    # берём первую букву каждого слова после фамилии и добавляем точку
    initials = ''.join(f'{p[0]}.' for p in parts[1:] if p)
    return f'{surname} {initials}'.strip()


class MainWindow(QMainWindow):
    """основной контейнер интерфейса после успешного входа.

    структура layout:
        QMainWindow
          └── QWidget (root)
                ├── QFrame#topbar  — шапка
                └── QWidget (holder)
                      ├── Sidebar  — левое меню
                      └── QStackedWidget (stack)  — страницы
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Личный кабинет франчайзера')
        self.resize(1855, 980)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── верхняя панель ──────────────────────────────────────────────
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
        menu_btn.setObjectName('topbarMenuIcon')
        brand = QLabel('ООО Торговые Автоматы')
        brand.setObjectName('brandLabel')

        # хлебная крошка — показывает текущий раздел
        crumb = QLabel('Главная')
        crumb.setObjectName('crumbLabel')
        self.crumb = crumb

        # фото пользователя (маленький аватар в правом углу)
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(26, 26)
        self._fill_photo()

        # кнопка профиля с выпадающим меню
        self.profile_btn = QToolButton()
        self.profile_btn.setText(f"{_to_initials(session.full_name)}\n{session.role}")
        self.profile_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.profile_btn.setPopupMode(QToolButton.InstantPopup)  # меню открывается сразу при нажатии
        self.profile_btn.setObjectName('topbarProfileBtn')

        profile_menu = QMenu(self.profile_btn)
        profile_menu.addAction(QAction('Мой профиль', self, triggered=self._show_profile))
        profile_menu.addAction(QAction('Мои сессии', self, triggered=self._show_my_sessions))
        profile_menu.addSeparator()
        profile_menu.addAction(QAction('Выход', self, triggered=self._logout))
        self.profile_btn.setMenu(profile_menu)

        top.addWidget(logo_label)
        top.addSpacing(8)
        top.addWidget(menu_btn)
        top.addSpacing(10)
        top.addWidget(brand)
        top.addStretch(1)  # растягивает пространство между брендом и правой частью
        top.addWidget(crumb)
        top.addSpacing(24)
        top.addWidget(self.photo_label)
        top.addWidget(self.profile_btn)
        layout.addWidget(topbar)

        # ── тело: sidebar + stack страниц ───────────────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.menu_selected.connect(self._on_menu)  # слушаем сигнал выбора пункта
        self.is_admin = session.role == 'admin'
        self.sidebar.set_admin_visible(self.is_admin)
        body.addWidget(self.sidebar)

        # QStackedWidget хранит все страницы, показывает одну за раз
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
            self.stack.addWidget(page)  # все страницы добавляются в стек

        body.addWidget(self.stack, 1)  # stretch=1 — стек занимает оставшееся место
        holder = QWidget()
        holder.setLayout(body)
        layout.addWidget(holder, 1)

        # открываем главную страницу по умолчанию
        self._on_menu('dashboard')

    def _refresh_session_ui(self):
        """обновляет ui после повторного входа под другим пользователем.

        вызывается когда пользователь нажал «выход» и вошёл заново —
        перечитываем роль, фото и имя из объекта session.
        """
        self.photo_label.clear()
        self._fill_photo()
        self.profile_btn.setText(f"{_to_initials(session.full_name)}\n{session.role}")
        self.is_admin = session.role == 'admin'
        self.sidebar.set_admin_visible(self.is_admin)
        # обновляем страницы, которые зависят от роли (кнопки экспорта и т.п.)
        for key in ('monitor', 'reports', 'inventory'):
            page = self.pages.get(key)
            if page and hasattr(page, 'refresh_for_session'):
                page.refresh_for_session()

    def _logout(self):
        """разлогинивает пользователя и снова показывает окно входа.

        фишка: окно не уничтожается, а скрывается (hide). если новый логин
        прошёл успешно — показываем его снова (show). если закрыли диалог —
        завершаем приложение.
        """
        from app.dialogs.login_dialog import LoginDialog
        self.hide()
        login = LoginDialog()
        if login.exec():
            self._refresh_session_ui()
            self.show()
        else:
            QApplication.quit()

    def _fill_photo(self):
        """показывает фото пользователя из session.photo_base64 или флаг-заглушку.

        фото хранится в бд как base64-строка (возможно с префиксом data:image/...;base64,).
        отрезаем префикс, декодируем байты, загружаем как QPixmap.
        если что-то пошло не так — ставим эмодзи-флаг.
        """
        raw = session.photo_base64
        if raw:
            try:
                # убираем префикс «data:image/png;base64,» если он есть
                payload = raw.split(',', 1)[1] if ',' in raw else raw
                decoded = base64.b64decode(payload)
                loaded = QPixmap()
                if loaded.loadFromData(decoded):
                    pix = loaded.scaled(26, 26, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    self.photo_label.setPixmap(pix)
                    self.photo_label.setText('')
                    return
            except Exception:
                pass  # если декодирование не удалось — идём дальше к заглушке
        # заглушка — флаг вместо фото
        self.photo_label.setPixmap(QPixmap())
        self.photo_label.setText('🇷🇺')
        self.photo_label.setStyleSheet('font-size:18px;')

    def _on_menu(self, key: str):
        """переключает текущую страницу по ключу из sidebar.

        ключи: 'dashboard', 'monitor', 'reports', 'inventory',
               'admin_machines', 'admin_companies', 'admin_users',
               'admin_modems', 'admin_extra'.

        раздел admin_* доступен только роли admin — иначе показываем предупреждение.
        """
        if key not in self.pages:
            return
        if key.startswith('admin_') and not self.is_admin:
            QMessageBox.warning(self, 'Доступ ограничен', 'Этот раздел доступен только администратору.')
            return
        self.stack.setCurrentWidget(self.pages[key])  # показываем нужную страницу
        # обновляем хлебную крошку в шапке
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
        """показывает всплывающее окно с данными текущего пользователя."""
        QMessageBox.information(
            self,
            'Профиль сотрудника',
            f'ФИО: {session.full_name}\nEmail: {session.email}\nРоль: {session.role}',
        )

    def _show_my_sessions(self):
        """показывает информацию о текущей сессии пользователя."""
        QMessageBox.information(
            self,
            'Мои сессии',
            f'Текущая сессия:\n\nФИО: {session.full_name}\nEmail: {session.email}\nРоль: {session.role}',
        )
