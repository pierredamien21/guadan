"""Ligne de commande : guadan analyse <dépôt> --sortie <dossier>."""
import argparse
import shutil
import sys
from pathlib import Path

from guadan import __version__, llm, pipeline


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="guadan", description=__doc__)
    p.add_argument("--version", action="version", version=__version__)
    sous = p.add_subparsers(dest="commande", required=True)
    a = sous.add_parser("analyse", help="analyser un dépôt C/C++ CMake")
    a.add_argument("depot", type=Path, help="dossier du dépôt (contient CMakeLists.txt)")
    a.add_argument("--sortie", type=Path, default=Path("guadan-sortie"),
                   help="dossier où écrire rapport.json et rapport.html")
    a.add_argument("--apt", action="append", default=[], metavar="PAQUET",
                   help="paquet Ubuntu à installer avant le build (répétable)")
    a.add_argument("--harnais", type=Path, metavar="FICHIER.cpp",
                   help="harnais libFuzzer à utiliser (sinon écrit par le LLM s'il y a une clé)")
    a.add_argument("--fuzz-duree", type=int, default=120, metavar="SECONDES",
                   help="durée de la campagne de fuzzing, 0 pour la désactiver (défaut 120)")
    a.add_argument("--declencheurs", type=int, default=0, metavar="N",
                   help="tenter un test déclencheur pour les N alertes les plus graves (coûteux en jetons)")
    a.add_argument("--sans-llm", action="store_true",
                   help="ne rien envoyer à un modèle, même si une clé est définie")
    args = p.parse_args(argv)

    if not args.depot.is_dir():
        print(f"guadan: dépôt introuvable : {args.depot}", file=sys.stderr)
        return 2
    if not (args.depot / "CMakeLists.txt").is_file():
        print(f"guadan: pas de CMakeLists.txt à la racine de {args.depot}", file=sys.stderr)
        return 2
    if shutil.which("docker") is None:
        print("guadan: docker introuvable ; il faut Docker pour isoler le build", file=sys.stderr)
        return 2
    if args.sortie.resolve().is_relative_to(args.depot.resolve()):
        print("guadan: le dossier de sortie ne doit pas être dans le dépôt analysé", file=sys.stderr)
        return 2

    print(f"guadan: analyse de {args.depot}…", flush=True)
    client = None if args.sans_llm else llm.Client.depuis_env()
    if client is None and not args.sans_llm:
        print("guadan: pas de clé GUADAN_API_KEY ni GROQ_API_KEY : analyse sans LLM")
    r = pipeline.analyser(args.depot, args.sortie, client=client, apt=args.apt,
                          harnais=args.harnais, fuzz_duree=args.fuzz_duree,
                          declencheurs_max=args.declencheurs)
    res = r["resume"]
    pluriel = "s" if res["prouves"] > 1 else ""
    print(f"guadan: {res['prouves']} constat{pluriel} prouvé{pluriel}, "
          f"{res['tests_echoues']}/{res['tests']} tests échoués, "
          f"{res['non_prouves']} alertes non prouvées")
    print(f"guadan: rapport dans {args.sortie / 'rapport.html'}")
    return 1 if res["prouves"] else 0
