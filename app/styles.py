APP_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #f3f4f6;
    color: #1f2937;
    font-family: 'Segoe UI';
    font-size: 10pt;
}

QFrame#topbar {
    background-color: #0b1220;
    min-height: 48px;
    max-height: 48px;
    border: none;
}

QLabel#brandLabel {
    color: #f8fafc;
    font-size: 14pt;
    font-weight: 600;
}

QLabel#crumbLabel {
    color: #94a3b8;
    font-size: 10pt;
}

QFrame#sidebar {
    background-color: #111827;
    min-width: 240px;
    max-width: 240px;
    border: none;
}

QLabel#sidebarTitle {
    color: #e5e7eb;
    font-size: 12pt;
    font-weight: 600;
    padding: 14px 14px 8px 14px;
}

QToolButton#menuButton {
    color: #e5e7eb;
    font-size: 10pt;
    text-align: left;
    border: none;
    padding: 10px 14px;
}

QToolButton#menuButton:hover {
    background-color: #1f2937;
}

QToolButton#menuButton:checked {
    background-color: #2563eb;
    color: #ffffff;
}

QFrame#panelCard {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 6px;
}

QLabel#panelTitle {
    color: #1d4ed8;
    font-size: 18pt;
    font-weight: 600;
    padding: 6px 8px;
}

QLabel#cardTitle {
    color: #374151;
    font-size: 11pt;
    font-weight: 600;
    padding: 6px 8px;
}

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

QPushButton[variant='ghost'] {
    background-color: #f9fafb;
    color: #374151;
    border: 1px solid #d1d5db;
}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit {
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    padding: 6px 8px;
    min-height: 28px;
    font-size: 10pt;
}

QTableWidget {
    background: #ffffff;
    border: 1px solid #d1d5db;
    gridline-color: #e5e7eb;
    font-size: 10pt;
}

QHeaderView::section {
    background: #f3f4f6;
    border: 1px solid #d1d5db;
    padding: 6px;
    font-size: 10pt;
    font-weight: 600;
}

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
"""
