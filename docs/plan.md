# Plan de réalisation, de A à Z

Établi le 2026-11-23, après l'étape 0. Les cases à cocher vivent dans `SUIVI.md` (une par tâche,
même numéro). Ce fichier dit quoi construire, dans quel ordre, et comment on sait que c'est fini.

## Ce qu'on construit

`guadan analyse <dépôt>` : compile un dépôt C/C++ CMake dans un conteneur isolé, avec
AddressSanitizer et UBSan, lance ses tests et les analyseurs, puis écrit `rapport.json` et
`rapport.html` à deux niveaux (D-02). « Prouvé » ne vient que d'une exécution observée : test qui
échoue, rapport de sanitizer, plantage trouvé par fuzzing, échec de build. Le LLM, facultatif,
répare les builds, écrit des harnais de fuzzing et trie les alertes (D-10).

Le même outil sert partout : sur la machine de l'auteur (ARM64), dans l'image Docker publiée,
dans l'action GitHub, et pour l'évaluation.

## Architecture

```
guadan analyse <dépôt>                      (Python, sur l'hôte ou dans l'action GitHub)
  │
  ├─ copie du dépôt dans un dossier de travail (le dépôt d'origine n'est jamais modifié)
  │
  ├─ phase A, réseau autorisé ─ docker run guadan-outils
  │     paquets apt déclarés ou proposés par le LLM, cmake configure (FetchContent)
  │
  ├─ phase B, sans réseau ─ docker run --network none, mémoire, CPU, processus limités
  │     build avec sanitizers → ctest → clang-tidy, cppcheck → fuzzing (si harnais)
  │
  ├─ lecture des résultats : rapports ASan/UBSan, JUnit de ctest, alertes, plantages
  │
  ├─ LLM facultatif : réparer le build, écrire harnais et graines, trier les alertes
  │
  └─ rapport.json + rapport.html (le niveau « prouvé » est décidé par du code)
```

Arborescence visée :

```
guadan/            paquet Python : cli, bac_a_sable, build, tests, sanitizer, analyse,
                   rapport, llm, fuzz
docker/Dockerfile  image d'outils guadan-outils (clang, cmake, ninja, cppcheck, clang-tidy)
exemples/          petits projets CMake avec défauts connus, servent de tests de bout en bout
tests/             tests unitaires (pytest) et de bout en bout
eval/              jeu de bugs figé, scripts d'évaluation, résultats
site/              site vitrine (GitHub Pages)
action.yml         action GitHub
```

### Choix d'architecture (enregistrés dans `docs/decisions.md`)

- **D-11 — Python sans framework pour le pipeline.** Le pipeline est déterministe et ne modifie
  jamais le dépôt de l'utilisateur : la pause de validation humaine prévue par D-03 n'a pas
  d'objet. LangGraph n'est envisagé que pour la boucle LLM de l'étape 2, si elle le justifie.
  Remplace la partie LangGraph de D-03.
- **D-12 — Image d'outils sur Ubuntu 24.04** (clang 18, CMake 3.28) plutôt que la dernière
  Ubuntu : CMake 4 refuse les vieux projets (constaté à l'étape 0). Image multi-architecture
  arm64 et amd64.
- Bibliothèque standard de Python d'abord ; pytest seulement pour les tests.

## Tâches

Taille : S = 1-2 fichiers, M = 3-5 fichiers. Chaque tâche finit par un commit.

### Étape 1 — Socle sans LLM

**T1. Squelette du paquet et intégration continue** (M)
- `python -m guadan --help` fonctionne ; `guadan analyse` accepte un dépôt et un dossier de sortie.
- pytest tourne en local et dans un workflow GitHub à chaque push.
- Vérif : `python -m pytest` vert en local et sur GitHub.

**T2. Image d'outils** (S) — dépend de T1
- `docker/Dockerfile` construit `guadan-outils` en arm64 (local) et amd64 (GitHub).
- clang, clang-tidy, cppcheck, cmake, ninja, libFuzzer présents et versions affichées.
- Vérif : `docker run guadan-outils clang --version` sur les deux architectures.

**T3. Projets d'exemple** (M) — dépend de T2
- `exemples/sain` (tout passe), `exemples/debordement-tas` (un test déclenche ASan),
  `exemples/ub-entier` (un test déclenche UBSan), `exemples/dep-manquante` (exige zlib absent).
- Vérif : chacun se comporte comme annoncé, à la main, dans l'image.

**T4. Bac à sable en deux phases** (M) — dépend de T2
- Phase A avec réseau, phase B `--network none`, limites mémoire, CPU, processus, durée, et aucune
  variable d'environnement de l'hôte transmise.
- Le dépôt d'origine est monté en lecture seule et copié ; il n'est jamais modifié.
- Vérif : un test de bout en bout prouve qu'un accès réseau échoue en phase B.

**T5. Build avec sanitizers** (S) — dépend de T4
- Configuration Clang + ASan + UBSan, `compile_commands.json`, nouvel essai automatique avec
  `-DCMAKE_POLICY_VERSION_MINIMUM=3.5` si CMake le demande.
- Un échec de build devient un constat « prouvé » de type build, avec la commande et le log.
- Vérif : les 4 exemples, plus muparser `9e28c71`, donnent le résultat attendu.

**T6. Tests sous sanitizers et lecture des rapports** (M) — dépend de T5
- ctest avec sortie JUnit ; chaque test en échec devient un constat avec sa commande
  (`ctest -R '^nom$'`), le type (sanitizer, plantage, assertion) et, si présent, le fichier:ligne.
- `sanitizer.py` lit ASan et UBSan ; testé sur de vrais rapports capturés (ARVO, UBSan).
- Vérif : `debordement-tas` → 1 constat prouvé `heap-buffer-overflow` au bon fichier:ligne ;
  `sain` → 0.

**T7. Analyseurs statiques** (S) — dépend de T5
- clang-tidy et cppcheck sur `compile_commands.json`, alertes dédoublonnées, niveau « non prouvé ».
- Vérif : sur muparser, un nombre d'alertes du même ordre qu'à l'étape 0 (40).

**T8. Rapport JSON et HTML** (M) — dépend de T6, T7
- Schéma JSON documenté ; page HTML autonome, sans dépendance externe.
- Un test garantit qu'une alerte ne passe jamais au niveau « prouvé ».
- Vérif : rapport de `debordement-tas` ouvert et relu.

**Point de contrôle 1** : `guadan analyse` de bout en bout sur les 4 exemples et sur muparser,
en local (ARM64) et sur GitHub (amd64).

### Étape 2 — LLM et fuzzing

**T9. Client LLM** (S) — dépend de T8
- Format OpenAI, configuré par `GUADAN_API_URL`, `GUADAN_API_KEY`, `GUADAN_MODEL` (Groq par
  défaut, D-08). User-Agent explicite, attente sur HTTP 429, troncature sous 8 000 jetons.
- Avertissement avant le premier envoi de code ; sans clé, le rapport est produit sans LLM.
- Vérif : tests sur un faux serveur local ; aucun appel réseau dans les tests.

**T10. Réparation des échecs de build** (M) — dépend de T9
- Sur échec de la phase A, le log tronqué part au LLM, qui répond en JSON : paquets apt, options
  CMake. Chaque proposition est validée (liste blanche de formats) puis essayée ; deux essais au plus.
- Vérif : `dep-manquante` se construit après la proposition `zlib1g-dev`, et le rapport le dit.

**T11. Fuzzing** (M) — dépend de T9
- Le LLM écrit un harnais, des graines et un dictionnaire à partir des en-têtes publics ; le
  harnais est compilé avec libFuzzer et ASan, lancé pour une durée bornée ; un plantage est
  minimisé et devient un constat prouvé avec sa commande de reproduction.
- Vérif : `exemples/parseur-fragile` (défaut dépendant de l'entrée) planté en moins de 60 s.

**T12. Tests déclencheurs, tentative bornée** (S) — dépend de T9
- Reprise de `experiences/etape0/tester_modele.py` pour les N alertes les plus graves.
- Vérif : sur les 6 cas de l'étape 0, aucune fausse preuve.

**T13. Tri expliqué des alertes** (S) — dépend de T9
- Un appel groupé étiquette chaque alerte (« probable fausse alerte » ou « à vérifier ») avec une
  raison ; l'étiquette ne change jamais le niveau.
- Vérif : test unitaire sur ce dernier point ; rapport muparser relu.

**Point de contrôle 2** : rapports avec et sans clé sur les exemples et muparser.

### Étape 3 — Évaluation

**T14. Jeu de bugs figé** (M) — dépend du point de contrôle 2
- `eval/jeu.json` : environ 10 bugs BugsC++ basés sur CTest et 5 vulnérabilités ARVO, avec
  commits bogué et corrigé et test révélateur ; reproductibilité vérifiée par workflow.

**T15. Évaluation automatisée** (M) — dépend de T14
- Workflow GitHub en matrice, résultats JSON en artefacts, `eval/agreger.py` produit le tableau.
- Mesures : taux de build, alertes brutes contre constats prouvés, bugs retrouvés (prouvé sur la
  version boguée, absent sur la corrigée), fausses preuves, jetons consommés.
- Vérif : une seule commande régénère le tableau à l'identique.

**T16. Comparaisons** (S) — dépend de T15
- Outils seuls contre guadan ; avec et sans LLM ; Groq contre un modèle local si le temps le permet.
- Résultats et limites dans `docs/evaluation.md`.

**Point de contrôle 3** : chiffres publiés, limites écrites.

### Étape 4 — Distribution

**T17. Image publiée** (S) — dépend de T15
- Workflow de publication sur le registre GitHub, multi-architecture, déclenché par une étiquette
  de version.

**T18. Action GitHub** (S) — dépend de T17
- `action.yml` ; un workflow du dépôt l'utilise sur les exemples ; marche sans clé.

**T19. Site vitrine** (M) — dépend de T15
- `site/` sur GitHub Pages : galerie de rapports réels, chiffres de l'évaluation, démarrage rapide.

### Étape 5 — Finition

**T20. README, documentation, licence, nom définitif** (M)
**T21. Démonstration** : guadan sur 3 à 5 vrais projets open source, tri des résultats, script de
la vidéo.
**T22. Signalement d'un vrai bug** à un projet open source, si l'étape T21 en trouve un.

## Ce qui ne peut venir que de toi

| Quand | Quoi | Pourquoi |
|---|---|---|
| Avant T17 | Licence (MIT ou Apache-2.0 conseillées) | Sans licence, personne n'a le droit de réutiliser l'outil |
| Avant T17 | Nom définitif | L'image et l'action publiées portent le nom |
| T18 | Publication sur le Marketplace GitHub | Se fait dans l'interface GitHub, avec ton compte |
| T21 | Enregistrement de la vidéo | Ta voix, ton écran |
| T22 | Envoi du signalement de bug | Message public en ton nom |

Tout le reste avance sans t'attendre ; je m'arrête seulement sur ces points ou sur un vrai blocage.

## Risques

| Risque | Effet | Parade |
|---|---|---|
| Un vrai projet a besoin de dépendances absentes de l'image | Build impossible | Phase A avec paquets apt déclarés ou proposés par le LLM (T10) ; taux de build mesuré et publié |
| Quota Groq gratuit (8 000 jetons/min, 200 000/jour) | Lenteur, évaluation limitée | Troncature, appels groupés, mode sans LLM toujours complet |
| Fuzzing trop court pour trouver de vrais bugs | Peu de constats prouvés par fuzzing | Campagnes longues sur GitHub (gratuit en dépôt public), résultats présentés honnêtement |
| Code tiers malveillant | Compromission de la machine | Phase B sans réseau, limites, aucun secret transmis, dépôt monté en lecture seule |
| Différences ARM64 / amd64 | Résultat local différent de GitHub | Points de contrôle exécutés sur les deux architectures |
