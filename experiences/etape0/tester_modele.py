#!/usr/bin/env python3
"""Étape 0 : un modèle gratuit sait-il écrire un test qui déclenche une alerte sous sanitizer ?

Pour chaque alerte de alertes-choisies.md, on envoie au modèle le code autour de l'alerte et
l'API publique de muparser, on compile sa réponse avec ASan et UBSan contre muparser compilé de
la même façon, et on l'exécute. Une alerte est « prouvée » seulement si le rapport du sanitizer
cite le fichier et la ligne de l'alerte. Jusqu'à 3 essais, l'erreur du précédent étant renvoyée.

Usage (dans WSL, clé dans GROQ_API_KEY) :
    python3 tester_modele.py <dossier_de_travail> <dossier_resultats>
    python3 tester_modele.py --autotest
"""
import json, os, re, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

URL = "https://api.groq.com/openai/v1/chat/completions"
MODELE = "openai/gpt-oss-120b"
COMMIT = "9e28c71"  # parent du correctif d'ARVO 25402
SAN = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"]
ESSAIS = 3

ALERTES = [  # (fichier, ligne, message) : voir alertes-choisies.md
    ("src/muParserInt.cpp", 186, "[cppcheck/shiftTooManyBitsSigned] Shifting signed 32-bit value by 31 bits is undefined behaviour"),
    ("src/muParserBase.cpp", 151, "[bugprone-unhandled-self-assignment] operator=() does not handle self-assignment properly"),
    ("samples/example2/example2.c", 334, "[cppcheck/nullPointerOutOfMemory] If memory allocation fails, then there is a possible null pointer dereference: x"),
    ("src/muParserTokenReader.cpp", 379, "[bugprone-narrowing-conversions] narrowing conversion from 'std::size_t' to signed type 'difference_type' is implementation-defined"),
    ("src/muParser.cpp", 84, "[clang-analyzer-optin.cplusplus.VirtualCall] Call to virtual method 'Parser::InitCharSets' during construction bypasses virtual dispatch"),
    # synthétique : emplacement réel de la faille ARVO 25402, qu'aucun analyseur n'a signalé
    ("src/muParserBase.cpp", 1242, "[synthetic] possible out-of-bounds read of 'Stack' at index m_nFinalResultIdx"),
]

CONSIGNE = """You are given a static-analysis alert in the C++ library muparser.
Write ONE complete C++ program (a main() function) that makes AddressSanitizer or
UndefinedBehaviorSanitizer report the defect AT THE ALERT LINE, using only the public API
(headers below). The program is compiled with: clang++ {flags} -Iinclude test.cpp libmuparser.a
and the library itself is compiled with the same sanitizers.
If you believe the alert cannot be triggered through the public API (false alarm, unreachable
code, or it only happens when malloc fails), reply with the single line UNTRIGGERABLE followed
by one sentence explaining why. Otherwise reply with the program in one ```cpp block and nothing else.

ALERT: {fichier}:{ligne}: {message}

CODE AROUND THE ALERT ({fichier}, lines {debut}-{fin}):
{extrait}

PUBLIC HEADERS:
{entetes}"""


def verdict(sortie: str, fichier: str, ligne: int) -> str:
    """prouvé si un rapport de sanitizer cite fichier:ligne ; sanitizer_ailleurs ; rien."""
    rapport = "ERROR: AddressSanitizer" in sortie or "runtime error:" in sortie
    if not rapport:
        return "rien"
    return "prouvé" if re.search(rf"{re.escape(Path(fichier).name)}:{ligne}(\D|$)", sortie) else "sanitizer_ailleurs"


def autotest():
    f = "src/muParserInt.cpp"
    assert verdict("x/src/muParserInt.cpp:186:24: runtime error: left shift", f, 186) == "prouvé"
    assert verdict("muParserInt.cpp:1860: runtime error: x", f, 186) == "sanitizer_ailleurs"
    assert verdict("==1==ERROR: AddressSanitizer: heap\n #0 in f muParserInt.cpp:186", f, 186) == "prouvé"
    assert verdict("muParserInt.cpp:186 tout va bien", f, 186) == "rien"
    assert extraire_code("blabla\n```cpp\nint main(){}\n```\nfin") == "int main(){}"
    assert extraire_code("UNTRIGGERABLE because") is None
    print("autotest ok")


def extraire_code(reponse: str):
    m = re.search(r"```(?:cpp|c\+\+|c)?\s*\n(.*?)```", reponse, re.S)
    return m.group(1).strip() if m else None


def appeler(messages, cle):
    corps = json.dumps({"model": MODELE, "messages": messages, "max_completion_tokens": 3000,
                        "reasoning_effort": "medium"}).encode()
    for _ in range(6):
        # sans User-Agent explicite, Cloudflare bloque « Python-urllib » (HTTP 403, code 1010)
        req = urllib.request.Request(URL, corps, {"Authorization": f"Bearer {cle}",
                                                   "Content-Type": "application/json",
                                                   "User-Agent": "guadan-etape0/0.1"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.load(r)
            return d["choices"][0]["message"]["content"] or "", d.get("usage", {})
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise RuntimeError(f"HTTP {e.code}: {e.read()[:300]!r}") from None
            attente = float(e.headers.get("retry-after", "30")) + 1
            print(f"    limite Groq atteinte, attente {attente:.0f} s", flush=True)
            time.sleep(attente)
    raise RuntimeError("limite Groq toujours atteinte après 6 tentatives")


def sh(cmd, cwd, timeout=600, env=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                       env={**os.environ, **(env or {})})
    return p.returncode, p.stdout + p.stderr


def preparer(src: Path):
    """Compile muparser au commit vulnérable avec Clang et les sanitizers."""
    sh(["git", "checkout", "-q", COMMIT], src)
    b = src / "build-modele"
    if not (b / "libmuparser.a").exists():
        code, out = sh(["cmake", "-S", ".", "-B", "build-modele", "-DCMAKE_CXX_COMPILER=clang++",
                        "-DCMAKE_C_COMPILER=clang", "-DCMAKE_BUILD_TYPE=Debug",
                        "-DCMAKE_POLICY_VERSION_MINIMUM=3.5", "-DENABLE_OPENMP=OFF",
                        "-DBUILD_SHARED_LIBS=OFF", f"-DCMAKE_CXX_FLAGS={' '.join(SAN)}"], src)
        code2, out2 = sh(["cmake", "--build", "build-modele", f"-j{os.cpu_count()}"], src)
        if code or code2:
            sys.exit(f"build de muparser échoué :\n{(out + out2)[-2000:]}")
    return b / "libmuparser.a"


def main(travail: Path, res: Path):
    cle = os.environ.get("GROQ_API_KEY") or sys.exit("GROQ_API_KEY absente")
    src = travail / "muparser"
    lib = preparer(src)
    res.mkdir(parents=True, exist_ok=True)
    entetes = "\n".join(f"// {h}\n{(src / h).read_text(errors='replace')}"
                        for h in ("include/muParser.h", "include/muParserInt.h"))
    lignes_resume = ["| # | Alerte | Verdict | Essais | Jetons |", "|---|---|---|---|---|"]

    for n, (fichier, ligne, message) in enumerate(ALERTES, 1):
        texte = (src / fichier).read_text(errors="replace").splitlines()
        debut, fin = max(1, ligne - 60), min(len(texte), ligne + 60)
        extrait = "\n".join(f"{i:5} {texte[i - 1]}" for i in range(debut, fin + 1))
        messages = [{"role": "user", "content": CONSIGNE.format(
            flags=" ".join(SAN), fichier=fichier, ligne=ligne, message=message,
            debut=debut, fin=fin, extrait=extrait, entetes=entetes)}]
        etat, jetons = "rien", 0
        for k in range(1, ESSAIS + 1):
            print(f"alerte {n} essai {k} : {fichier}:{ligne}", flush=True)
            reponse, usage = appeler(messages, cle)
            jetons += usage.get("total_tokens", 0)
            (res / f"alerte{n}-essai{k}-reponse.md").write_text(reponse)
            code = extraire_code(reponse)
            if code is None:
                etat = "refus_motivé" if "UNTRIGGERABLE" in reponse else "réponse_sans_code"
                break
            t = res / f"alerte{n}-essai{k}.cpp"
            t.write_text(code + "\n")
            c, sortie = sh(["clang++", *SAN, "-Iinclude", str(t), str(lib), "-o", str(res / "test")], src)
            if c:
                etat, retour = "ne_compile_pas", f"The program does not compile:\n{sortie[-1500:]}"
            else:
                try:
                    _, sortie = sh([str(res / "test")], src, timeout=30, env={
                        "ASAN_OPTIONS": "detect_leaks=0",
                        "UBSAN_OPTIONS": "print_stacktrace=1:halt_on_error=1"})
                except subprocess.TimeoutExpired:
                    sortie = "timeout after 30 s"
                etat = verdict(sortie, fichier, ligne)
                retour = f"The program ran but the sanitizer did not report {fichier}:{ligne}. Output:\n{sortie[-1500:]}"
            (res / f"alerte{n}-essai{k}.log").write_text(sortie)
            print(f"    -> {etat}", flush=True)
            if etat == "prouvé":
                break
            messages += [{"role": "assistant", "content": reponse}, {"role": "user", "content": retour}]
        lignes_resume.append(f"| {n} | `{fichier}:{ligne}` | {etat} | {k} | {jetons} |")

    resume = "\n".join([f"Modèle : `{MODELE}` (Groq), muparser `{COMMIT}`, "
                        f"{time.strftime('%Y-%m-%d %H:%M')}", "", *lignes_resume, ""])
    (res / "resume.md").write_text(resume)
    print(resume)


if __name__ == "__main__":
    if sys.argv[1:] == ["--autotest"]:
        autotest()
    elif len(sys.argv) == 3:
        main(Path(sys.argv[1]), Path(sys.argv[2]))
    else:
        sys.exit(__doc__)
