"""Regole che assegnano lo stato. Il default è sempre 'Da verificare'."""
from .licenses import conditions
from .models import ContentItem, Status

COMMERCIAL = "commercial"
NON_COMMERCIAL = "non_commercial"


def evaluate(item: ContentItem, use: str = COMMERCIAL) -> ContentItem:
    lic = item.license
    reasons = []

    if not lic.known:
        status = Status.TO_CHECK
        reasons.append("Licenza non identificata: l'assenza di informazioni non è un via libera")
    elif use == COMMERCIAL and lic.commercial_use is False:
        status = Status.NOT_AUTHORIZED
        reasons.append("La licenza vieta l'uso commerciale")
    elif not item.evidence:
        status = Status.TO_CHECK
        reasons.append("Fonte della licenza non documentata")
    elif not item.evidence_strong:
        status = Status.TO_CHECK
        reasons.append("Licenza solo dichiarata: non è provato che l'autore sia titolare dei diritti")
    else:
        status = Status.VERIFIED
        reasons.append("Licenza e fonte documentate")

    reasons.extend(conditions(lic))
    item.status = status
    item.reasons = reasons
    return item
