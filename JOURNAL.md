# Journal de bord

Une entrée par séance de travail, la plus récente en haut. Chaque entrée dit ce qui a été fait,
ce qui a été constaté (avec la commande ou la source), et la prochaine action.

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
