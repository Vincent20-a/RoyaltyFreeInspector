import html

from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QFileDialog, QHBoxLayout, QLabel,
                               QLineEdit, QMainWindow, QMessageBox, QPushButton, QSplitter,
                               QTableWidget, QTableWidgetItem, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)

from ..evaluation import COMMERCIAL, NON_COMMERCIAL, evaluate
from ..local_scan import scan_folder
from ..models import Status
from ..report import export_csv
from ..sources import SOURCES
from ..url_check import check_url
from .workers import Worker

MEDIA = {"Immagini": "image", "Grafiche vettoriali": "graphic",
         "Musica e audio": "audio", "Video": "video"}
COLORS = {Status.VERIFIED: "#2e7d32", Status.TO_CHECK: "#f9a825", Status.NOT_AUTHORIZED: "#c62828"}
HEADERS = ["Stato", "Titolo", "Origine", "Tipo", "Licenza", "Autore"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RoyaltyFree Inspector")
        self.resize(1100, 700)
        self.items = []
        self._worker = None

        tabs = QTabWidget()
        tabs.addTab(self._search_tab(), "Ricerca Internet")
        tabs.addTab(self._local_tab(), "File locali")
        tabs.addTab(self._url_tab(), "Verifica URL")
        tabs.setMaximumHeight(120)

        self.table = QTableWidget(0, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemSelectionChanged.connect(self._show_detail)
        self.detail = QTextBrowser()
        self.detail.setOpenExternalLinks(True)
        split = QSplitter()
        split.addWidget(self.table)
        split.addWidget(self.detail)
        split.setSizes([700, 400])

        self.use = QComboBox()
        self.use.addItem("Uso commerciale", COMMERCIAL)
        self.use.addItem("Uso non commerciale", NON_COMMERCIAL)
        self.use.currentIndexChanged.connect(self._refresh)
        export = QPushButton("Esporta CSV")
        export.clicked.connect(self._export)
        self.info = QLabel("Pronto.")
        bottom = QHBoxLayout()
        bottom.addWidget(QLabel("Uso previsto:"))
        bottom.addWidget(self.use)
        bottom.addStretch()
        bottom.addWidget(self.info)
        bottom.addWidget(export)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(tabs)
        layout.addWidget(split, 1)
        layout.addLayout(bottom)
        self.setCentralWidget(central)

    # --- schede di input ---
    def _search_tab(self):
        w = QWidget()
        row = QHBoxLayout(w)
        self.query = QLineEdit()
        self.query.setPlaceholderText("Cosa cerchi?")
        self.query.returnPressed.connect(self._search)
        self.media = QComboBox()
        self.media.addItems(MEDIA)
        self.source = QComboBox()
        self.source.addItems(SOURCES)
        btn = QPushButton("Cerca")
        btn.clicked.connect(self._search)
        for x in (self.query, self.media, self.source, btn):
            row.addWidget(x)
        return w

    def _local_tab(self):
        w = QWidget()
        row = QHBoxLayout(w)
        self.folder = QLineEdit()
        self.folder.setPlaceholderText("Cartella da analizzare")
        browse = QPushButton("Sfoglia…")
        browse.clicked.connect(self._browse)
        scan = QPushButton("Analizza")
        scan.clicked.connect(self._scan)
        for x in (self.folder, browse, scan):
            row.addWidget(x)
        return w

    def _url_tab(self):
        w = QWidget()
        row = QHBoxLayout(w)
        self.url = QLineEdit()
        self.url.setPlaceholderText("https://…")
        self.url.returnPressed.connect(self._check_url)
        btn = QPushButton("Verifica")
        btn.clicked.connect(self._check_url)
        row.addWidget(self.url)
        row.addWidget(btn)
        return w

    # --- azioni ---
    def _run(self, fn, *args):
        if self._worker and self._worker.isRunning():
            return
        self.info.setText("Elaborazione in corso…")
        self._worker = Worker(fn, *args)
        self._worker.done.connect(self._on_done)
        self._worker.failed.connect(self._on_failed)
        self._worker.start()

    def _search(self):
        q = self.query.text().strip()
        if q:
            source = SOURCES[self.source.currentText()]
            self._run(source.search, q, MEDIA[self.media.currentText()])

    def _browse(self):
        path = QFileDialog.getExistingDirectory(self, "Scegli una cartella")
        if path:
            self.folder.setText(path)

    def _scan(self):
        if self.folder.text().strip():
            self._run(scan_folder, self.folder.text().strip())

    def _check_url(self):
        if self.url.text().strip():
            self._run(check_url, self.url.text())

    def _on_done(self, items):
        self.items = items
        self._refresh()
        self.info.setText(f"{len(items)} risultati.")

    def _on_failed(self, message):
        self.info.setText("Errore.")
        QMessageBox.warning(self, "Errore", message)

    def _refresh(self):
        use = self.use.currentData()
        self.table.setRowCount(len(self.items))
        for row, item in enumerate(self.items):
            evaluate(item, use)
            values = [item.status.value, item.title, item.origin, item.media_type,
                      item.license.name, item.author]
            for col, value in enumerate(values):
                cell = QTableWidgetItem(value)
                if col == 0:
                    cell.setBackground(QBrush(QColor(COLORS[item.status])))
                    dark = item.status is Status.TO_CHECK
                    cell.setForeground(QBrush(QColor("#000000" if dark else "#ffffff")))
                self.table.setItem(row, col, cell)
        self.table.resizeColumnsToContents()
        self.detail.clear()

    def _show_detail(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        i = self.items[rows[0].row()]
        e = html.escape

        def li(xs):
            return "".join(f"<li>{e(x)}</li>" for x in xs)

        link = (f'<a href="{e(i.location)}">{e(i.location)}</a>'
                if i.location.startswith("http") else e(i.location))
        self.detail.setHtml(
            f"<h3>{e(i.title)}</h3>"
            f"<p><b style='color:{COLORS[i.status]}'>{i.status.value}</b></p>"
            f"<ul>{li(i.reasons)}</ul>"
            f"<p><b>Licenza:</b> {e(i.license.name)}<br><b>Autore:</b> {e(i.author or '—')}<br>"
            f"<b>Posizione:</b> {link}<br><b>Evidenza:</b> {e(i.evidence or '—')}</p>"
            f"<p><b>Note</b></p><ul>{li(i.notes)}</ul>")

    def _export(self):
        if not self.items:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Esporta CSV", "reports/rapporto.csv",
                                              "CSV (*.csv)")
        if path:
            export_csv(self.items, path, self.use.currentText())
            self.info.setText(f"Esportato: {path}")
