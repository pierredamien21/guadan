"""Lecture des rapports AddressSanitizer et UndefinedBehaviorSanitizer dans une sortie de test."""
import posixpath
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
    chemin = posixpath.normpath(chemin)  # /travail/src/test/../peglib.h -> /travail/src/peglib.h
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
            fichier, ligne, fonction = _relatif(m.group(1)), int(m.group(2)), ""
            cadres = _premiere_pile(lignes[i + 1:])
            if not _du_projet(m.group(1)) and cadres:  # erreur dans un en-tête système : remonter au projet
                fichier, ligne, fonction = cadres[0]
            type_ = re.split(r": | of type '", message)[0]
            rapports.append(Rapport("UBSan", type_, fichier, ligne, fonction, message,
                                    [f"{f}:{n} {fn}" for f, n, fn in cadres] or [f"{fichier}:{ligne}"]))
    return rapports
