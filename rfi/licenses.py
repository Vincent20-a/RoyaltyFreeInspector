"""Classificazione euristica delle licenze a partire da testo o URL."""
import re

from .models import UNKNOWN, LicenseInfo

# (regex, nome, uso commerciale, attribuzione, share-alike, no-derivate)
# L'ordine conta: le varianti più specifiche vanno prima.
_RULES = [
    (r"\bcc0\b|creative commons zero|publicdomain/zero", "CC0", True, False, False, False),
    (r"public domain|publicdomain/mark|\bpdm\b", "Pubblico dominio", True, False, False, False),
    (r"by-nc-nd|noncommercial-noderiv", "CC BY-NC-ND", False, True, False, True),
    (r"by-nc-sa|noncommercial-sharealike", "CC BY-NC-SA", False, True, True, False),
    (r"by-nc|noncommercial", "CC BY-NC", False, True, False, False),
    (r"by-nd|noderiv", "CC BY-ND", True, True, False, True),
    (r"by-sa|sharealike", "CC BY-SA", True, True, True, False),
    (r"\bcc[ -]by\b|licenses/by/|creative commons attribution", "CC BY", True, True, False, False),
    (r"sil open font|\bofl\b", "SIL OFL", True, True, False, False),
    (r"apache license|apache-2", "Apache-2.0", True, True, False, False),
    (r"\bmit license\b|\bmit\b", "MIT", True, True, False, False),
    (r"gnu general public license|\bgpl\b", "GPL", True, True, True, False),
]


def classify(text: str = "", url: str = "") -> LicenseInfo:
    """Restituisce la licenza riconosciuta, o UNKNOWN. Mai un'ipotesi ottimistica."""
    haystack = f"{text} {url}".lower().strip()
    if not haystack:
        return UNKNOWN
    for pattern, name, commercial, attribution, sa, nd in _RULES:
        if re.search(pattern, haystack):
            version = re.search(r"\b(\d\.\d)\b", haystack)
            if version and name.startswith("CC") and name != "CC0":
                name = f"{name} {version.group(1)}"
            return LicenseInfo(name, True, commercial, attribution, sa, nd)
    return UNKNOWN


def conditions(lic: LicenseInfo) -> list:
    """Condizioni d'uso in chiaro, da mostrare all'utente."""
    out = []
    if lic.attribution:
        out.append("Richiede attribuzione all'autore")
    if lic.share_alike:
        out.append("Le opere derivate vanno rilasciate con la stessa licenza")
    if lic.no_derivatives:
        out.append("Vietate modifiche e opere derivate")
    if lic.commercial_use is False:
        out.append("Vietato l'uso commerciale")
    return out
