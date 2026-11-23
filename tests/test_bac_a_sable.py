"""Le bac à sable isole vraiment : pas de réseau en phase B, pas de variable de l'hôte, dépôt
d'origine intact. Ces tests lancent des conteneurs (marqueur docker)."""
import os

import pytest

from guadan import bac_a_sable

pytestmark = pytest.mark.docker

# HTTPS vers github.com : port ouvert partout où GitHub l'est (le TCP 53 peut être filtré)
TEST_RESEAU = "python3 -c \"import socket; socket.create_connection(('github.com', 443), 5)\""


def test_phase_b_sans_reseau(tmp_path):
    r = bac_a_sable.executer(tmp_path, TEST_RESEAU, reseau=False)
    assert r.code != 0
    assert "gaierror" in r.sortie or "unreachable" in r.sortie.lower(), r.sortie


def test_phase_a_avec_reseau(tmp_path):
    r = bac_a_sable.executer(tmp_path, TEST_RESEAU, reseau=True)
    assert r.code == 0, r.sortie


def test_aucune_variable_de_l_hote_transmise(tmp_path, monkeypatch):
    monkeypatch.setenv("GUADAN_SECRET_TEST", "ne-doit-pas-passer")
    r = bac_a_sable.executer(tmp_path, "env", reseau=False)
    assert "ne-doit-pas-passer" not in r.sortie


def test_les_fichiers_produits_appartiennent_a_l_utilisateur(tmp_path):
    bac_a_sable.executer(tmp_path, "touch produit", reseau=False)
    assert (tmp_path / "produit").stat().st_uid == os.getuid()


def test_duree_limitee(tmp_path):
    r = bac_a_sable.executer(tmp_path, "sleep 30", reseau=False, duree_s=2)
    assert r.expire


def test_copie_laisse_le_depot_intact(tmp_path):
    depot = tmp_path / "depot"
    (depot / "build").mkdir(parents=True)
    (depot / "build" / "CMakeCache.txt").write_text("cache")  # vrai dossier de build
    (depot / "cmake").mkdir()
    (depot / "cmake" / "Outils.cmake").write_text("# module")  # dossier source ordinaire
    (depot / "CMakeLists.txt").write_text("project(x)\n")
    travail = tmp_path / "travail"
    src = bac_a_sable.copier(depot, travail)
    bac_a_sable.executer(travail, "echo modif >> src/CMakeLists.txt", reseau=False)
    assert (depot / "CMakeLists.txt").read_text() == "project(x)\n"
    assert src == travail / "src"
    assert not (src / "build").exists()  # les anciens dossiers de build ne sont pas copiés
    assert (src / "cmake" / "Outils.cmake").exists()
