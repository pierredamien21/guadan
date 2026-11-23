import json
from pathlib import Path

import pytest

from guadan import fuzz, pipeline
from tests.test_reparation import FauxLLM

RACINE = Path(__file__).resolve().parent.parent
HARNAIS = (RACINE / "tests" / "donnees" / "harnais_parseur.cpp").read_text()


def test_reponse_du_llm_lue_et_filtree():
    texte = json.dumps({"harnais": "int x;", "graines": ["M\u0003abc", "x" * 5000],
                        "dictionnaire": ["M", "a\"b", "\x00\x01", "y" * 200]})
    h, graines, dico = fuzz.lire_reponse("voici : " + texte)
    assert h == "int x;"
    assert graines == ["M\u0003abc"]          # graine trop longue écartée
    assert dico == ['"M"', '"a\\"b"', '"\\x00\\x01"']  # format libFuzzer, entrée trop longue écartée


def test_reponse_inexploitable():
    assert fuzz.lire_reponse("pas de json") == (None, [], [])


def verifier_constat(r):
    [p] = [p for p in r["prouves"] if p["categorie"] == "fuzzing"]
    assert (p["type"], p["fichier"], p["ligne"]) == ("stack-buffer-overflow", "parseur.cpp", 12)
    assert "cd fuzz && " in p["reproduction"] and "./fuzzer crash-" in p["reproduction"]
    assert r["resume"]["tests_echoues"] == 0  # les tests du projet passent, seul le fuzzing trouve


@pytest.mark.docker
def test_fuzzing_avec_harnais_fourni(tmp_path):
    h = tmp_path / "h.cpp"
    h.write_text(HARNAIS)
    r = pipeline.analyser(RACINE / "exemples" / "parseur-fragile", tmp_path / "s", harnais=h, fuzz_duree=60)
    verifier_constat(r)
    assert list((tmp_path / "s" / "travail" / "fuzz").glob("crash-*"))


@pytest.mark.docker
def test_fuzzing_avec_harnais_ecrit_par_le_llm(tmp_path):
    faux = FauxLLM(json.dumps({"harnais": HARNAIS, "graines": ["M\u0003abc"], "dictionnaire": ["M"]}))
    r = pipeline.analyser(RACINE / "exemples" / "parseur-fragile", tmp_path, client=faux, fuzz_duree=60)
    assert "parseur.h" in faux.questions[0]  # les en-têtes publics sont montrés au modèle
    verifier_constat(r)


def test_json_mal_echappe_par_le_modele_harnais_recupere():
    # vraie réponse de gpt-oss-120b : graines écrites \"...\" hors d'une chaîne, JSON invalide
    texte = (RACINE / "tests" / "donnees" / "reponse-harnais-json-invalide.txt").read_text()
    h, graines, dico = fuzz.lire_reponse(texte)
    assert "LLVMFuzzerTestOneInput" in h and '#include "parseur.h"' in h
    assert graines == [] and dico == []


def test_harnais_qui_redefinit_des_symboles_refuse():
    # extrait du vrai harnais de gpt-oss-120b pour muparser : bouchons OpenMP
    bouchons = '''extern "C" {
    int omp_get_max_threads() { return 1; }
    void __kmpc_fork_call(void *loc, int argc, void (*micro)(void *), ...) {}
}
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *d, size_t n) { return 0; }
'''
    assert fuzz.symboles_redefinis(bouchons) == ["__kmpc_fork_call", "omp_get_max_threads"]
    assert fuzz.symboles_redefinis(HARNAIS) == []
