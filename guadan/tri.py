"""Tri expliqué des alertes non prouvées (D-10), en un seul appel groupé. L'étiquette aide à lire
le rapport ; elle ne change jamais le niveau d'une alerte."""
import json
import re
from pathlib import Path

from guadan import llm

ETIQUETTES = ("probable fausse alerte", "à vérifier")
MAX_ALERTES = 40
CONSIGNE = """Classify each static-analysis alert of a C/C++ project. For each one, say whether it is
"probable fausse alerte" (false positive, intended design, or unreachable) or "à vérifier" (could be
a real defect), with a one-sentence reason in French based on the code shown. Reply with JSON only:
[{{"id": 0, "etiquette": "à vérifier", "raison": "..."}}]

ALERTS:
{alertes}"""


def lire(texte: str, n: int) -> dict:
    m = re.search(r"\[.*\]", texte, re.S)
    try:
        liste = json.loads(m.group(0)) if m else []
    except json.JSONDecodeError:
        return {}
    tri = {}
    for x in liste if isinstance(liste, list) else []:
        if (isinstance(x, dict) and isinstance(x.get("id"), int) and 0 <= x["id"] < n
                and x.get("etiquette") in ETIQUETTES):
            tri[x["id"]] = {"etiquette": x["etiquette"], "raison": str(x.get("raison", ""))[:300]}
    return tri


def trier(src: Path, alertes: list, client) -> dict:
    """Rend {indice de l'alerte: {etiquette, raison}} pour les MAX_ALERTES premières."""
    blocs = []
    for i, a in enumerate(alertes[:MAX_ALERTES]):
        try:
            lignes = (Path(src) / a.fichier).read_text(errors="replace").splitlines()
        except OSError:
            lignes = []
        code = "\n".join(f"{n:5} {lignes[n - 1]}" for n in range(max(1, a.ligne - 3), min(len(lignes), a.ligne + 3) + 1))
        blocs.append(f"id {i}: {a.fichier}:{a.ligne} [{a.outil}/{a.regle}] {a.message}\n{code}")
    if not blocs:
        return {}
    question = CONSIGNE.format(alertes=llm.tronquer("\n\n".join(blocs), 16_000))
    try:
        return lire(client.demander([{"role": "user", "content": question}], 4000), len(blocs))
    except llm.ErreurLLM:
        return {}
