"""La règle centrale (D-02) : seul ce qui a été observé à l'exécution est « prouvé »."""
import json

from guadan import rapport
from guadan.build import Build
from guadan.sanitizer import Rapport
from guadan.statique import Alerte
from guadan.tests import ResultatTest

BUILD_OK = Build(True, "compilation", "cmake --build build", "", "docker run ...")
ALERTE = Alerte("cppcheck", "arrayIndexOutOfBounds", "a.cpp", 4, "error", "hors limites")
ASAN = Rapport("ASan", "heap-buffer-overflow", "texte.cpp", 8, "copie(char const*)")


def test_une_alerte_n_est_jamais_prouvee():
    r = rapport.construire("depot", BUILD_OK, [ResultatTest("t", "réussi")], [ALERTE])
    assert r["prouves"] == []
    assert r["non_prouves"][0]["regle"] == "arrayIndexOutOfBounds"


def test_test_echoue_sous_sanitizer_est_prouve_avec_sa_commande():
    t = ResultatTest("copie_longue", "échoué", "sanitizer", "==1==ERROR: AddressSanitizer: ...",
                     [ASAN], "docker run ... ctest -R '^copie_longue$'")
    r = rapport.construire("depot", BUILD_OK, [t], [ALERTE])
    [p] = r["prouves"]
    assert (p["type"], p["fichier"], p["ligne"], p["test"]) == ("heap-buffer-overflow", "texte.cpp", 8, "copie_longue")
    assert "ctest -R" in p["reproduction"] and "AddressSanitizer" in p["preuve"]
    assert r["resume"] == {"tests": 1, "tests_echoues": 1, "plantages_fuzzing": 0, "prouves": 1, "non_prouves": 1}


def test_echec_de_build_est_prouve_et_rien_d_autre():
    b = Build(False, "configuration", "cmake -S src", "Could NOT find ZLIB", "docker run ... cmake")
    r = rapport.construire("depot", b, [], [])
    assert [p["type"] for p in r["prouves"]] == ["échec de configuration"]


def test_html_echappe_les_sorties_non_fiables(tmp_path):
    t = ResultatTest("x", "échoué", "échec", "<script>alert(1)</script>", [], "cmd")
    r = rapport.construire("depot", BUILD_OK, [t], [])
    rapport.ecrire(r, tmp_path)
    page = (tmp_path / "rapport.html").read_text()
    assert "<script>alert(1)</script>" not in page and "&lt;script&gt;" in page
    assert json.loads((tmp_path / "rapport.json").read_text())["depot"] == "depot"


def test_build_en_echec_annonce_des_tests_non_lances(tmp_path):
    b = Build(False, "configuration", "cmake -S src", "Could NOT find ZLIB", "docker run ...")
    rapport.ecrire(rapport.construire("depot", b, [], []), tmp_path)
    page = (tmp_path / "rapport.html").read_text()
    assert "tests non lancés" in page and "0 / 0" not in page
