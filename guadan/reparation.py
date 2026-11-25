"""Réparation d'un échec de build : le LLM propose des paquets apt, des options CMake et des
drapeaux de compilation.

Chaque proposition est filtrée par une liste blanche de formats avant d'être essayée : rien de ce
que dit le modèle n'est exécuté tel quel, et aucun drapeau ne peut toucher aux sanitizers.
"""
import json
import re
from dataclasses import dataclass

from guadan import llm

PAQUET = re.compile(r"^[a-z0-9][a-z0-9+.-]{1,62}$")
OPTION = re.compile(r"^-D[A-Za-z_][A-Za-z0-9_]*(:[A-Z]+)?=[A-Za-z0-9_.,/+-]*$")
# avertissements, norme du langage, macros : rien qui commence par -f (donc rien sur les sanitizers)
DRAPEAU = re.compile(r"^-(W[A-Za-z0-9=+-]+|std=(c|gnu)(\+\+)?[0-9a-z]{2}|D[A-Za-z_][A-Za-z0-9_]*(=[A-Za-z0-9_.]*)?)$")
MAX = 10

CONSIGNE = """The build of a C/C++ CMake project failed at the {etape} step inside an Ubuntu 24.04
container (clang 18 with -fsanitize=address,undefined, CMake 3.28; installed: cmake ninja-build
pkg-config git python3 libomp-18-dev). The compiler already appends -Wno-error. Propose the smallest
fix: Ubuntu 24.04 apt packages, CMake -D options (for example to disable an optional feature), and/or
extra compiler flags appended last (warnings -W..., -std=..., -D macros; never -f... flags). Old code
often needs an older -std or a -Wno-... flag. Reply with JSON only:
{{"paquets_apt": ["..."], "options_cmake": ["-DNAME=VALUE"], "drapeaux": ["-W..."], "explication": "one sentence"}}

TOP-LEVEL CMakeLists.txt (excerpt):
{cmakelists}

BUILD LOG (error lines first, then the end of the log):
{log}"""


@dataclass
class Proposition:
    paquets: list
    options: list
    explication: str
    drapeaux: list = None


def _valides(d: dict, cle: str, motif) -> list:
    return [x for x in d.get(cle, []) if isinstance(x, str) and motif.match(x)][:MAX]


def lire_proposition(texte: str):
    m = re.search(r"\{.*\}", texte, re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    paquets, options = _valides(d, "paquets_apt", PAQUET), _valides(d, "options_cmake", OPTION)
    drapeaux = _valides(d, "drapeaux", DRAPEAU)
    if not (paquets or options or drapeaux):
        return None
    return Proposition(paquets, options, str(d.get("explication", ""))[:300], drapeaux)


def log_utile(sortie: str) -> str:
    """Les lignes d'erreur d'abord : un build qui échoue noie souvent l'erreur sous les avertissements."""
    erreurs = [l for l in sortie.splitlines() if "error" in l.lower() or "Could NOT" in l][:60]
    return llm.tronquer("\n".join(erreurs) + "\n[…]\n" + llm.tronquer(sortie, 4000), 9000)


def proposer(client, sortie: str, cmakelists: str, etape: str = "configuration"):
    """Rend (Proposition ou None, message d'erreur éventuel)."""
    question = CONSIGNE.format(etape=etape, cmakelists=llm.tronquer(cmakelists, 3000), log=log_utile(sortie))
    try:
        return lire_proposition(client.demander([{"role": "user", "content": question}], 2000)), ""
    except llm.ErreurLLM as e:
        return None, str(e)
