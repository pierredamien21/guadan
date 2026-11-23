"""Tests du projet (ctest) sous sanitizers, en phase B, avec un résultat par test."""
import shlex
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from guadan import bac_a_sable, sanitizer
from guadan.build import reproduction

# detect_leaks=0 : beaucoup de suites de tests fuient volontairement ; les fuites ne sont pas suivies
ENV = "ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=print_stacktrace=1"
STATUTS = {"run": "réussi", "fail": "échoué", "notrun": "non lancé", "disabled": "désactivé"}


@dataclass
class ResultatTest:
    nom: str
    statut: str          # réussi, échoué, non lancé, désactivé
    categorie: str = ""  # pour un échec : sanitizer, plantage, délai dépassé, échec
    sortie: str = ""
    rapports: list = field(default_factory=list)
    reproduction: str = ""


def _categorie(message: str, rapports) -> str:
    if rapports:
        return "sanitizer"
    if "Timeout" in message:
        return "délai dépassé"
    if any(s in message for s in ("SEGFAULT", "Exception", "Child aborted", "BAD_COMMAND")):
        return "plantage"
    return "échec"


def lancer(travail: Path, duree_test_s: int = 300, image: str = bac_a_sable.IMAGE) -> list:
    xml = Path(travail) / "ctest.xml"
    xml.unlink(missing_ok=True)
    bac_a_sable.executer(travail, f"{ENV} ctest --test-dir build --output-junit /travail/ctest.xml "
                                  f"--timeout {duree_test_s} -j4", reseau=False, image=image)
    if not xml.exists():  # aucun test déclaré : ctest n'écrit rien
        return []
    contenu = xml.read_text(errors="replace")
    # le fichier vient d'un conteneur où tourne du code non fiable : pas de DTD ni d'entités
    if "<!DOCTYPE" in contenu or "<!ENTITY" in contenu:
        raise ValueError("ctest.xml contient une DTD : refusé")
    resultats = []
    for cas in ET.fromstring(contenu).iter("testcase"):
        nom, sortie = cas.get("name"), cas.findtext("system-out") or ""
        statut = STATUTS.get(cas.get("status"), cas.get("status"))
        r = ResultatTest(nom, statut, sortie=sortie)
        if statut == "échoué":
            echec = cas.find("failure")
            r.rapports = sanitizer.lire(sortie)
            r.categorie = _categorie(echec.get("message", "") if echec is not None else "", r.rapports)
            r.reproduction = reproduction(travail, f"{ENV} ctest --test-dir build -R {shlex.quote('^' + nom + '$')} "
                                                   "--output-on-failure", image)
        resultats.append(r)
    return resultats
