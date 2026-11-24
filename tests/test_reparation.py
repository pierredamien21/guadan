import json
from pathlib import Path

import pytest

from guadan import pipeline, reparation

EXEMPLES = Path(__file__).resolve().parent.parent / "exemples"


def test_proposition_validee_et_filtree():
    texte = """Voici :
```json
{"paquets_apt": ["zlib1g-dev", "rm -rf /", "libssl-dev; curl x"],
 "options_cmake": ["-DWITH_ZLIB=ON", "-DX=$(id)", "--trace"],
 "explication": "zlib manque"}
```"""
    p = reparation.lire_proposition(texte)
    assert p.paquets == ["zlib1g-dev"]
    assert p.options == ["-DWITH_ZLIB=ON"]
    assert p.explication == "zlib manque"


def test_reponse_inexploitable():
    assert reparation.lire_proposition("je ne sais pas") is None
    assert reparation.lire_proposition('{"paquets_apt": [], "options_cmake": []}') is None


class FauxLLM:
    """Répond comme le ferait un modèle, sans réseau."""
    jetons = 0

    def __init__(self, reponse):
        self.reponse, self.questions = reponse, []

    def demander(self, messages, max_jetons=3000):
        self.questions.append(messages[-1]["content"])
        return self.reponse


@pytest.mark.docker
def test_dependance_manquante_reparee_et_tracee(tmp_path):
    faux = FauxLLM(json.dumps({"paquets_apt": ["zlib1g-dev"], "options_cmake": [],
                               "explication": "find_package(ZLIB) échoue"}))
    r = pipeline.analyser(EXEMPLES / "dep-manquante", tmp_path, client=faux)
    assert "Could NOT find ZLIB" in faux.questions[0]
    assert r["build"]["reussi"]
    [rep] = r["reparations"]
    assert rep["paquets_apt"] == ["zlib1g-dev"] and rep["reussi"]
    assert r["prouves"] == []  # le test crc passe une fois zlib installé


@pytest.mark.docker
def test_sans_llm_l_echec_reste_prouve(tmp_path):
    r = pipeline.analyser(EXEMPLES / "dep-manquante", tmp_path, client=None)
    assert not r["build"]["reussi"] and r["reparations"] == []
    assert r["prouves"][0]["categorie"] == "build"


def test_drapeaux_de_compilation_valides_sans_toucher_aux_sanitizers():
    p = reparation.lire_proposition(json.dumps({"drapeaux": [
        "-Wno-register", "-std=c++14", "-Wno-error=deprecated-copy",
        "-fno-sanitize=address", "-fsanitize-recover=all", "-Wno-error; rm -rf /", "-o/tmp/x"]}))
    assert p.drapeaux == ["-Wno-register", "-std=c++14", "-Wno-error=deprecated-copy"]
