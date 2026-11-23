import json
import subprocess
import sys
from pathlib import Path

import pytest


def guadan(*args, cwd=None):
    return subprocess.run([sys.executable, "-m", "guadan", *args],
                          capture_output=True, text=True, cwd=cwd)


def test_aide_disponible():
    r = guadan("--help")
    assert r.returncode == 0
    assert "analyse" in r.stdout


def test_analyse_refuse_un_depot_inexistant(tmp_path):
    r = guadan("analyse", str(tmp_path / "absent"), "--sortie", str(tmp_path / "out"))
    assert r.returncode == 2
    assert "introuvable" in r.stderr


def test_analyse_refuse_un_dossier_sans_cmakelists(tmp_path):
    r = guadan("analyse", str(tmp_path), "--sortie", str(tmp_path / "out"))
    assert r.returncode == 2
    assert "CMakeLists.txt" in r.stderr


EXEMPLES = Path(__file__).resolve().parent.parent / "exemples"


@pytest.mark.docker
def test_analyse_de_bout_en_bout_debordement(tmp_path):
    r = guadan("analyse", str(EXEMPLES / "debordement-tas"), "--sortie", str(tmp_path))
    assert r.returncode == 1, r.stderr  # 1 : au moins un constat prouvé
    rap = json.loads((tmp_path / "rapport.json").read_text())
    [p] = rap["prouves"]
    assert (p["type"], p["fichier"], p["ligne"]) == ("heap-buffer-overflow", "texte.cpp", 8)
    assert (tmp_path / "rapport.html").exists()
    assert "1 constat prouvé" in r.stdout


@pytest.mark.docker
def test_analyse_de_bout_en_bout_sain(tmp_path):
    r = guadan("analyse", str(EXEMPLES / "sain"), "--sortie", str(tmp_path))
    assert r.returncode == 0, r.stdout + r.stderr
    assert json.loads((tmp_path / "rapport.json").read_text())["prouves"] == []
