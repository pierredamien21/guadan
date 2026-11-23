"""Ligne de commande : guadan analyse <dépôt> --sortie <dossier>."""
import argparse
import sys
from pathlib import Path

from guadan import __version__


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="guadan", description=__doc__)
    p.add_argument("--version", action="version", version=__version__)
    sous = p.add_subparsers(dest="commande", required=True)
    a = sous.add_parser("analyse", help="analyser un dépôt C/C++ CMake")
    a.add_argument("depot", type=Path, help="dossier du dépôt (contient CMakeLists.txt)")
    a.add_argument("--sortie", type=Path, default=Path("guadan-sortie"),
                   help="dossier où écrire rapport.json et rapport.html")
    args = p.parse_args(argv)

    if not args.depot.is_dir():
        print(f"guadan: dépôt introuvable : {args.depot}", file=sys.stderr)
        return 2
    if not (args.depot / "CMakeLists.txt").is_file():
        print(f"guadan: pas de CMakeLists.txt à la racine de {args.depot}", file=sys.stderr)
        return 2
    print(f"guadan: analyse de {args.depot} (pipeline à venir)")  # shortcut: remplacé à T4-T8
    return 0
