# Journal de bord

Une entrée par séance de travail, la plus récente en haut. Chaque entrée dit ce qui a été fait,
ce qui a été constaté (avec la commande ou la source), et la prochaine action.

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
