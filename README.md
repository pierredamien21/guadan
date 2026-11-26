# guadan

**Diagnostic prouvé de dépôts C/C++ CMake.** guadan compile un projet dans un conteneur isolé avec
AddressSanitizer et UndefinedBehaviorSanitizer, lance ses tests, le fuzz, passe les analyseurs
statiques, puis rend un rapport à deux niveaux :

- **Prouvé** : ce qui a été observé à l'exécution (échec de build, test qui échoue, rapport de
  sanitizer, plantage trouvé par fuzzing), toujours avec la commande pour le revoir.
- **Non prouvé** : les alertes de cppcheck et clang-tidy qu'aucune exécution n'a confirmées.

Le niveau « prouvé » est décidé par du code, jamais par un modèle de langage. Le LLM, facultatif,
sert d'outil : il répare les builds, écrit des harnais de fuzzing et trie les alertes.

> *English summary: guadan builds a C/C++ CMake repository in a sandbox with ASan/UBSan, runs its
> tests, fuzzes it and runs static analyzers. A finding is reported as **proven** only when it was
> observed at runtime, with the exact command to reproduce it. An optional LLM repairs builds,
> writes fuzzing harnesses and triages static alerts; it never decides what is proven.*

## Pourquoi

Un dépôt C/C++ inconnu produit vite des centaines d'avertissements, dont la plupart ne comptent
pas. Sur muparser, cppcheck et clang-tidy en signalent 38 ; aucun ne pointe la faille connue de
cette version. En deux minutes de fuzzing avec un harnais écrit par un modèle gratuit, guadan y a
trouvé seul un comportement indéfini réel (`muParserBytecode.cpp:158`, entrée `88e8&&2`), confirmé
depuis par une correction en amont.

## Démarrage rapide

Il faut Linux (ou WSL 2), Docker et Python 3.10 ou plus. Aucune dépendance Python.

```bash
git clone https://github.com/pierredamien21/guadan && cd guadan
docker build -t guadan-outils docker/
python3 -m guadan analyse /chemin/vers/projet --sortie /tmp/rapport
```

Le rapport est dans `/tmp/rapport/rapport.html` (et `rapport.json`). Code de sortie : 0 sans
constat prouvé, 1 s'il y en a, 2 en cas d'erreur d'usage.

Options utiles :

| Option | Effet |
|---|---|
| `--apt PAQUET` | installe un paquet Ubuntu avant le build (répétable) |
| `--fuzz-duree S` | durée du fuzzing en secondes (défaut 120 ; il faut un harnais ou une clé LLM) |
| `--harnais F.cpp` | harnais libFuzzer fourni, sans LLM |
| `--declencheurs N` | le LLM tente un test qui prouve les N alertes les plus graves |
| `--sans-llm` | ne rien envoyer à un modèle |

### Avec un modèle de langage (facultatif)

Toute API au format OpenAI convient. Par défaut, guadan utilise l'offre gratuite de Groq :

```bash
export GUADAN_API_KEY=...   # ou GROQ_API_KEY ; GUADAN_API_URL et GUADAN_MODEL pour un autre service
```

guadan prévient avant le premier envoi : des extraits du dépôt (logs, en-têtes, code autour des
alertes) partent chez ce fournisseur. Sans clé, tout fonctionne, sauf ce que fait le LLM.

## Action GitHub

```yaml
- uses: actions/checkout@v4
- uses: pierredamien21/guadan@main
  with:
    chemin: .
    fuzz-duree: "120"
    cle-llm: ${{ secrets.GUADAN_API_KEY }}   # facultatif
```

Le rapport est publié en artefact `rapport-guadan`, un résumé s'affiche dans le job, et le job
échoue s'il y a un constat prouvé (`echouer-si-prouve: "false"` pour l'empêcher).

## Comment ça marche

```
dépôt ──copie──▶ dossier de travail (le dépôt d'origine n'est jamais modifié)
  │
  ├─ phase A, réseau : configuration CMake (Clang, ASan, UBSan), paquets apt
  │     └─ échec ? le LLM propose paquets et options, validés puis essayés (2 fois au plus)
  ├─ phase B, sans réseau : compilation, ctest, cppcheck, clang-tidy
  ├─ fuzzing : harnais fourni ou écrit par le LLM, libFuzzer, plantage minimisé puis rejoué
  ├─ LLM : tests déclencheurs bornés, tri expliqué des alertes
  └─ rapport.json + rapport.html
```

Chaque conteneur tourne sans variable d'environnement de l'hôte, sans capacité Linux, avec mémoire,
processus et durée limités. Le code analysé est considéré comme hostile : ses sorties sont
échappées dans le rapport, et un nom de test ne peut pas injecter de commande dans la commande de
reproduction.

## Résultats

Sur 12 bugs réels de [BugsC++](https://github.com/Suresoft-GLaDOS/bugscpp), versions boguée et
corrigée, sans LLM : 11 builds réussis, **5 bugs prouvés, soit 5 sur 5 là où les tests du projet
tournent sous CTest**, aucune fausse preuve. Les analyseurs statiques produisent 3 768 alertes sur
les mêmes versions. Les 6 bugs non retrouvés (exiv2, md4c) ont des tests hors CTest, que guadan ne
lance pas. Détail, méthode et limites : [docs/evaluation.md](docs/evaluation.md).

Sur quatre projets actuels (muparser, tinyxml2, cJSON, yaml-cpp), guadan n'a rien trouvé, ce qui
était attendu de projets fuzzés en continu par OSS-Fuzz ; il a surtout révélé une fausse preuve de
guadan lui-même, corrigée depuis : [docs/demo-projets.md](docs/demo-projets.md).

## Limites

- CMake seulement, Linux seulement ; les dépendances absentes de l'image doivent être installables
  par apt.
- Le fuzzing ne trouve que ce que son harnais atteint, dans la durée donnée.
- Les offres gratuites de modèles sont limitées (Groq : 200 000 jetons par jour) ; une analyse avec
  fuzzing et tri en consomme de 5 000 à 20 000.

## Documentation du projet

[Plan](docs/plan.md) · [Décisions](docs/decisions.md) · [Suivi](SUIVI.md) · [Journal](JOURNAL.md) ·
[Recherche](docs/research/)

## Remerciements

Les bugs de l'évaluation viennent de [BugsC++](https://github.com/Suresoft-GLaDOS/bugscpp) et
d'[ARVO](https://github.com/n132/ARVO-Meta), elles-mêmes issues d'OSS-Fuzz.
