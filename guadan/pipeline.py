"""Enchaînement : copie, build, tests, analyse statique, rapport."""
from pathlib import Path

from guadan import bac_a_sable, build, rapport, statique, tests


def analyser(depot: Path, sortie: Path) -> dict:
    depot, sortie = Path(depot).resolve(), Path(sortie).resolve()
    travail = sortie / "travail"
    bac_a_sable.copier(depot, travail)
    b = build.construire(travail)
    resultats = tests.lancer(travail) if b.reussi else []
    alertes = statique.analyser(travail) if b.reussi else []
    r = rapport.construire(depot.name, b, resultats, alertes)
    rapport.ecrire(r, sortie)
    return r
