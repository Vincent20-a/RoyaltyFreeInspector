"""Modelli dati condivisi da tutti i moduli."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Status(Enum):
    VERIFIED = "Verificato"
    TO_CHECK = "Da verificare"
    NOT_AUTHORIZED = "Non autorizzato"


@dataclass(frozen=True)
class LicenseInfo:
    name: str = "Sconosciuta"
    known: bool = False
    commercial_use: Optional[bool] = None  # None = non noto
    attribution: bool = False
    share_alike: bool = False
    no_derivatives: bool = False


UNKNOWN = LicenseInfo()


@dataclass
class ContentItem:
    title: str
    origin: str            # "Wikimedia Commons", "File locale", "URL"
    media_type: str        # image, audio, video, graphic, font, other
    location: str          # URL o percorso del file
    evidence: str = ""     # dove è stata trovata la licenza (pagina, file, XMP)
    evidence_strong: bool = False  # True solo se la prova riguarda proprio questo contenuto
    license: LicenseInfo = UNKNOWN
    license_raw: str = ""
    author: str = ""
    notes: list = field(default_factory=list)
    status: Status = Status.TO_CHECK
    reasons: list = field(default_factory=list)
