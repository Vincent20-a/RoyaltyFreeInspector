from PySide6.QtCore import QThread, Signal


class Worker(QThread):
    """Esegue una funzione bloccante fuori dal thread dell'interfaccia."""
    done = Signal(list)
    failed = Signal(str)

    def __init__(self, fn, *args):
        super().__init__()
        self._fn, self._args = fn, args

    def run(self):
        try:
            self.done.emit(self._fn(*self._args))
        except Exception as exc:  # errori di rete, cartelle illeggibili, ecc.
            self.failed.emit(str(exc))
