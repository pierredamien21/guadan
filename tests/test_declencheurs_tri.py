"""T12 (tests déclencheurs, tentative bornée) et T13 (tri expliqué des alertes)."""
import json
from pathlib import Path

import pytest

from guadan import declencheurs, pipeline, rapport, tri
from guadan.build import Build
from guadan.sanitizer import Rapport
from guadan.statique import Alerte

EXEMPLES = Path(__file__).resolve().parent.parent / "exemples"
A_HORS = Alerte("cppcheck", "arrayIndexOutOfBounds", "alertes.cpp", 4, "error", "hors limites")
A_DIV = Alerte("clang-tidy", "bugprone-integer-division", "alertes.cpp", 8, "warning", "division")


def test_preuve_seulement_si_le_rapport_pointe_la_ligne_de_l_alerte():
    bon = Rapport("ASan", "stack-buffer-overflow", "alertes.cpp", 4, pile=["alertes.cpp:4 dernier()"])
    ailleurs = Rapport("ASan", "heap-use-after-free", "autre.cpp", 9, pile=["autre.cpp:9 f()", "alertes.cpp:40 g()"])
    assert declencheurs.prouve([bon], A_HORS)
    assert not declencheurs.prouve([ailleurs], A_HORS)
    assert not declencheurs.prouve([], A_HORS)


def test_ordre_les_erreurs_d_abord():
    assert declencheurs.choisir([A_DIV, A_HORS], 1) == [A_HORS]


def test_tri_lu_et_valide():
    texte = json.dumps([{"id": 0, "etiquette": "à vérifier", "raison": "indice constant 3"},
                        {"id": 1, "etiquette": "n'importe quoi", "raison": "x"},
                        {"id": 7, "etiquette": "probable fausse alerte", "raison": "id inconnu"}])
    assert tri.lire(texte, 2) == {0: {"etiquette": "à vérifier", "raison": "indice constant 3"}}


def test_le_tri_ne_change_jamais_le_niveau():
    b = Build(True, "compilation", "c", "", "r")
    r = rapport.construire("d", b, [], [A_HORS], tri={0: {"etiquette": "à vérifier", "raison": "x"}})
    assert r["prouves"] == [] and r["non_prouves"][0]["tri"]["etiquette"] == "à vérifier"


class LLMParAlerte:
    """Faux modèle : écrit un vrai déclencheur pour l'indice hors limites, refuse la division,
    et trie les alertes."""
    jetons, modele = 0, "faux"

    def demander(self, messages, max_jetons=3000):
        q = messages[-1]["content"]
        if "Classify each static-analysis alert" in q:
            return json.dumps([{"id": 0, "etiquette": "à vérifier", "raison": "t[3] sur un tableau de 3"}])
        if "arrayIndexOutOfBounds" in q:
            return "```cpp\nint dernier();\nint main() { return dernier() == 42; }\n```"
        return "UNTRIGGERABLE integer division is not a memory error"


@pytest.mark.docker
def test_alerte_prouvee_par_un_declencheur_et_tri(tmp_path):
    r = pipeline.analyser(EXEMPLES / "alertes", tmp_path, client=LLMParAlerte(), declencheurs_max=3)
    [p] = r["prouves"]
    assert (p["categorie"], p["fichier"], p["ligne"]) == ("déclencheur", "alertes.cpp", 4)
    etats = {a["ligne"]: a.get("declencheur") for a in r["non_prouves"]}
    assert etats[4] == "prouvé" and etats[8] == "refusé par le modèle"
    assert any(a.get("tri") for a in r["non_prouves"])
