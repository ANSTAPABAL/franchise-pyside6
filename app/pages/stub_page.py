"""заглушка страницы.

используется вместо настоящей страницы, когда раздел ещё не реализован.
просто показывает текст по центру.
"""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class StubPage(QWidget):
    """минимальный виджет-заглушка с одной текстовой меткой."""
    def __init__(self, text: str):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(text))
