import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from rfi.ui.main_window import MainWindow


def resource_path(rel: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def main() -> int:
    app = QApplication(sys.argv)
    icon_file = "assets/icon.ico" if sys.platform == "win32" else "assets/icon.png"
    icon = QIcon(resource_path(icon_file))
    app.setWindowIcon(icon)
    window = MainWindow()
    window.setWindowIcon(icon)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
