from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class StubPage(QWidget):
    def __init__(self, text: str):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(text))
