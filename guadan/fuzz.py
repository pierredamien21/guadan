"""Fuzzing sous sanitizers avec libFuzzer (D-10). Le harnais est fourni par l'utilisateur ou écrit
par le LLM ; dans les deux cas, seul un plantage rejoué sous sanitizer devient un constat prouvé."""
import json
import re
import shlex
from pathlib import Path

from guadan import bac_a_sable, llm, sanitizer
from guadan.build import reproduction
from guadan.tests import ResultatTest

FZ = ("-fsanitize=fuzzer-no-link,address,undefined -fno-sanitize=vptr "
      "-fno-sanitize-recover=undefined -fno-omit-frame-pointer -g")
LIEN = FZ.replace("fuzzer-no-link", "fuzzer")
ENV = "ASAN_OPTIONS=detect_leaks=0"
ESSAIS_HARNAIS = 3

CONSIGNE = """Write a libFuzzer harness for this C/C++ library: one C++ file defining
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) that feeds the input to the
library's public API (parsers, decoders, evaluators first), catches the library's own exceptions,
and never calls exit or abort itself. Never define, stub or override any library, OpenMP or runtime
symbol: the only functions with C linkage you may define are LLVMFuzzerTestOneInput and
LLVMFuzzerInitialize. It is compiled with: clang++ {lien} -I<include dirs> harness.cpp
<library .a files>. Also give up to 10 seed inputs (strings) and up to 30 dictionary tokens of the
input grammar. Reply with JSON only:
{{"harnais": "<C++ code>", "graines": ["..."], "dictionnaire": ["..."]}}

PUBLIC HEADERS:
{entetes}"""


def lire_reponse(texte: str):
    m = re.search(r"\{.*\}", texte, re.S)
    try:
        d = json.loads(m.group(0)) if m else None
    except json.JSONDecodeError:
        # JSON invalide (constaté : graines mal échappées) : on sauve au moins le harnais
        h = re.search(r'"harnais"\s*:\s*"((?:[^"\\]|\\.)*)"', texte, re.S)
        try:
            return (json.loads(f'"{h.group(1)}"'), [], []) if h else (None, [], [])
        except json.JSONDecodeError:
            return None, [], []
    if not isinstance(d, dict) or not isinstance(d.get("harnais"), str):
        return None, [], []
    graines = [g for g in d.get("graines", []) if isinstance(g, str) and len(g) <= 4096][:20]
    dico = []
    for jeton in d.get("dictionnaire", []):
        if isinstance(jeton, str) and 0 < len(jeton) <= 64:
            echappe = "".join(c if 32 <= ord(c) < 127 and c not in '"\\' else
                              ("\\" + c if c in '"\\' else f"\\x{ord(c) & 0xFF:02x}") for c in jeton)
            dico.append(f'"{echappe}"')
    return d["harnais"], graines, dico[:50]


def _entetes(src: Path, budget: int = 7000) -> str:
    fichiers = [f for f in sorted(src.rglob("*")) if f.suffix in (".h", ".hpp", ".hh")
                and not any(p in ("test", "tests", "build", "third_party", "external") for p in f.parts)]
    fichiers.sort(key=lambda f: ("include" not in f.parts, len(f.parts)))  # en-têtes publics d'abord
    morceaux, reste = [], budget
    for f in fichiers:
        texte = f"// {f.relative_to(src)}\n{f.read_text(errors='replace')}\n"
        if len(texte) > reste:
            continue
        morceaux.append(texte)
        reste -= len(texte)
    return "".join(morceaux) or "(aucun en-tête trouvé)"


def _inclusions(travail: Path) -> list:
    """Dossiers d'en-têtes du projet, tirés de la base de compilation."""
    dossiers = []
    for entree in json.loads((travail / "build-fuzz" / "compile_commands.json").read_text()):
        args = entree.get("arguments") or shlex.split(entree["command"])
        for i, a in enumerate(args):
            for opt in ("-I", "-isystem"):
                if a == opt and i + 1 < len(args):
                    dossiers.append(args[i + 1])
                elif a.startswith(opt) and len(a) > len(opt):
                    dossiers.append(a[len(opt):])
    return list(dict.fromkeys(dossiers))


def _compiler_projet(travail: Path, image: str, options) -> str:
    """Seconde compilation, instrumentée pour libFuzzer ; rend le log en cas d'échec."""
    conf = ("rm -rf build-fuzz && cmake -S src -B build-fuzz -G Ninja -DCMAKE_BUILD_TYPE=Debug "
            "-DBUILD_SHARED_LIBS=OFF -DBUILD_TESTING=OFF -DCMAKE_EXPORT_COMPILE_COMMANDS=ON "
            "-DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ "
            f"-DCMAKE_C_FLAGS='{FZ}' -DCMAKE_CXX_FLAGS='{FZ}' " + " ".join(map(shlex.quote, options)))
    r = bac_a_sable.executer(travail, conf, reseau=True, image=image)
    if r.code == 0:
        r = bac_a_sable.executer(travail, "cmake --build build-fuzz", reseau=False, image=image)
    return "" if r.code == 0 else r.sortie


def openmp(travail: Path) -> str:
    """« -fopenmp » si le projet l'utilise : sinon le lien échoue, et un LLM est tenté de bouchonner."""
    return "-fopenmp" if "-fopenmp" in (travail / "build-fuzz" / "compile_commands.json").read_text() else ""


EXTERN_C = re.compile(r'extern\s+"C"[^;{(]*?\b(\w+)\s*\([^;]*?\)\s*\{')
BLOC_C = re.compile(r'extern\s+"C"\s*\{(.*?)^\}', re.S | re.M)
DEFINITION = re.compile(r'^\s*[\w:*&<> ]+?\b(\w+)\s*\([^;{]*\)\s*\{', re.M)


def symboles_redefinis(code: str) -> list:
    """Fonctions à lien C définies par le harnais, hors points d'entrée de libFuzzer. Un harnais qui
    redéfinit un symbole de la bibliothèque peut fabriquer un faux plantage (constaté : bouchons OpenMP)."""
    noms = set(EXTERN_C.findall(code))
    for bloc in BLOC_C.findall(code):
        noms |= set(DEFINITION.findall(bloc))
    return sorted(noms - {"LLVMFuzzerTestOneInput", "LLVMFuzzerInitialize"})


def _compiler_harnais(travail: Path, image: str):
    inc = " ".join(f"-I{shlex.quote(d)}" for d in _inclusions(travail))
    cmd = (f"clang++ {LIEN} {openmp(travail)} {inc} fuzz/harnais.cpp -Wl,--start-group "
           "$(find build-fuzz -name '*.a') -Wl,--end-group -lpthread -o fuzz/fuzzer")
    return bac_a_sable.executer(travail, cmd, reseau=False, image=image)


def lancer(travail: Path, image: str, options=(), harnais: Path = None, client=None,
           duree_s: int = 120) -> tuple:
    """Rend (liste de constats sous forme de ResultatTest, journal pour le rapport)."""
    travail = Path(travail)
    dossier = travail / "fuzz"
    for sous in ("graines", "corpus"):
        (dossier / sous).mkdir(parents=True, exist_ok=True)
    erreur = _compiler_projet(travail, image, options)
    if erreur:
        return [], {"etat": "projet non compilable pour le fuzzing", "detail": erreur[-1500:]}

    messages, origine = [], "fourni"
    if harnais is not None:
        (dossier / "harnais.cpp").write_text(Path(harnais).read_text())
        r = _compiler_harnais(travail, image)
    elif client is not None:
        origine = "écrit par le LLM"
        messages = [{"role": "user", "content": CONSIGNE.format(
            lien=LIEN, entetes=_entetes(travail / "src"))}]
        for _ in range(ESSAIS_HARNAIS):
            try:
                reponse = client.demander(messages, 4000)
            except llm.ErreurLLM as e:
                return [], {"etat": "LLM indisponible", "detail": str(e)}
            code, graines, dico = lire_reponse(reponse)
            if code is None:
                return [], {"etat": "réponse du LLM inexploitable", "detail": reponse[:500]}
            (dossier / "harnais.cpp").write_text(code)
            for i, g in enumerate(graines):
                (dossier / "graines" / f"g{i}").write_bytes(g.encode("utf-8", "replace"))
            (dossier / "dict").write_text("\n".join(dico) + "\n")
            interdits = symboles_redefinis(code)
            if interdits:
                r = bac_a_sable.Resultat(1, f"harnais refusé : il redéfinit {', '.join(interdits)}")
                messages += [{"role": "assistant", "content": reponse}, {"role": "user", "content":
                              f"Rejected: the harness defines {', '.join(interdits)}. Do not define or "
                              "stub any library or runtime symbol. Reply with the corrected JSON."}]
                continue
            r = _compiler_harnais(travail, image)
            if r.code == 0:
                break
            messages += [{"role": "assistant", "content": reponse},
                         {"role": "user", "content": "The harness does not compile or link:\n"
                          + llm.tronquer(r.sortie, 3000) + "\nReply with the corrected JSON."}]
    else:
        return [], {"etat": "pas de harnais (ni fourni, ni LLM)"}
    if r.code != 0:
        return [], {"etat": f"harnais {origine} non compilable", "detail": r.sortie[-1500:]}

    dico = "-dict=dict" if (dossier / "dict").exists() and (dossier / "dict").read_text().strip() else ""
    campagne = (f"cd fuzz && {ENV} ./fuzzer corpus graines {dico} -max_total_time={duree_s} "
                "-max_len=4096 -artifact_prefix=/travail/fuzz/ -print_final_stats=1")
    r = bac_a_sable.executer(travail, campagne, reseau=False, image=image, duree_s=duree_s + 120)
    journal = {"etat": "campagne terminée", "harnais": origine, "duree_s": duree_s,
               "executions": int(m.group(1)) if (m := re.search(r"number_of_executed_units: (\d+)", r.sortie)) else 0}
    plantages = sorted(dossier.glob("crash-*"), key=lambda f: f.stat().st_mtime)
    if not plantages:
        return [], journal

    entree = plantages[-1].name
    mini = bac_a_sable.executer(travail, f"cd fuzz && {ENV} ./fuzzer -minimize_crash=1 -max_total_time=30 "
                                         f"-exact_artifact_path=crash-minimal {entree}",
                                reseau=False, image=image, duree_s=150)
    if mini.code == 0 or (dossier / "crash-minimal").exists():
        entree = "crash-minimal"
    rejeu = f"cd fuzz && {ENV} ./fuzzer {entree}"
    r = bac_a_sable.executer(travail, rejeu, reseau=False, image=image, duree_s=120)
    rapports = sanitizer.lire(r.sortie)
    if not rapports:  # plantage non rejoué sous sanitizer : pas de preuve
        journal["etat"] = "plantage trouvé mais non reproduit"
        return [], journal
    journal["etat"] = "plantage prouvé"
    return [ResultatTest(f"fuzzing ({origine})", "échoué", "fuzzing", r.sortie, rapports,
                         reproduction(travail, rejeu, image))], journal
