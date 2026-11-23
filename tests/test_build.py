from pathlib import Path

import pytest

from guadan import bac_a_sable, build

pytestmark = pytest.mark.docker
EXEMPLES = Path(__file__).resolve().parent.parent / "exemples"


def construire(nom, tmp_path):
    bac_a_sable.copier(EXEMPLES / nom, tmp_path)
    return build.construire(tmp_path)


def test_exemple_sain_se_construit_avec_base_de_compilation(tmp_path):
    r = construire("sain", tmp_path)
    assert r.reussi, r.sortie
    assert (tmp_path / "build" / "compile_commands.json").exists()
    assert "-fsanitize=address,undefined" in (tmp_path / "build" / "compile_commands.json").read_text()


def test_dependance_manquante_echoue_a_la_configuration(tmp_path):
    r = construire("dep-manquante", tmp_path)
    assert not r.reussi
    assert r.etape == "configuration"
    assert "Could NOT find ZLIB" in r.sortie
    assert "docker run" in r.reproduction and "cmake -S src -B build" in r.reproduction
