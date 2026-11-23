"""Lecture des rapports AddressSanitizer et UndefinedBehaviorSanitizer dans une sortie de test."""
import re
from dataclasses import dataclass, field

PREFIXE = "/travail/src/"  # chemin du dépôt dans le conteneur
ASAN = re.compile(r"ERROR: AddressSanitizer: ([\w-]+)")
UBSAN = re.compile(r"(\S+?):(\d+):\d+: runtime error: (.+)$")
CADRE = re.compile(r"^\s*#\d+ 0x[0-9a-f]+ in (.+?) (/\S+?):(\d+)(?::\d+)?\s*$")


@dataclass
class Rapport:
    outil: str          # « ASan » ou « UBSan »
    type: str           # ex. heap-buffer-overflow, signed integer overflow
    fichier: str        # relatif au dépôt quand c'est possible
    ligne: int
    fonction: str = ""
    message: str = ""
    pile: list = field(default_factory=list)  # « fichier:ligne fonction », cadres du projet seulement


def _relatif(chemin: str) -> str:
    return chemin[len(PREFIXE):] if chemin.startswith(PREFIXE) else chemin


def _du_projet(chemin: str) -> bool:
    return not chemin.startswith(("/usr/", "/lib/")) and "compiler-rt" not in chemin


def _premiere_pile(lignes):
    """Cadres de la première pile (l'accès fautif), pas celle de l'allocation qui suit."""
    cadres, commence = [], False
    for l in lignes:
        if l.strip().startswith("#"):
            commence = True
            m = CADRE.match(l)
            if m and _du_projet(m.group(2)):
                cadres.append((_relatif(m.group(2)), int(m.group(3)), m.group(1)))
        elif commence:
            break
    return cadres


def lire(texte: str) -> list:
    lignes = texte.splitlines()
    rapports = []
    for i, l in enumerate(lignes):
        if m := ASAN.search(l):
            cadres = _premiere_pile(lignes[i + 1:])
            fichier, ligne, fonction = cadres[0] if cadres else ("", 0, "")
            rapports.append(Rapport("ASan", m.group(1), fichier, ligne, fonction, l.strip(),
                                    [f"{f}:{n} {fn}" for f, n, fn in cadres]))
        elif m := UBSAN.search(l):
            message = m.group(3).strip()
            rapports.append(Rapport("UBSan", message.split(":")[0], _relatif(m.group(1)),
                                    int(m.group(2)), message=message,
                                    pile=[f"{_relatif(m.group(1))}:{m.group(2)}"]))
    return rapports
