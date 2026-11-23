"""Exécution isolée dans l'image d'outils.

Phase A (reseau=True) : configuration, qui peut télécharger des dépendances.
Phase B (reseau=False) : build, tests, analyse et fuzzing, sans réseau.
Dans les deux cas : aucune variable d'environnement de l'hôte, aucune capacité Linux, mémoire,
processus et durée limités. Seul le dossier de travail est monté ; le dépôt d'origine n'y est
qu'en copie.
"""
import os
import shutil
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path

IMAGE = os.environ.get("GUADAN_IMAGE", "guadan-outils")


@dataclass
class Resultat:
    code: int
    sortie: str
    expire: bool = False


def copier(depot: Path, travail: Path) -> Path:
    """Copie le dépôt dans travail/src, sans les dossiers de build existants à la racine."""
    def ignorer(dossier, noms):
        if Path(dossier) != depot:
            return []
        return [n for n in noms if (depot / n / "CMakeCache.txt").exists()]

    src = travail / "src"
    if src.exists():
        shutil.rmtree(src)
    shutil.copytree(depot, src, ignore=ignorer, symlinks=True)
    return src


def executer(travail: Path, commande: str, reseau: bool, duree_s: int = 1800,
             image: str = IMAGE) -> Resultat:
    nom = f"guadan-{uuid.uuid4().hex[:12]}"
    cmd = ["docker", "run", "--rm", "--name", nom,
           "-v", f"{Path(travail).resolve()}:/travail", "-w", "/travail",
           "--user", f"{os.getuid()}:{os.getgid()}", "-e", "HOME=/tmp",
           "--memory", "4g", "--pids-limit", "1024", "--cpus", str(min(4, os.cpu_count() or 1)),
           "--cap-drop", "ALL", "--security-opt", "no-new-privileges"]
    if not reseau:
        cmd += ["--network", "none"]
    cmd += [image, "bash", "-c", commande]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                           errors="replace", timeout=duree_s)
        return Resultat(p.returncode, p.stdout)
    except subprocess.TimeoutExpired as e:
        subprocess.run(["docker", "kill", nom], capture_output=True)
        sortie = e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        return Resultat(124, sortie + f"\n[guadan] arrêté après {duree_s} s", expire=True)
