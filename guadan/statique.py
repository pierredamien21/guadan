"""Analyse statique (cppcheck, clang-tidy) en phase B. Ses alertes ne sont jamais « prouvées »."""
import re
from dataclasses import dataclass
from pathlib import Path

from guadan import bac_a_sable

CPPCHECK = ("cppcheck --project=build/compile_commands.json --enable=warning,performance,portability "
            "--inline-suppr --quiet -j4 "
            "--template='{file}:{line}:{column}: [cppcheck/{id}] {severity}: {message}'")
# shortcut: contrôles limités aux familles qui visent des défauts ; à élargir si l'évaluation le justifie
CLANG_TIDY = ("run-clang-tidy -p build -quiet -j 4 "
              "-checks='-*,clang-analyzer-*,bugprone-*,-bugprone-easily-swappable-parameters' "
              "'^/travail/src/'")
LIGNE_CPPCHECK = re.compile(r"^(\S+?):(\d+):\d+: \[cppcheck/([\w-]+)\] (\w+): (.+)$")
LIGNE_TIDY = re.compile(r"^(\S+?):(\d+):\d+: (warning|error): (.+) \[([\w.,-]+)\]$")


@dataclass(frozen=True)
class Alerte:
    outil: str
    regle: str
    fichier: str
    ligne: int
    gravite: str
    message: str


def _dans_le_depot(chemin: str):
    for prefixe in ("/travail/src/", "src/"):
        if chemin.startswith(prefixe):
            return chemin[len(prefixe):]
    return None


def lire(sortie: str) -> list:
    alertes, vues = [], set()
    for l in sortie.splitlines():
        if m := LIGNE_CPPCHECK.match(l):
            chemin, ligne, regle, gravite, message, outil = *m.groups(), "cppcheck"
        elif m := LIGNE_TIDY.match(l):
            chemin, ligne, gravite, message, regle = m.groups()
            outil = "clang-tidy"
            if regle.startswith("clang-diagnostic"):  # erreur de configuration, pas une alerte
                continue
        else:
            continue
        fichier = _dans_le_depot(chemin)
        cle = (outil, regle, fichier, int(ligne))
        if fichier is None or cle in vues:
            continue
        vues.add(cle)
        alertes.append(Alerte(outil, regle, fichier, int(ligne), gravite, message))
    return alertes


def analyser(travail: Path) -> list:
    sortie = "".join(bac_a_sable.executer(travail, c, reseau=False).sortie + "\n"
                     for c in (CPPCHECK, CLANG_TIDY))
    return lire(sortie)
