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


def test_werror_du_projet_neutralise_mais_code_ancien_refuse(tmp_path):
    r = construire("vieux-code", tmp_path)
    assert not r.reussi and r.etape == "compilation"
    assert "does not allow 'register'" in r.sortie
    assert "error: unused variable" not in r.sortie  # le -Werror du projet ne bloque plus


def test_drapeau_declare_repare_le_code_ancien(tmp_path):
    bac_a_sable.copier(EXEMPLES / "vieux-code", tmp_path)
    r = build.construire(tmp_path, drapeaux=["-Wno-register"])
    assert r.reussi, r.sortie[-1500:]
