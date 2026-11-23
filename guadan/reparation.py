"""Réparation d'un échec de configuration : le LLM propose des paquets apt et des options CMake.

Chaque proposition est filtrée par une liste blanche de formats avant d'être essayée : rien de ce
que dit le modèle n'est exécuté tel quel.
"""
import json
import re
from dataclasses import dataclass

from guadan import llm

PAQUET = re.compile(r"^[a-z0-9][a-z0-9+.-]{1,62}$")
OPTION = re.compile(r"^-D[A-Za-z_][A-Za-z0-9_]*(:[A-Z]+)?=[A-Za-z0-9_.,/+-]*$")
MAX = 10

CONSIGNE = """The CMake configuration of a C/C++ project failed inside an Ubuntu 24.04 container
(clang 18, CMake 3.28, already installed: cmake ninja-build pkg-config git python3 libomp-18-dev).
Propose the smallest fix: Ubuntu 24.04 apt package names to install, and/or CMake -D options
(for example to disable an optional feature). Reply with JSON only:
{{"paquets_apt": ["..."], "options_cmake": ["-DNAME=VALUE"], "explication": "one sentence"}}

TOP-LEVEL CMakeLists.txt (excerpt):
{cmakelists}

CONFIGURATION LOG (truncated):
{log}"""


@dataclass
class Proposition:
    paquets: list
    options: list
    explication: str


def lire_proposition(texte: str):
    m = re.search(r"\{.*\}", texte, re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    paquets = [p for p in d.get("paquets_apt", []) if isinstance(p, str) and PAQUET.match(p)][:MAX]
    options = [o for o in d.get("options_cmake", []) if isinstance(o, str) and OPTION.match(o)][:MAX]
    if not paquets and not options:
        return None
    return Proposition(paquets, options, str(d.get("explication", ""))[:300])


def proposer(client, sortie: str, cmakelists: str):
    """Rend (Proposition ou None, message d'erreur éventuel)."""
    question = CONSIGNE.format(cmakelists=llm.tronquer(cmakelists, 3000), log=llm.tronquer(sortie, 8000))
    try:
        return lire_proposition(client.demander([{"role": "user", "content": question}], 2000)), ""
    except llm.ErreurLLM as e:
        return None, str(e)
