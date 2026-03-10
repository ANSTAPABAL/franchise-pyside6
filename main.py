"""минимальный launcher.

нужен, чтобы запускать проект командой `python main.py` из корня.
просто делегирует запуск в app/main.py.
"""

from app.main import run

if __name__ == '__main__':
    run()
