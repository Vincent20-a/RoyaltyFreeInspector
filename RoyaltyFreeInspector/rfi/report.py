"""Esportazione dei risultati."""
import csv
from datetime import datetime

from .licenses import conditions

COLUMNS = ["Stato", "Motivazioni", "Titolo", "Origine", "Tipo", "Posizione", "Evidenza",
           "Licenza", "Autore", "Condizioni", "Uso richiesto", "Data verifica"]


def export_csv(items, path: str, use_label: str) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh, delimiter=";")
        writer.writerow(COLUMNS)
        for i in items:
            writer.writerow([
                i.status.value, " | ".join(i.reasons), i.title, i.origin, i.media_type,
                i.location, i.evidence, i.license.name, i.author,
                " | ".join(conditions(i.license)), use_label, now])
