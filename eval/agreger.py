"""Agrège les rapports de l'évaluation : python3 -m eval.agreger <dossier des résultats>.

Chaque cas contient buggy/rapport.json, fixed/rapport.json et bug.patch (le patch de BugsC++ qui
transforme la version corrigée en version boguée : ses lignes « + » sont la zone du bug).
"""
import json
import re
import sys
from pathlib import Path

MARGE = 2  # lignes de tolérance autour de la zone modifiée par le correctif
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def zone(patch: str) -> dict:
    """{fichier: [(première, dernière ligne)]} dans la version boguée."""
    zones, fichier = {}, None
    for l in patch.splitlines():
        if l.startswith("+++ "):
            chemin = l[4:].split("\t")[0]
            fichier = None if chemin == "/dev/null" else re.sub(r"^b/", "", chemin)
        elif fichier and (m := HUNK.match(l)):
            debut, n = int(m.group(1)), int(m.group(2) or 1)
            zones.setdefault(fichier, []).append((debut, debut + max(n, 1) - 1))
    return zones


def _dans(zones: dict, fichier: str, ligne: int) -> bool:
    return any(a - MARGE <= ligne <= b + MARGE for a, b in zones.get(fichier, []))


def _localise(constat: dict, zones: dict) -> bool:
    lieux = [(constat.get("fichier", ""), constat.get("ligne", 0))]
    for p in constat.get("pile", []):
        if m := re.match(r"(\S+):(\d+)", p):
            lieux.append((m.group(1), int(m.group(2))))
    return any(_dans(zones, f, n) for f, n in lieux if f)


def _cle(c: dict) -> tuple:
    return c.get("categorie"), c.get("test"), c.get("type")


def analyser(dossier: Path) -> list:
    lignes = []
    for cas in sorted(p for p in Path(dossier).iterdir() if (p / "buggy" / "rapport.json").exists()):
        b = json.loads((cas / "buggy" / "rapport.json").read_text(encoding="utf-8"))
        f = json.loads((cas / "fixed" / "rapport.json").read_text(encoding="utf-8")) if (cas / "fixed" / "rapport.json").exists() else None
        zones = zone((cas / "bug.patch").read_text(encoding="utf-8")) if (cas / "bug.patch").exists() else {}
        deja = {_cle(c) for c in (f or {}).get("prouves", [])}
        nouveaux = [c for c in b["prouves"] if _cle(c) not in deja and c.get("categorie") != "build"]
        lignes.append({
            "cas": cas.name,
            "build": b["build"]["reussi"] and bool(f and f["build"]["reussi"]),
            "tests": b["resume"]["tests"],
            "prouves": len(b["prouves"]),
            "retrouve": bool(nouveaux),
            "localise": any(_localise(c, zones) for c in nouveaux),
            "echecs_deja_presents": len(deja),
            "alertes": len(b["non_prouves"]),
            "alertes_dans_zone": sum(_localise(a, zones) for a in b["non_prouves"]),
        })
    return lignes


def totaux(lignes: list) -> dict:
    return {"cas": len(lignes), "builds": sum(l["build"] for l in lignes),
            "retrouves": sum(l["retrouve"] for l in lignes),
            "localises": sum(l["localise"] for l in lignes),
            "outils_seuls_dans_zone": sum(l["alertes_dans_zone"] > 0 for l in lignes),
            "alertes": sum(l["alertes"] for l in lignes),
            "prouves": sum(l["prouves"] for l in lignes)}


def markdown(lignes: list) -> str:
    t = totaux(lignes)
    oui = lambda v: "oui" if v else "non"
    corps = "\n".join(
        f"| {l['cas']} | {oui(l['build'])} | {l['tests']} | {l['prouves']} | {oui(l['retrouve'])} | "
        f"{oui(l['localise'])} | {l['echecs_deja_presents']} | {l['alertes']} | {l['alertes_dans_zone']} |"
        for l in lignes)
    return (f"| Cas | Build | Tests | Prouvés | Bug retrouvé | Localisé | Échecs déjà présents | "
            f"Alertes | Alertes dans la zone du bug |\n|---|---|---|---|---|---|---|---|---|\n{corps}\n\n"
            f"**Totaux** : {t['cas']} cas, {t['builds']} builds réussis, {t['retrouves']} bugs retrouvés "
            f"(prouvés sur la version boguée et absents de la corrigée), dont {t['localises']} localisés "
            f"dans la zone du correctif ; {t['alertes']} alertes statiques au total, et des alertes dans "
            f"la zone du bug pour {t['outils_seuls_dans_zone']} cas sur {t['cas']}.\n")


if __name__ == "__main__":
    resultats = analyser(Path(sys.argv[1]))
    print(markdown(resultats))
    Path(sys.argv[1], "resultats.json").write_text(
        json.dumps({"cas": resultats, "totaux": totaux(resultats)}, ensure_ascii=False, indent=2), encoding="utf-8")
