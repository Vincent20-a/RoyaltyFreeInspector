"""Verifica di un URL: cerca la licenza dichiarata dalla pagina."""
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .licenses import classify
from .models import UNKNOWN, ContentItem

HEADERS = {"User-Agent": "RoyaltyFreeInspector/0.1 (desktop app; licence checker)"}


def check_url(url: str) -> list[ContentItem]:
    url = url.strip()
    if not re.match(r"https?://", url, re.I):
        url = "https://" + url
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    href = None
    for tag in soup.find_all(["a", "link"], rel=True):
        rel = tag["rel"] if isinstance(tag["rel"], list) else [tag["rel"]]
        if "license" in [r.lower() for r in rel] and tag.get("href"):
            href = urljoin(resp.url, tag["href"])
            break

    lic = classify(url=href) if href else UNKNOWN
    notes = ["Licenza dichiarata dalla pagina: non prova la titolarità dei diritti."]
    if not href:
        notes.append('Nessun collegamento rel="license" trovato nella pagina.')
    title = soup.title.get_text(strip=True) if soup.title else resp.url
    return [ContentItem(
        title=title, origin="URL", media_type="other", location=resp.url,
        evidence=href or "", evidence_strong=False, license=lic,
        license_raw=href or "", notes=notes)]
