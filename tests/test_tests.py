from pathlib import Path

import pytest

from guadan import bac_a_sable, build, tests as tests_projet

pytestmark = pytest.mark.docker
EXEMPLES = Path(__file__).resolve().parent.parent / "exemples"


def lancer(nom, tmp_path):
    bac_a_sable.copier(EXEMPLES / nom, tmp_path)
    assert build.construire(tmp_path).reussi
    return {t.nom: t for t in tests_projet.lancer(tmp_path)}


def test_exemple_sain_tous_les_tests_passent(tmp_path):
    t = lancer("sain", tmp_path)
    assert set(t) == {"somme"}
    assert t["somme"].statut == "réussi"


def test_debordement_rattache_le_rapport_asan_au_bon_test(tmp_path):
    t = lancer("debordement-tas", tmp_path)
    assert t["copie_courte"].statut == "réussi"
    echec = t["copie_longue"]
    assert echec.statut == "échoué" and echec.categorie == "sanitizer"
    [r] = echec.rapports
    assert (r.type, r.fichier, r.ligne) == ("heap-buffer-overflow", "texte.cpp", 8)
    assert "ctest" in echec.reproduction and "^copie_longue$" in echec.reproduction


def test_ubsan_fait_echouer_le_test(tmp_path):
    t = lancer("ub-entier", tmp_path)
    assert t["moyenne_grands"].categorie == "sanitizer"
    assert t["moyenne_grands"].rapports[0].fichier == "calcul.cpp"
