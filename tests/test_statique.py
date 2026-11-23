from pathlib import Path

import pytest

from guadan import bac_a_sable, build, statique

EXEMPLES = Path(__file__).resolve().parent.parent / "exemples"

# sorties réelles de cppcheck 2.13 et clang-tidy 18 sur exemples/alertes
CPPCHECK = ("src/alertes.cpp:4:13: [cppcheck/arrayIndexOutOfBounds] error: Array 't[3]' accessed "
            "at index 3, which is out of bounds.\n")
CLANG_TIDY = ("/travail/src/alertes.cpp:8:12: warning: result of integer division used in a floating "
              "point context; possible loss of precision [bugprone-integer-division]\n"
              "/travail/build/genere.cpp:1:1: warning: hors du dépôt [bugprone-xyz]\n"
              "/travail/src/a.cpp:1:10: error: 'omp.h' file not found [clang-diagnostic-error]\n")


def test_lecture_cppcheck_et_clang_tidy_chemins_relatifs_au_depot():
    alertes = statique.lire(CPPCHECK + CLANG_TIDY)
    assert [(a.outil, a.regle, a.fichier, a.ligne) for a in alertes] == [
        ("cppcheck", "arrayIndexOutOfBounds", "alertes.cpp", 4),
        ("clang-tidy", "bugprone-integer-division", "alertes.cpp", 8),
    ]  # fichiers hors de src/ et erreurs de configuration de clang-tidy écartés


def test_doublons_retires():
    assert len(statique.lire(CPPCHECK + CPPCHECK)) == 1


@pytest.mark.docker
def test_exemple_alertes(tmp_path):
    bac_a_sable.copier(EXEMPLES / "alertes", tmp_path)
    assert build.construire(tmp_path).reussi
    cles = {(a.regle, a.fichier, a.ligne) for a in statique.analyser(tmp_path)}
    assert ("arrayIndexOutOfBounds", "alertes.cpp", 4) in cles
    assert ("bugprone-integer-division", "alertes.cpp", 8) in cles
