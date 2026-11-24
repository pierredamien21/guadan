"""Enchaînement : copie, build (avec réparation éventuelle), tests, analyse statique, fuzzing,
LLM facultatif, rapport."""
from pathlib import Path

from guadan import bac_a_sable, build, declencheurs, fuzz, rapport, reparation, statique, tests, tri

ESSAIS_REPARATION = 2
ETAPES = ("configuration", "compilation")


def analyser(depot: Path, sortie: Path, client=None, apt=(), harnais=None, fuzz_duree: int = 0,
             declencheurs_max: int = 0, drapeaux=(), trier: bool = True) -> dict:
    depot, sortie = Path(depot).resolve(), Path(sortie).resolve()
    travail = sortie / "travail"
    src = bac_a_sable.copier(depot, travail)
    paquets, options, drapeaux, reparations = list(apt), [], list(drapeaux), []

    image, journal = bac_a_sable.image_avec(paquets)
    if image is None:
        raise SystemExit(f"guadan: installation des paquets demandés impossible :\n{journal[-1500:]}")
    b = build.construire(travail, image, options, drapeaux)

    while not b.reussi and client and len(reparations) < ESSAIS_REPARATION:
        cmakelists = (src / "CMakeLists.txt").read_text(errors="replace")
        prop, erreur = reparation.proposer(client, b.sortie, cmakelists, b.etape)
        if prop is None:
            reparations.append({"etape": b.etape, "paquets_apt": [], "options_cmake": [], "drapeaux": [],
                                "reussi": False, "explication": erreur or "aucune proposition exploitable"})
            break
        nouvelle, journal = bac_a_sable.image_avec(paquets + prop.paquets)
        entree = {"etape": b.etape, "paquets_apt": prop.paquets, "options_cmake": prop.options,
                  "drapeaux": prop.drapeaux}
        if nouvelle is None:
            reparations.append({**entree, "reussi": False,
                                "explication": f"{prop.explication} (installation impossible)"})
            break
        etape_avant = ETAPES.index(b.etape)
        image, paquets = nouvelle, paquets + prop.paquets
        options, drapeaux = options + prop.options, drapeaux + prop.drapeaux
        b = build.construire(travail, image, options, drapeaux)
        reparations.append({**entree, "explication": prop.explication,
                            "reussi": b.reussi or ETAPES.index(b.etape) > etape_avant})

    resultats = tests.lancer(travail, image=image) if b.reussi else []
    alertes = statique.analyser(travail, image=image) if b.reussi else []
    plantages, journal_fuzz = [], None
    if b.reussi and fuzz_duree > 0 and (harnais or client):
        plantages, journal_fuzz = fuzz.lancer(travail, image, options, harnais, client, fuzz_duree)
    tri_alertes, etats = {}, {}
    if client is not None and alertes:
        if trier:
            tri_alertes = tri.trier(travail / "src", alertes, client)
        if declencheurs_max > 0:
            prouves, etats = declencheurs.tenter(travail, image, alertes, client, declencheurs_max, options)
            plantages += prouves
    r = rapport.construire(depot.name, b, resultats, alertes, reparations, plantages, tri_alertes, etats)
    r["build"]["drapeaux"] = drapeaux
    r["fuzzing"] = journal_fuzz
    if client is not None:
        r["llm"] = {"modele": getattr(client, "modele", "?"), "jetons": client.jetons}
    rapport.ecrire(r, sortie)
    return r
