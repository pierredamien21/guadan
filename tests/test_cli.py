import subprocess
import sys


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
