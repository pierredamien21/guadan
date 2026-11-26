# Journal de bord

Une entrée par séance de travail, la plus récente en haut. Chaque entrée dit ce qui a été fait,
ce qui a été constaté (avec la commande ou la source), et la prochaine action.

## 2026-11-26 — T21 : quatre projets actuels, une fausse preuve corrigée

**Fait**
- guadan avec Groq, tri et 120 s de fuzzing sur muparser `430ce5c`, tinyxml2 `8224e42`,
  cJSON `6d9f244`, yaml-cpp `f473f3b` : `docs/demo-projets.md`. Script vidéo : `docs/demo-video.md`.
- D-16 : 64 Mo de pile pour tout conteneur et dans la commande de reproduction.
- Évaluation relancée (exécution 45900229066) : tableau identique.

**Constaté**
- muparser, tinyxml2, yaml-cpp : 0 prouvé ; fuzzing de 0,2 à 74 millions d'exécutions sans
  plantage. yaml-cpp : 0 test (désactivés par défaut).
- cJSON : `stack-overflow` ASan dans `cJSON_Duplicate_rec` (test `misc_tests`) ; rejoué sans
  sanitizer (passe), ASan seul (passe), options de guadan à 8 Mo (déborde) et 64 Mo (passe) : fausse
  preuve due à l'instrumentation. Après D-16 : 0 prouvé, 19 tests sur 19.
- yaml_cpp-1 déborde toujours avec 64 Mo : récursion infinie, vrai bug.
- Harnais de Groq pour cJSON non compilable en 3 essais.

**Non vérifié**
- yaml-cpp avec `-DYAML_CPP_BUILD_TESTS=ON`.

**Prochaine action**
- Décisions de l'auteur : licence, nom, mise en ligne du site (Pages), publication de l'image.

## 2026-11-24 au 2026-11-26 — Étapes 3 et 4 : évaluation, action GitHub, site

**Fait**
- T14-T16 : jeu de 12 bugs BugsC++, workflow `evaluation.yml`, agrégateur, `docs/evaluation.md`.
- T17 : workflow de publication de l'image prêt, non déclenché (licence et nom attendus).
- T18 : action GitHub `action.yml`, essai vert.
- T19 : site `site/` (direction « La phrase est la mise en page »), images = captures de vrais
  rapports (`outils/captures.sh`), contrôlé à 1440, 768 et 390 px : 0 échec.
- README.

**Constaté**
- Trois fois le même piège : GitHub lance `bash -e`, et le code 1 de guadan coupait le script
  (évaluation, action). Corrigé par `|| code=$?`.
- Première évaluation : 7 cas sur 12 ne compilaient pas (vieux code face à clang 18). D'où D-15 :
  enveloppe du compilateur qui ajoute `-Wno-error` puis les drapeaux validés après ceux du projet ;
  réparation par le LLM étendue à la compilation.
- cpp_peglib : Catch 2.2.2 incompatible avec glibc 2.34+ (`MINSIGSTKSZ`), corrigé par
  `-DCATCH_CONFIG_NO_POSIX_SIGNALS`. cpp_peglib-6 : échec de lien (`peg::enabler`) non corrigé.
- Image dérivée périmée réutilisée après une mise à jour de l'image d'outils : son nom inclut
  maintenant l'identifiant de l'image de base.
- UBSan levé dans `stl_vector.h` : le lecteur remonte désormais au premier cadre du projet et
  normalise les chemins (`test/../peglib.h`).
- Évaluation finale (exécution 45574336860) : 11 builds, 5 bugs prouvés sur 12 (5 sur 5 avec tests
  CTest), 1 localisé, 3 768 alertes, aucune fausse preuve. exiv2 et md4c : tests hors CTest.

**Non vérifié**
- Groq contre un modèle local. Le LLM sur les 12 bugs (quota).

**Prochaine action**
- T21 : guadan sur 3 à 5 vrais projets open source actuels ; script de la vidéo.

## 2026-11-24 — Étape 2 : T9 à T13, point de contrôle 2

**Fait**
- T9 client LLM ; T10 réparation de la configuration (image dérivée avec paquets apt validés) ;
  T11 fuzzing libFuzzer (harnais fourni ou écrit par le LLM, minimisation, rejeu) ; T12 tests
  déclencheurs bornés (`--declencheurs N`) ; T13 tri groupé des alertes. Décisions D-13 et D-14.
- Nouvel exemple `parseur-fragile`. 49 tests.

**Constaté (vrai Groq, gpt-oss-120b)**
- `dep-manquante` réparé par `zlib1g-dev` : 611 jetons.
- `parseur-fragile` : harnais écrit, stack-buffer-overflow prouvé à `parseur.cpp:12` en 49 s,
  7 294 jetons. Une première réponse avait un JSON invalide (graines mal échappées) : lecture
  rendue tolérante.
- `alertes` : l'alerte réelle de la ligne 4 prouvée par un déclencheur, la division de la ligne 8
  refusée, tri en français : 2 418 jetons.
- muparser `9e28c71` : vrai défaut trouvé par fuzzing (UB `muParserBytecode.cpp:158`, entrée
  `88e8&&2`), rejoué avec un harnais propre sans OpenMP, absent de la version `430ce5c`. Le premier
  harnais bouchonnait OpenMP : D-14. Après correction, harnais propre, même défaut, 15 366 jetons.
- Faille de sécurité corrigée : nom de test non échappé dans la commande de reproduction.

**Non vérifié**
- Le comportement des déclencheurs (T12) sur un vrai projet avec le vrai modèle, au-delà de
  l'exemple `alertes`.

**Prochaine action**
- Étape 3 : T14, jeu de bugs figé.

## 2026-11-24 — Point de contrôle 1

**Constaté**
- CI 45233209609 (amd64) : tests rapides, image et suite Docker de bout en bout verts.
- Rapports HTML regardés dans le navigateur (bureau et 375 px) : deux défauts corrigés, le tableau
  d'alertes débordait sur téléphone, et « 0 / 0 tests échoués » s'affichait quand le build échoue
  (désormais « tests non lancés »).

**Prochaine action**
- Étape 2 : T9, client LLM.

## 2026-11-23 — Étape 1 : T1 à T8

**Fait**
- Plan de A à Z (`docs/plan.md`, T1 à T22), décisions D-11 et D-12.
- Paquet `guadan` : CLI, bac à sable deux phases, build ASan/UBSan, tests ctest sous sanitizers,
  lecture des rapports, cppcheck et clang-tidy, rapport JSON et HTML, pipeline.
- Image `docker/Dockerfile` (Ubuntu 24.04, clang 18) et `docker/verifier_image.sh`.
- 5 projets d'exemple ; CI : tests rapides, image amd64, suite Docker de bout en bout.

**Constaté**
- 27 tests passent en local (ARM64). CI amd64 : image et tests rapides verts ; la suite Docker
  de bout en bout vient d'être ajoutée, résultat non lu.
- muparser `9e28c71` : il fallait OpenMP dans l'image et `-fno-sanitize=vptr` (programme C lié à
  une bibliothèque C++ instrumentée). Analyse complète en 20 s : 0 prouvé, 38 alertes.

**Non vérifié**
- Le rendu du rapport HTML à l'œil (le navigateur intégré a refusé localhost).

**Prochaine action**
- Lire la CI de bout en bout, regarder le rapport HTML, puis étape 2 (T9).

## 2026-11-23 — Fin de l'étape 0

**Fait**
- D-10 acceptée par l'auteur : le LLM trie et outille, les preuves viennent des tests du projet
  et du fuzzing sous sanitizers.
- Fiche projet et suivi alignés sur D-10 (fuzzing ajouté au périmètre, étape 2 redéfinie).

**Bilan de l'étape 0**
- Machine : ARM64, Docker et clang dans WSL ; ASan fonctionne en natif, pas sous émulation.
- 6 bugs connus reproduits sur GitHub x86-64 ; ARVO 25402 rejoué en natif en recompilant.
- Groq gratuit retenu (D-08) ; il trie bien les fausses alertes mais ne prouve pas la vraie faille.

**Prochaine action**
- Étape 1 : conteneur isolé en deux phases, build CMake, tests du projet sous sanitizers.

## 2026-11-23 — Étape 0 : test de Groq sur les 6 alertes et fuzzing court

**Fait**
- Clé Groq enregistrée par l'utilisateur dans `/root/.bashrc` via une saisie masquée ; vérifiée
  sans affichage (préfixe et longueur) et acceptée par l'API (`/v1/models`, HTTP 200).
- `tester_modele.py` lancé sur les 6 alertes ; cas 6 rejoué avec `CreateRPN` en contexte.
- `fuzz_25402.sh` et `fuzz_harnais.cpp` : libFuzzer sur muparser vulnérable, 5 min sans aide,
  puis 5 min avec graines (`fuzz_graines/`) et dictionnaire (`fuzz.dict`).
- Résultats bruts copiés dans `experiences/etape0/resultats-groq/` ; proposition D-10.

**Constaté**
- Premier appel refusé : HTTP 403, `error code: 1010` (Cloudflare bloque l'agent `Python-urllib`).
  Corrigé avec un `User-Agent` explicite.
- Verdicts : les 6 cas se terminent en `refus_motivé`. Alertes 1 et 5 : deux tentatives de code
  sans rapport de sanitizer, puis refus. Aucune fausse preuve.
- Raisons justes vérifiées : alerte 1 (UBSan ne signale pas `1 << 31` en C++) ; alerte 2
  (`Assign` commence par `if (&a_Parser == this) return;`).
- Cas 6 (vraie faille) : refus, avec et sans `CreateRPN` en contexte, alors que la preuve de
  concept d'ARVO la déclenche.
- Fuzzing : aucun rapport ASan en 2 × 5 min (518 924 puis 523 323 exécutions).
- Coût : environ 44 000 jetons et 10 min pour les 6 alertes, à cause de la limite de 8 000
  jetons/min.

**Non vérifié**
- Les raisons données pour les alertes 3, 4 et 5 (plausibles, non contrôlées une à une).
- Un modèle plus fort, ou du fuzzing plus long, sur le cas 6.

**Prochaine action**
- L'auteur valide ou non D-10 ; c'est la dernière case de l'étape 0.

## 2026-11-23 — Étape 0 : script de test du modèle et contrôle du banc

**Fait**
- `experiences/etape0/tester_modele.py` : envoie chaque alerte à Groq (`openai/gpt-oss-120b`),
  compile la réponse avec ASan et UBSan contre muparser `9e28c71`, l'exécute, et ne compte une
  preuve que si le rapport du sanitizer cite le fichier et la ligne de l'alerte. 3 essais au plus,
  avec l'erreur du précédent renvoyée. Autotest : `python3 tester_modele.py --autotest`.
- Contrôle manuel de l'alerte 1 (`controle_alerte1.cpp`), puis ajout d'un 6e cas synthétique :
  l'emplacement réel de la faille, `muParserBase.cpp:1242`.

**Constaté**
- La clé Groq est introuvable dans WSL (`/root/.bashrc`, `.profile`, `/etc/environment`), dans
  les variables d'environnement Windows et dans un `.bashrc` côté Windows. Test du modèle non lancé.
- L'alerte 1 de cppcheck est fausse en C++ : UBSan signale `1 << 31` en C11 et C17, pas en C++11,
  C++17 ni C++20 (résultat `-2147483648`). Je l'avais d'abord classée « prouvable ».
- Le verdict « prouvé » s'applique au journal du témoin ARVO pour `muParserBase.cpp:1242`, pas
  pour la ligne 1487 : le banc sait reconnaître une vraie preuve.

**Non vérifié**
- Le comportement de Groq : aucun appel fait.
- Si l'alerte 2 (auto-affectation) est prouvable.

**Prochaine action**
- Enregistrer la clé dans WSL, puis lancer `tester_modele.py` sur les 6 alertes.

## 2026-11-23 — Étape 0 : modèles gratuits et banc de test des alertes

**Fait**
- Recherche sur les offres gratuites de modèles : `docs/research/modeles-gratuits.md`.
- Installation de clang 21.1.8, clang-tidy et cppcheck 2.19.0 dans WSL.
- `experiences/etape0/collecter_alertes.sh` : cppcheck et clang-tidy sur muparser à la version
  vulnérable d'ARVO 25402. `experiences/etape0/temoin_25402.sh` : rejoue la faille en natif.
- 5 alertes choisies pour le test du modèle : `experiences/etape0/alertes-choisies.md`.
- Décisions D-08 (Groq par défaut, action utilisable sans modèle) et D-09 (rejeu natif).

**Constaté**
- Relu à la source : GitHub Models retiré le 2026-07-30, API comprise ; limites gratuites de Groq
  pour gpt-oss-120b (30 req/min, 1 000/jour, 8K jetons/min, 200K/jour) ; Mistral sans API gratuite.
- 40 alertes sur muparser (13 cppcheck, 27 clang-tidy), aucune sur la ligne de la faille.
- CMake 4.2.3 refuse de configurer muparser à cette version sans
  `-DCMAKE_POLICY_VERSION_MINIMUM=3.5`.
- Lier une bibliothèque compilée par GCC avec un test compilé par Clang échoue
  (`undefined reference to __ubsan_vptr_type_cache`) : tout doit être compilé par le même
  compilateur.
- L'entrée du test ajouté par le correctif (`("") , 7`) change le résultat (7 contre une
  exception) sans erreur mémoire : un changement de comportement n'est pas une preuve.
- Avec la vraie preuve de concept d'ARVO : rapport ASan sur la version vulnérable seulement,
  sur ARM64, en 18 s.

**Non vérifié**
- Carte bancaire exigée ou non chez Groq ; utilisation des données pour l'entraînement chez Groq.
- Quotas gratuits exacts de Gemini.
- Les autres chiffres de la recherche, en dehors des trois faits relus.

**Prochaine action**
- L'utilisateur crée un compte Groq et une clé ; puis test du modèle sur les 5 alertes.

## 2026-11-20 — Étape 0 : reproduction de bugs connus sur GitHub

**Fait**
- Workflow `.github/workflows/reproduire-bugs.yml` : une tâche par bug, version boguée puis
  corrigée. Règle : reproduit seulement si la boguée échoue et la corrigée passe (BugsC++), ou
  si seule la version vulnérable produit un rapport ASan (ARVO).
- Bugs choisis : BugsC++ cpp_peglib-1 (cas 4), cpp_peglib-2 (cas 93, 94), exiv2-2 (cas 5) ;
  ARVO 25402 (muparser), 30087 (htslib), 19324 (ndpi), tous en ASan.
- Quatre exécutions pour corriger quatre erreurs du workflow, chacune confirmée par le journal :
  1. `git am` refusé faute d'identité Git (« Please tell me who you are ») ;
  2. le shell `bash -e` arrêtait le script ARVO au plantage attendu de la version vulnérable ;
  3. le conteneur BugsC++ (utilisateur `defects4cpp`) ne pouvait pas écrire dans le dossier :
     compilation de 10 à 15 s sans rien produire, contre environ 1 min après `chmod -R a+rwX` ;
  4. avec `-v`, `bugscpp test` n'écrit pas les fichiers `<cas>.test`.

**Constaté**
- Exécution 44723506671 : les 6 tâches réussissent.
- ARVO : `ERROR: AddressSanitizer: heap-buffer-overflow` sur la version vulnérable, rien sur la
  corrigée, pour les trois.
- BugsC++ : `failed` sur la boguée, `passed` sur la corrigée, pour les quatre cas. Pas de rapport
  ASan : cpp_peglib-1 échoue sur une assertion, cpp_peglib-2 sur `SIGSEGV`.
- Durée : environ 1 min par tâche ARVO, 3 min par tâche BugsC++.

**Non vérifié**
- Le contenu de `5.output` pour exiv2-2 est vide dans l'extrait ; seul le fichier `.test` a été lu.
- La reproductibilité sur d'autres bugs que ces six.

**Prochaine action**
- Recenser les offres gratuites de modèles en ligne, avec leurs limites.

## 2026-11-13 — Étape 0 : dépôt Git et GitHub

**Fait**
- `git init` sur la branche `main`, deux commits (cadrage et suivi, fins de ligne LF).
- Dépôt public créé avec `gh repo create guadan --public` et poussé.
- `idee.txt` exclu par `.gitignore` : notes brutes de départ, non publiées.

**Constaté**
- `gh repo view` : `pierredamien21/guadan`, PUBLIC, branche `main`, à jour avec `origin/main`.
- Les commits utilisent une adresse `users.noreply.github.com`, pas l'adresse personnelle.

**Non fait**
- Pas de licence, pas de README.

**Prochaine action**
- Écrire un workflow GitHub Actions qui reproduit 3 bugs de BugsC++ et 3 d'ARVO.

## 2026-11-13 — Étape 0 : test de l'émulation x86-64

**Fait**
- Installation de `qemu-user` et `qemu-user-binfmt` dans WSL (le paquet `qemu-user-static`
  n'existe plus sous Ubuntu 26.04).
- Test d'un dépassement de tas volontaire compilé avec `gcc -fsanitize=address` dans l'image
  `gcc:14`, en amd64 émulé puis en arm64 natif.

**Constaté**
- `docker run --platform linux/amd64 alpine uname -m` renvoie `x86_64` : l'émulation démarre.
- En amd64 émulé, le programme plante avant tout rapport :
  `AddressSanitizer: CHECK failed: sanitizer_allocator_primary32.h:292`, avec ou sans
  `ASAN_OPTIONS=detect_leaks=0`.
- En arm64 natif, le même programme donne le rapport attendu :
  `ERROR: AddressSanitizer: heap-buffer-overflow ... WRITE of size 16 ... main /tmp/t.c:3`.

**Non vérifié**
- ASan compilé avec Clang sous émulation, et une vraie image ARVO sous émulation.
- UBSan sous émulation (le programme de test ne le déclenche pas).

**Reste sur la machine**
- Paquets `qemu-user` et `qemu-user-binfmt`, et deux images `gcc:14` (amd64 et arm64).

**Prochaine action**
- Créer le dépôt GitHub public, puis reproduire les bugs connus sur une machine GitHub.

## 2026-11-13 — Étape 0 : installation de Docker et architecture des jeux de bugs

**Fait**
- Réparation d'une mise à jour de paquets restée interrompue dans WSL (`dpkg --configure -a`,
  paquets util-linux, mount, fdisk et associés).
- Installation de `docker.io` dans Ubuntu sous WSL, en root (`wsl -u root`).

**Constaté**
- Docker 29.1.3 actif, architecture aarch64 ; `docker run --rm hello-world` affiche
  « Hello from Docker! ».
- L'utilisateur par défaut de WSL est root : pas de groupe docker à configurer.
- `docker manifest inspect -v n132/arvo:25402-vul` : image amd64 uniquement.
- Le README de BugsC++ indique « CPU architecture: AMD64 ».
- `docker run --platform linux/amd64 alpine uname -m` échoue avec `exec format error` :
  aucune émulation x86-64 n'est installée.

**Non vérifié**
- Une seule image ARVO a été inspectée, pas l'ensemble.
- Le comportement d'AddressSanitizer sous émulation x86-64 (QEMU).

**Prochaine action**
- Décider : émulation locale ou exécution des jeux de bugs sur les machines GitHub x86-64.

## 2026-11-13 — Étape 0 : relevé de la machine

**Fait**
- Relevé par commandes PowerShell (`Get-CimInstance`, `wsl -l -v`) et dans WSL (`uname -m`,
  `command -v`).

**Constaté**
- Processeur Snapdragon X (ARM64), 8 cœurs, 15,6 Go de mémoire, carte graphique intégrée Adreno
  X1-45, pas de carte NVIDIA.
- WSL 2 avec Ubuntu 26.04.1 en aarch64, 7 Go de mémoire alloués, 951 Go libres.
- Dans WSL : cmake 4.2.3, gcc 15.2.0, python 3.14.4 présents ; docker, podman, clang, clang-tidy,
  cppcheck et qemu absents.
- Sous Windows : git et gh présents ; docker et ollama absents.
- Disques : 201 Go libres sur C, 400 Go libres sur E.

**Non vérifié**
- Si les images Docker de BugsC++ et d'ARVO existent en arm64.
- Le comportement d'AddressSanitizer sous émulation x86-64.

**Prochaine action**
- Installer Docker dans WSL (commande `sudo`, à lancer par l'utilisateur), puis vérifier
  l'architecture des images des jeux de bugs.

## 2026-11-13 — Cadrage

**Fait**
- Lecture critique des trois idées de `idee.txt` ; choix de l'idée d'audit de code.
- Recherche documentaire sur la cible : `docs/research/choix-cible-codeguardian.md`.
- Fiche projet, forme du rendu et plan sur trois mois : `docs/ideas/fiche-projet.md`.
- Mise en place des fichiers de suivi.

**Constaté**
- Gratuité d'Actions, du registre de conteneurs et de Pages pour un dépôt public, lue dans la
  documentation GitHub.
- Trois sources de la recherche relues directement (arXiv 2607.09979, Codex Security, BuildBench).
  Les autres chiffres de la recherche ne sont pas recontrôlés.

**Non fait / non vérifié**
- Aucun code. Aucun outil ni jeu de bugs installé ou lancé.
- Docker, WSL et la carte graphique de la machine non vérifiés.

**Prochaine action**
- Étape 0 : vérifier Docker, WSL et le matériel.
