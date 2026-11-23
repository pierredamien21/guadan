"""Configuration (phase A, réseau) puis compilation (phase B, sans réseau) avec Clang, ASan et UBSan."""
import shlex
from dataclasses import dataclass
from pathlib import Path

from guadan import bac_a_sable

# -fno-sanitize-recover=undefined : UBSan arrête le programme, sinon le test passerait quand même.
# -fno-sanitize=vptr : sinon un programme C lié à une bibliothèque C++ instrumentée ne se lie pas
# (runtime UBSan C++ absent ; constaté sur muparser, example2.c).
SAN = ("-fsanitize=address,undefined -fno-sanitize=vptr -fno-sanitize-recover=undefined "
       "-fno-omit-frame-pointer -g")
CONFIGURATION = ("cmake -S src -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug "
                 "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_TESTING=ON "
                 "-DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ "
                 f"-DCMAKE_C_FLAGS='{SAN}' -DCMAKE_CXX_FLAGS='{SAN}'")
COMPILATION = "cmake --build build"


@dataclass
class Build:
    reussi: bool
    etape: str  # « configuration » ou « compilation » : la dernière étape tentée
    commande: str
    sortie: str
    reproduction: str


def reproduction(travail: Path, commande: str) -> str:
    """Commande que l'utilisateur peut relancer telle quelle pour voir le même résultat."""
    return (f"docker run --rm -v {shlex.quote(str(Path(travail).resolve()))}:/travail -w /travail "
            f"{bac_a_sable.IMAGE} bash -c {shlex.quote(commande)}")


def construire(travail: Path) -> Build:
    for etape, commande, reseau in (("configuration", CONFIGURATION, True),
                                    ("compilation", COMPILATION, False)):
        r = bac_a_sable.executer(travail, commande, reseau=reseau)
        if r.code != 0:
            return Build(False, etape, commande, r.sortie, reproduction(travail, commande))
    return Build(True, etape, commande, r.sortie, reproduction(travail, commande))
