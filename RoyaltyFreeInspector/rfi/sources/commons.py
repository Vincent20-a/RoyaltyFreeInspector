"""Ricerca su Wikimedia Commons tramite API MediaWiki."""
import requests
from bs4 import BeautifulSoup

from ..licenses import classify
from ..models import ContentItem
from .base import Source

API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "RoyaltyFreeInspector/0.1 (desktop app; licence checker)"}
FILETYPES = {"image": "bitmap", "graphic": "drawing", "audio": "audio", "video": "video"}
META_KEYS = "LicenseShortName|LicenseUrl|UsageTerms|Artist|Credit|AttributionRequired|Copyrighted"


def _text(html: str) -> str:
    return BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)


class CommonsSource(Source):
    name = "Wikimedia Commons"
    media_types = tuple(FILETYPES)

    def search(self, query, media_type, limit=20):
        params = {
            "action": "query", "format": "json", "generator": "search",
            "gsrnamespace": 6, "gsrlimit": limit,
            "gsrsearch": f"{query} filetype:{FILETYPES[media_type]}",
            "prop": "imageinfo", "iiprop": "url|extmetadata|mime",
            "iiextmetadatafilter": META_KEYS,
        }
        resp = requests.get(API, params=params, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        pages = resp.json().get("query", {}).get("pages", {})
        ordered = sorted(pages.values(), key=lambda p: p.get("index", 0))
        return [self._to_item(p, media_type) for p in ordered if p.get("imageinfo")]

    def _to_item(self, page, media_type):
        info = page["imageinfo"][0]
        meta = {k: v.get("value", "") for k, v in info.get("extmetadata", {}).items()}
        lic_text = meta.get("LicenseShortName") or meta.get("UsageTerms", "")
        lic = classify(lic_text, meta.get("LicenseUrl", ""))
        notes = ["I file di Commons possono includere diritti di terzi (marchi, persone, opere "
                 "riprodotte): controlla la pagina del file."]
        if meta.get("Copyrighted", "").lower() == "false" and not lic.known:
            notes.append("Segnalato come non protetto da copyright: verifica sulla pagina.")
        return ContentItem(
            title=page.get("title", "").removeprefix("File:"),
            origin=self.name,
            media_type=media_type,
            location=info.get("descriptionurl", info.get("url", "")),
            evidence=info.get("descriptionurl", ""),
            evidence_strong=lic.known,
            license=lic,
            license_raw=lic_text,
            author=_text(meta.get("Artist", "")) or _text(meta.get("Credit", "")),
            notes=notes,
        )
