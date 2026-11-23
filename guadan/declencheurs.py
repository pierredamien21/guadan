"""Tentative bornée de tests déclencheurs (D-10) : le LLM écrit un programme qui doit faire réagir
un sanitizer à la ligne d'une alerte. Seul un rapport de sanitizer à cette ligne prouve l'alerte."""
import re
from pathlib import Path

from guadan import bac_a_sable, fuzz, llm, sanitizer
from guadan.build import reproduction
from guadan.tests import ResultatTest

ESSAIS = 2
GRAVITE = {"error": 0, "warning": 1}
CONSIGNE = """Static analysis reported this alert in a C/C++ library:
{fichier}:{ligne}: [{outil}/{regle}] {message}
Write ONE complete C++ program (with main()) that makes AddressSanitizer or
UndefinedBehaviorSanitizer report the defect AT THAT LINE, using the library's functions (declare
them yourself if no header exposes them). Compiled with: clang++ -fsanitize=address,undefined
-I<include dirs> test.cpp <library .a files>.
If the defect cannot be triggered (false alarm, unreachable, only on malloc failure), reply with the
single line UNTRIGGERABLE and one sentence why. Otherwise reply with the program in one ```cpp block.

CODE AROUND THE ALERT ({fichier}, lines {debut}-{fin}):
{extrait}

PUBLIC HEADERS:
{entetes}"""


def choisir(alertes: list, n: int) -> list:
    return sorted(alertes, key=lambda a: (GRAVITE.get(a.gravite, 2), a.outil != "cppcheck"))[:n]


def prouve(rapports: list, alerte) -> bool:
    cible = f"{alerte.fichier}:{alerte.ligne}"
    return any((r.fichier, r.ligne) == (alerte.fichier, alerte.ligne)
               or any(p.split(" ")[0] == cible for p in r.pile) for r in rapports)


def _extrait(src: Path, alerte, marge: int = 40):
    lignes = (src / alerte.fichier).read_text(errors="replace").splitlines()
    debut, fin = max(1, alerte.ligne - marge), min(len(lignes), alerte.ligne + marge)
    return debut, fin, "\n".join(f"{i:5} {lignes[i - 1]}" for i in range(debut, fin + 1))


def tenter(travail: Path, image: str, alertes: list, client, n: int, options=()) -> tuple:
    """Rend (constats prouvés, état de chaque alerte tentée par (fichier, ligne, règle))."""
    travail, etats, constats = Path(travail), {}, []
    if not (travail / "build-fuzz" / "compile_commands.json").exists():
        if fuzz._compiler_projet(travail, image, options):
            return [], {(a.fichier, a.ligne, a.regle): "projet non compilable" for a in choisir(alertes, n)}
    (travail / "fuzz").mkdir(exist_ok=True)
    inc = " ".join(f"-I{d}" for d in fuzz._inclusions(travail))
    entetes = fuzz._entetes(travail / "src", 4000)
    compiler = (f"clang++ {fuzz.FZ} {fuzz.openmp(travail)} {inc} fuzz/declencheur.cpp -Wl,--start-group "
                "$(find build-fuzz -name '*.a') -Wl,--end-group -lpthread -o fuzz/declencheur")
    executer = "ASAN_OPTIONS=detect_leaks=0 ./fuzz/declencheur"

    lignes_prouvees = set()
    for a in choisir(alertes, n):
        cle = (a.fichier, a.ligne, a.regle)
        if (a.fichier, a.ligne) in lignes_prouvees:  # une seule preuve par ligne, pas de jetons en plus
            etats[cle] = "prouvé"
            continue
        debut, fin, extrait = _extrait(travail / "src", a)
        messages = [{"role": "user", "content": CONSIGNE.format(
            fichier=a.fichier, ligne=a.ligne, outil=a.outil, regle=a.regle, message=a.message,
            debut=debut, fin=fin, extrait=extrait, entetes=entetes)}]
        etats[cle] = "non prouvé"
        for _ in range(ESSAIS):
            try:
                reponse = client.demander(messages, 3000)
            except llm.ErreurLLM:
                etats[cle] = "LLM indisponible"
                break
            m = re.search(r"```(?:cpp|c\+\+|c)?\s*\n(.*?)```", reponse, re.S)
            if m is None:
                etats[cle] = "refusé par le modèle" if "UNTRIGGERABLE" in reponse else "réponse inexploitable"
                break
            (travail / "fuzz" / "declencheur.cpp").write_text(m.group(1))
            r = bac_a_sable.executer(travail, compiler, reseau=False, image=image, duree_s=300)
            if r.code != 0:
                etats[cle], retour = "ne compile pas", "It does not compile:\n" + llm.tronquer(r.sortie, 2500)
            else:
                r = bac_a_sable.executer(travail, executer, reseau=False, image=image, duree_s=30)
                rapports = sanitizer.lire(r.sortie)
                if prouve(rapports, a):
                    etats[cle] = "prouvé"
                    lignes_prouvees.add((a.fichier, a.ligne))
                    constats.append(ResultatTest(f"déclencheur {a.fichier}:{a.ligne}", "échoué",
                                                 "déclencheur", r.sortie, rapports,
                                                 reproduction(travail, f"{compiler} && {executer}", image)))
                    break
                etats[cle] = "non prouvé"
                retour = (f"It ran but no sanitizer report points at {a.fichier}:{a.ligne}. Output:\n"
                          + llm.tronquer(r.sortie, 2500))
            messages += [{"role": "assistant", "content": reponse}, {"role": "user", "content": retour}]
    return constats, etats
