"""Lecture de vrais rapports ASan/UBSan capturés (tests/donnees). Les valeurs attendues ont été
relevées à la main dans ces fichiers et dans le code des exemples (ligne marquée DEFAUT)."""
from pathlib import Path

from guadan import sanitizer

DONNEES = Path(__file__).parent / "donnees"


def lire(nom):
    return sanitizer.lire((DONNEES / nom).read_text())


def test_asan_designe_la_ligne_fautive_du_projet_pas_le_runtime():
    [r] = lire("debordement-tas.txt")
    assert (r.outil, r.type) == ("ASan", "heap-buffer-overflow")
    assert (r.fichier, r.ligne) == ("texte.cpp", 8)  # memcpy, pas __asan_memcpy ni l'allocation (ligne 7)
    assert r.fonction == "copie(char const*)"
    assert r.pile[0].startswith("texte.cpp:8")


def test_ubsan_signed_overflow():
    [r] = lire("ub-entier.txt")
    assert (r.outil, r.type) == ("UBSan", "signed integer overflow")
    assert (r.fichier, r.ligne) == ("calcul.cpp", 3)


def test_rapport_arvo_hors_dossier_de_travail_garde_le_chemin_absolu():
    [r] = lire("arvo-25402.txt")
    assert r.type == "heap-buffer-overflow"
    assert r.fichier.endswith("src/muParserBase.cpp") and r.ligne == 1242


def test_sortie_sans_rapport():
    assert sanitizer.lire("100% tests passed, 0 tests failed out of 1\n") == []


def test_ubsan_dans_un_en_tete_systeme_remonte_au_code_du_projet():
    # vrai rapport (cpp_peglib-2, évaluation) : l'erreur est dans stl_vector.h, la cause dans peglib.h,
    # dont le chemin est écrit /travail/src/test/../peglib.h
    [r] = lire("ubsan-peglib.txt")
    assert (r.outil, r.fichier, r.ligne) == ("UBSan", "peglib.h", 2843)
    assert r.type == "reference binding to null pointer"
