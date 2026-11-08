"""Analisi di cartelle locali: documenti di licenza, sidecar .license e metadati XMP."""
import re
from pathlib import Path

from .licenses import classify
from .models import UNKNOWN, ContentItem

EXTENSIONS = {
    "image": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff", ".svg"},
    "audio": {".mp3", ".wav", ".flac", ".ogg", ".m4a"},
    "video": {".mp4", ".mov", ".mkv", ".avi", ".webm"},
    "font": {".ttf", ".otf", ".woff", ".woff2"},
}
LICENSE_PREFIXES = ("license", "licence", "copying", "unlicense")
XMP_URL = re.compile(rb'cc:license[^>]*?rdf:resource="([^"]+)"', re.I)
XMP_STATEMENT = re.compile(rb"xmpRights:WebStatement[^>]*>\s*([^<\s][^<]*)<", re.I)


def _read(path: Path, limit=200_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""


def _media_type(path: Path):
    ext = path.suffix.lower()
    return next((t for t, exts in EXTENSIONS.items() if ext in exts), None)


def _license_doc(directory: Path):
    try:
        return next((f for f in sorted(directory.iterdir())
                     if f.is_file() and f.stem.lower().startswith(LICENSE_PREFIXES)), None)
    except OSError:
        return None


def _folder_license(directory: Path, root: Path, cache: dict):
    """Cerca un documento di licenza risalendo dalla cartella del file fino alla radice."""
    for d in [directory, *directory.parents]:
        if d not in cache:
            cache[d] = _license_doc(d)
        if cache[d]:
            return cache[d]
        if d == root:
            break
    return None


def _embedded_xmp(path: Path):
    if path.suffix.lower() not in EXTENSIONS["image"]:
        return UNKNOWN, ""
    try:
        with path.open("rb") as fh:
            chunk = fh.read(512_000)
    except OSError:
        return UNKNOWN, ""
    found = XMP_URL.search(chunk) or XMP_STATEMENT.search(chunk)
    if not found:
        return UNKNOWN, ""
    raw = found.group(1).decode("utf-8", errors="ignore").strip()
    return classify(url=raw), raw


def scan_folder(folder: str) -> list[ContentItem]:
    root = Path(folder).resolve()
    cache: dict = {}
    items = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        mtype = _media_type(path)
        if not mtype:
            continue
        notes = ["Rilevamento locale euristico: confronta sempre con la fonte originale."]
        sidecar = path.with_name(path.name + ".license")

        lic, raw = _embedded_xmp(path)
        evidence, strong = (f"Metadati XMP in {path.name}", True) if lic.known else ("", False)

        if not lic.known and sidecar.exists():
            raw = _read(sidecar)
            lic = classify(raw)
            evidence, strong = (str(sidecar), True) if lic.known else ("", False)

        if not lic.known:
            doc = _folder_license(path.parent, root, cache)
            if doc:
                raw = _read(doc)
                lic = classify(raw)
                if lic.known:
                    evidence, strong = str(doc), False
                    notes.append("La licenza viene da un documento di cartella: potrebbe non "
                                 "riguardare questo file.")
        if not lic.known:
            notes.append("Nessuna licenza associata: il risultato è 'sconosciuto', non royalty-free.")

        items.append(ContentItem(
            title=path.name, origin="File locale", media_type=mtype, location=str(path),
            evidence=evidence, evidence_strong=strong, license=lic,
            license_raw=raw[:200].replace("\n", " "), notes=notes))
    return items
