"""Agrégation de l'évaluation : valeurs attendues calculées à la main sur ces petites données."""
import json

from eval import agreger

PATCH = """--- a/src/x.cpp
+++ b/src/x.cpp
@@ -10,3 +10,4 @@ int f() {
   a();
+  b();
   c();
 }
"""


def rapport(prouves=(), alertes=(), tests=1, echecs=0, build=True):
    return {"build": {"reussi": build}, "prouves": list(prouves), "non_prouves": list(alertes),
            "resume": {"tests": tests, "tests_echoues": echecs, "prouves": len(prouves),
                       "non_prouves": len(alertes)}}


def test_zone_du_bug_lue_dans_le_patch():
    assert agreger.zone(PATCH) == {"src/x.cpp": [(10, 13)]}


def ecrire(dossier, cas, bogue, corrige):
    d = dossier / cas
    for v, r in (("buggy", bogue), ("fixed", corrige)):
        (d / v).mkdir(parents=True)
        (d / v / "rapport.json").write_text(json.dumps(r))
    (d / "bug.patch").write_text(PATCH)


def test_bug_retrouve_localise_et_outils_seuls(tmp_path):
    asan = {"categorie": "sanitizer", "test": "t1", "fichier": "src/x.cpp", "ligne": 11, "pile": []}
    alerte_zone = {"fichier": "src/x.cpp", "ligne": 12, "outil": "cppcheck"}
    alerte_loin = {"fichier": "src/y.cpp", "ligne": 3, "outil": "clang-tidy"}
    ecrire(tmp_path, "a-1", rapport([asan], [alerte_zone, alerte_loin], echecs=1),
           rapport([], [alerte_zone, alerte_loin]))
    echec_ancien = {"categorie": "échec", "test": "t9", "fichier": "", "ligne": 0, "pile": []}
    ecrire(tmp_path, "b-1", rapport([echec_ancien], [], echecs=1), rapport([echec_ancien], [], echecs=1))
    ecrire(tmp_path, "c-1", rapport(build=False, tests=0), rapport(build=False, tests=0))
    lignes = {l["cas"]: l for l in agreger.analyser(tmp_path)}
    a, b, c = lignes["a-1"], lignes["b-1"], lignes["c-1"]
    assert (a["build"], a["retrouve"], a["localise"], a["alertes"], a["alertes_dans_zone"]) == (True, True, True, 2, 1)
    assert (b["retrouve"], b["echecs_deja_presents"]) == (False, 1)  # échoue aussi une fois corrigé
    assert (c["build"], c["retrouve"]) == (False, False)
    t = agreger.totaux(list(lignes.values()))
    assert (t["cas"], t["builds"], t["retrouves"], t["localises"], t["outils_seuls_dans_zone"]) == (3, 2, 1, 1, 1)
