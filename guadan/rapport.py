"""Rapport à deux niveaux (D-02). Le niveau « prouvé » n'est rempli que par un échec de build ou un
test qui échoue : une alerte d'analyse statique ne peut pas y entrer, quoi qu'elle dise."""
import datetime
import html
import json
from pathlib import Path

from guadan import __version__, bac_a_sable


def _extrait(sortie: str, debut: str = "", n: int = 30) -> str:
    lignes = sortie.splitlines()
    if debut:
        for i, l in enumerate(lignes):
            if debut in l:
                return "\n".join(lignes[i:i + n])
    return "\n".join(lignes[-n:])


def _constat_test(t) -> dict:
    if t.rapports:
        r = t.rapports[0]
        titre = f"{r.type} dans {r.fonction or r.fichier}"
        repere = "AddressSanitizer" if r.outil == "ASan" else "runtime error"
        return {"type": r.type, "categorie": t.categorie, "titre": titre, "test": t.nom,
                "fichier": r.fichier, "ligne": r.ligne, "pile": r.pile,
                "preuve": _extrait(t.sortie, repere), "reproduction": t.reproduction}
    verbe = {"plantage": "plante", "délai dépassé": "dépasse le délai"}.get(t.categorie, "échoue")
    return {"type": t.categorie, "categorie": t.categorie, "titre": f"Le test {t.nom} {verbe}",
            "test": t.nom, "fichier": "", "ligne": 0, "pile": [],
            "preuve": _extrait(t.sortie), "reproduction": t.reproduction}


def construire(depot: str, build, tests: list, alertes: list) -> dict:
    prouves = []
    if not build.reussi:
        prouves.append({"type": f"échec de {build.etape}", "categorie": "build",
                        "titre": f"Le projet ne passe pas l'étape de {build.etape}", "test": "",
                        "fichier": "", "ligne": 0, "pile": [], "preuve": _extrait(build.sortie, n=40),
                        "reproduction": build.reproduction})
    prouves += [_constat_test(t) for t in tests if t.statut == "échoué"]
    non_prouves = [a.__dict__.copy() for a in alertes]
    return {
        "outil": "guadan", "version": __version__, "image": bac_a_sable.IMAGE, "depot": depot,
        "date": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "build": {"reussi": build.reussi, "etape": build.etape, "commande": build.commande,
                  "reproduction": build.reproduction},
        "prouves": prouves,
        "non_prouves": non_prouves,
        "resume": {"tests": len(tests), "tests_echoues": sum(t.statut == "échoué" for t in tests),
                   "prouves": len(prouves), "non_prouves": len(non_prouves)},
    }


STYLE = """
:root{--fond:#fbfaf8;--texte:#1d1d1b;--doux:#5f5e5a;--trait:#e2dfd8;--prouve:#b42318;--carte:#fff;--code:#f3f1ec}
@media (prefers-color-scheme:dark){:root{--fond:#161614;--texte:#ecebe6;--doux:#a3a19a;--trait:#33322e;--prouve:#f97066;--carte:#1f1f1c;--code:#26251f}}
body{margin:0;background:var(--fond);color:var(--texte);font:16px/1.55 system-ui,sans-serif}
main{max-width:920px;margin:0 auto;padding:32px 16px 64px}
h1{font-size:1.6rem;margin:0 0 4px}h2{font-size:1.2rem;margin:40px 0 12px}
.meta{color:var(--doux);font-size:.9rem}
.chiffres{display:flex;gap:24px;flex-wrap:wrap;margin:24px 0}
.chiffres div{min-width:120px}.chiffres b{display:block;font-size:1.8rem}
.constat{background:var(--carte);border:1px solid var(--trait);border-left:4px solid var(--prouve);border-radius:6px;padding:16px;margin:12px 0}
.constat h3{margin:0 0 6px;font-size:1.05rem}
pre{background:var(--code);padding:12px;border-radius:4px;overflow-x:auto;font-size:.82rem;white-space:pre}
.tableau{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:.9rem}td{overflow-wrap:anywhere}td,th{border-bottom:1px solid var(--trait);padding:6px 8px;text-align:left;vertical-align:top}
details summary{cursor:pointer;color:var(--doux)}
"""


def _html(r: dict) -> str:
    e = html.escape
    res = r["resume"]
    constats = "".join(
        f"<article class='constat'><h3>{e(p['titre'])}</h3>"
        f"<p class='meta'>{e(p['categorie'])}"
        f"{' · ' + e(p['fichier']) + ':' + str(p['ligne']) if p['fichier'] else ''}"
        f"{' · test ' + e(p['test']) if p['test'] else ''}</p>"
        f"<p>Pour le reproduire :</p><pre>{e(p['reproduction'])}</pre>"
        f"<details><summary>Preuve observée</summary><pre>{e(p['preuve'])}</pre></details></article>"
        for p in r["prouves"]) or "<p>Aucun constat prouvé.</p>"
    lignes = "".join(
        f"<tr><td>{e(a['fichier'])}:{a['ligne']}</td><td>{e(a['outil'])}<br>{e(a['regle'])}</td>"
        f"<td>{e(a['message'])}</td></tr>" for a in r["non_prouves"])
    alertes = (f"<div class='tableau'><table><tr><th>Emplacement</th><th>Outil</th><th>Message</th></tr>{lignes}</table></div>"
               if lignes else "<p>Aucune alerte.</p>")
    tests = (f"<b>{res['tests_echoues']} / {res['tests']}</b>tests échoués" if r["build"]["reussi"]
             else "<b>—</b>tests non lancés (build en échec)")
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Rapport guadan</title>
<style>{STYLE}</style></head><body><main>
<h1>Rapport guadan : {e(r['depot'])}</h1>
<p class="meta">{e(r['date'])} · guadan {e(r['version'])} · image {e(r['image'])}</p>
<div class="chiffres"><div><b>{res['prouves']}</b>constats prouvés</div>
<div>{tests}</div>
<div><b>{res['non_prouves']}</b>alertes non prouvées</div></div>
<h2>Prouvé</h2><p class="meta">Observé à l'exécution, avec la commande pour le revoir.</p>{constats}
<h2>Non prouvé</h2><p class="meta">Alertes d'analyse statique qu'aucune exécution n'a confirmées.</p>{alertes}
</main></body></html>"""


def ecrire(r: dict, sortie: Path) -> None:
    sortie = Path(sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    (sortie / "rapport.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    (sortie / "rapport.html").write_text(_html(r), encoding="utf-8")
