"""единая qss-тема приложения.

qss (qt style sheets) — это как css, только для qt-виджетов.
лучше менять цвета/размеры именно здесь, чтобы стиль был одинаковым
во всех окнах сразу, а не разбросан по коду.

фишка: objectName в python-коде (widget.setObjectName('topbar'))
позволяет прицеливаться к конкретному виджету в qss через #topbar,
как id в css.
"""

APP_STYLESHEET = """
/* базовые стили для всего приложения */
QMainWindow, QWidget {
    background-color: #f8fafc;
    color: #1e293b;
    font-family: 'Segoe UI';
    font-size: 10pt;
}

/* верхняя панель (логотип, название, профиль) */
QFrame#topbar {
    background-color: #ffffff;
    min-height: 48px;
    max-height: 48px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
}

QLabel#topbarMenuIcon {
    color: #64748b;
    font-size: 10pt;
}

QToolButton#topbarProfileBtn {
    color: #334155;
    font-size: 10pt;
    border: none;
}

/* название компании в шапке */
QLabel#brandLabel {
    color: #1e293b;
    font-size: 14pt;
    font-weight: 600;
}

/* текущий раздел (хлебная крошка) */
QLabel#crumbLabel {
    color: #64748b;
    font-size: 10pt;
}

/* левое меню навигации */
QFrame#sidebar {
    background-color: #f1f5f9;
    min-width: 240px;
    max-width: 240px;
    border: none;
    border-right: 1px solid #e2e8f0;
}

QLabel#sidebarTitle {
    color: #475569;
    font-size: 12pt;
    font-weight: 600;
    padding: 14px 14px 8px 14px;
}

/* кнопки разделов в меню */
QToolButton#menuButton {
    color: #334155;
    font-size: 10pt;
    text-align: left;
    border: none;
    padding: 10px 14px;
}

QToolButton#menuButton:hover {
    background-color: #e2e8f0;
    color: #1e293b;
}

/* активный (выбранный) пункт меню — синий */
QToolButton#menuButton:checked {
    background-color: #dbeafe;
    color: #1d4ed8;
}

/* карточка/плитка на странице */
QFrame#panelCard {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 6px;
}

/* заголовок страницы (синий крупный) */
QLabel#panelTitle {
    color: #1d4ed8;
    font-size: 18pt;
    font-weight: 600;
    padding: 6px 8px;
}

/* заголовок внутри карточки */
QLabel#cardTitle {
    color: #374151;
    font-size: 11pt;
    font-weight: 600;
    padding: 6px 8px;
}

/* кнопки — синие по умолчанию */
QPushButton {
    background-color: #3b82f6;
    color: #ffffff;
    border: 1px solid #3b82f6;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 10pt;
}

QPushButton:hover {
    background-color: #2563eb;
}

/* вторичные кнопки (отмена, удалить) — светлые */
QPushButton[variant='ghost'] {
    background-color: #f9fafb;
    color: #374151;
    border: 1px solid #d1d5db;
}

/* поля ввода */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit {
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    padding: 6px 8px;
    min-height: 28px;
    font-size: 10pt;
}

/* таблицы */
QTableWidget {
    background: #ffffff;
    border: 1px solid #d1d5db;
    gridline-color: #e5e7eb;
    font-size: 10pt;
}

/* заголовки колонок таблицы */
QHeaderView::section {
    background: #f3f4f6;
    border: 1px solid #d1d5db;
    padding: 6px;
    font-size: 10pt;
    font-weight: 600;
}

/* выпадающее меню (профиль и т.п.) */
QMenu {
    background: #ffffff;
    border: 1px solid #d1d5db;
    font-size: 10pt;
}

QMenu::item {
    padding: 8px 24px;
}

QMenu::item:selected {
    background-color: #e6eef8;
}

/* заглушка «нет данных» */
QLabel#emptyStateLabel {
    color: #64748b;
    font-size: 14pt;
    padding: 8px;
}

/* значение в карточке (крупная цифра) */
QLabel#cardValueLabel {
    color: #1e293b;
    font-size: 12pt;
    padding: 8px;
}

/* список (плиточный режим) */
QListWidget {
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 10pt;
    color: #1e293b;
}

/* диалоговые окна (логин, форма та) */
QDialog {
    background-color: #f8fafc;
    color: #1e293b;
    font-family: 'Segoe UI';
    font-size: 10pt;
}
"""
