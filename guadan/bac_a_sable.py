"""Exécution isolée dans l'image d'outils.

Phase A (reseau=True) : configuration, qui peut télécharger des dépendances.
Phase B (reseau=False) : build, tests, analyse et fuzzing, sans réseau.
Dans les deux cas : aucune variable d'environnement de l'hôte, aucune capacité Linux, mémoire,
processus et durée limités. Seul le dossier de travail est monté ; le dépôt d'origine n'y est
qu'en copie.
"""
import hashlib
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


def image_avec(paquets: list, base: str = IMAGE) -> tuple:
    """Image dérivée de l'image d'outils avec des paquets apt en plus. Seuls des paquets des
    dépôts Ubuntu sont installés : aucun code du projet analysé ne s'exécute ici.
    Rend (nom de l'image ou None, sortie de docker build)."""
    paquets = sorted(set(paquets))
    if not paquets:
        return base, ""
    nom = f"{base}-{hashlib.sha256(' '.join(paquets).encode()).hexdigest()[:12]}"
    if subprocess.run(["docker", "image", "inspect", nom], capture_output=True).returncode == 0:
        return nom, ""
    dockerfile = (f"FROM {base}\nRUN apt-get update && DEBIAN_FRONTEND=noninteractive "
                  f"apt-get install -y --no-install-recommends {' '.join(paquets)} "
                  "&& rm -rf /var/lib/apt/lists/*\n")
    p = subprocess.run(["docker", "build", "-q", "-t", nom, "-"], input=dockerfile, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, errors="replace")
    return (nom if p.returncode == 0 else None), p.stdout


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
