# Journal des décisions

Une décision n'est jamais effacée. Si elle change, on ajoute une nouvelle entrée qui dit laquelle
elle remplace. Statuts : acceptée, remplacée par D-xx.

## D-01 — Cible : C/C++ avec CMake uniquement
- **Date** : 2026-11-13 — **Statut** : acceptée
- **Pourquoi** : preuve objective par les sanitizers, jeux de bugs réels exploitables, les outils
  grand public ne compilent pas le code.
- **Écarté** : Python seul (preuve moins objective), les deux langages (trop pour une personne).
- **Conséquence** : le build automatique C/C++ échoue souvent ; périmètre restreint et annoncé.
- **Source** : `docs/research/choix-cible-codeguardian.md`

## D-02 — Rapport à deux niveaux : prouvé, non prouvé
- **Date** : 2026-11-13 — **Statut** : acceptée
- **Pourquoi** : la règle « sans preuve, pas de constat » donnerait trop peu de résultats, la
  génération d'une preuve ne réussissant que dans 20 à 30 % des cas en un essai selon la recherche.
- **Écarté** : rapport limité aux seuls constats prouvés.
- **Conséquence** : le filtre « prouvé » est appliqué par du code, jamais par le LLM.

## D-03 — Pipeline déterministe, LLM à trois endroits
- **Date** : 2026-11-13 — **Statut** : acceptée
- **Pourquoi** : lancer CMake, CTest ou un analyseur ne demande pas de LLM.
- **Écarté** : les six agents spécialisés de l'idée d'origine.
- **Conséquence** : le LLM sert à diagnostiquer un échec de build, écrire un test déclencheur,
  expliquer un constat. LangGraph sert à l'enchaînement, à la reprise et à la validation humaine.

## D-04 — Rendu : outil Docker, action GitHub, site vitrine statique
- **Date** : 2026-11-13 — **Statut** : acceptée
- **Pourquoi** : utilisable par d'autres et gratuit à héberger sur un dépôt public.
- **Écarté** : service web où l'on colle son dépôt (coût des serveurs et du modèle, exécution de
  code inconnu), application de bureau (n'apporte rien de plus que le rapport HTML).

## D-05 — Modèle : tout service compatible avec le format d'API d'OpenAI, gratuit par défaut
- **Date** : 2026-11-13 — **Statut** : acceptée, modèle précis à choisir à l'étape 0
- **Pourquoi** : aucun coût pour l'auteur ni pour les utilisateurs, qui branchent un modèle local
  ou une offre gratuite.
- **Conséquence** : un modèle plus faible donne moins de constats prouvés ; la comparaison entre
  modèles entre dans l'évaluation.

## D-06 — Abandon du nom « CodeGuardian »
- **Date** : 2026-11-13 — **Statut** : acceptée, nom définitif à choisir
- **Pourquoi** : Rubrik et Akamai ont chacun un produit « Code Guardian ».
- **Conséquence** : « Guadan » sert de nom de travail ; sa disponibilité n'est pas vérifiée.

## D-07 — Jeux de bugs sur les machines GitHub x86-64, développement en natif ARM64
- **Date** : 2026-11-13 — **Statut** : acceptée
- **Pourquoi** : la machine de développement est en ARM64, ARVO et BugsC++ sont en amd64
  uniquement, et AddressSanitizer plante sous émulation QEMU (`CHECK failed:
  sanitizer_allocator_primary32.h:292`) alors qu'il fonctionne en natif ARM64.
- **Écarté** : émulation x86-64 locale (preuve par sanitizer impossible).
- **Conséquence** : il faut un dépôt GitHub public dès l'étape 0. L'outil doit fonctionner sur
  arm64 et sur amd64. Les petits dépôts d'exemple servent au développement local.

## D-08 — Modèle par défaut : Groq gratuit ; l'action GitHub fonctionne aussi sans modèle
- **Date** : 2026-11-23 — **Statut** : acceptée ; précise D-05 sans la remplacer
- **Pourquoi** : GitHub Models est retiré depuis le 2026-07-30, API comprise : le `GITHUB_TOKEN`
  ne donne plus accès à aucun modèle gratuit. Groq publie des limites gratuites utilisables
  (gpt-oss-120b : 30 req/min, 1 000 req/jour, 8 000 jetons/min, 200 000 jetons/jour). Mistral,
  Hugging Face, Together et Cerebras n'ont pas d'API gratuite sans paiement.
- **Écarté** : Gemini gratuit par défaut (quotas non publiés, données utilisées pour
  l'entraînement, et ses conditions réservent aux services payants les applications proposées
  à des utilisateurs de l'EEE, de Suisse et du Royaume-Uni). Il reste possible au choix de
  l'utilisateur. Modèle local par défaut (trop lent sans GPU) : gardé comme mode « rien ne sort ».
- **Conséquences** :
  - L'action GitHub demande une clé fournie par l'utilisateur, en secret. Sans clé, elle
    produit quand même le rapport sans LLM (build, tests, sanitizers, alertes non prouvées).
  - Le plafond de 8 000 jetons/min impose de tronquer les logs envoyés au modèle.
  - Le code de l'utilisateur part chez un tiers : l'outil doit le dire avant le premier appel.
- **Source** : `docs/research/modeles-gratuits.md`

## D-09 — Les bugs connus peuvent aussi être rejoués en natif, en recompilant depuis les sources
- **Date** : 2026-11-23 — **Statut** : acceptée ; complète D-07 sans la remplacer
- **Pourquoi** : `experiences/etape0/temoin_25402.sh` extrait la preuve de concept de l'image
  ARVO sans la lancer, recompile muparser avec Clang et ASan, et reproduit la faille sur ARM64
  en 18 s (`heap-buffer-overflow`, `READ of size 8`, `muParserBase.cpp:1242`).
- **Conséquence** : les images x86-64 restent réservées aux machines GitHub, mais le
  développement local peut utiliser de vrais bugs, à condition de recompiler le projet.

## D-10 — Rôle du LLM : trier et outiller, pas prouver seul chaque alerte
- **Date** : 2026-11-23 — **Statut** : acceptée le 2026-11-23 par l'auteur
- **Pourquoi** (expériences de l'étape 0, `experiences/etape0/`) :
  - Les 40 alertes de cppcheck et clang-tidy sur muparser ratent la vraie faille (ARVO 25402).
  - Groq `gpt-oss-120b` gratuit, sur 6 cas : aucune fausse preuve, et les 5 fausses alertes sont
    écartées avec une raison juste (vérifiée pour les alertes 1 et 2). Mais il déclare la vraie
    faille « impossible à déclencher », y compris avec la fonction fautive en contexte.
  - libFuzzer 5 min (avec ou sans graines et dictionnaire, environ 520 000 exécutions) ne la
    trouve pas non plus. La preuve de concept d'ARVO la déclenche en 18 s.
  - Le plafond gratuit de Groq (8 000 jetons/min) interdit d'envoyer un fichier de 1 900 lignes.
- **Proposition** :
  - Les preuves viennent d'abord des tests existants et de campagnes de fuzzing longues sous
    sanitizers (sur les machines GitHub), pas de tests écrits par le LLM alerte par alerte.
  - Le LLM sert à : diagnostiquer les échecs de build, écrire harnais, graines et dictionnaires
    de fuzzing, trier les alertes non prouvées en expliquant pourquoi, expliquer les preuves.
  - La génération de tests déclencheurs reste une tentative bornée, jamais une promesse.
  - D-02 (rapport prouvé / non prouvé, filtre appliqué par du code) est inchangée.
- **À trancher** : valider, ou retester avec un modèle plus fort avant de décider.

## D-11 — Pipeline en Python sans framework ; LangGraph seulement si l'étape 2 le justifie
- **Date** : 2026-11-23 — **Statut** : acceptée ; remplace la partie LangGraph de D-03
- **Pourquoi** : depuis D-10, le pipeline est déterministe et l'outil ne modifie jamais le dépôt
  de l'utilisateur ; la pause de validation humaine prévue par D-03 n'a donc pas d'objet. La
  reprise après interruption se fait en réutilisant les sorties déjà écrites dans le dossier de
  travail.
- **Écarté** : LangGraph pour tout le pipeline (dépendance lourde sans usage).
- **Conséquence** : LangGraph sera réexaminé pour la boucle LLM de l'étape 2 (essai, erreur,
  nouvel essai) ; s'il est retenu, il restera confiné au module `guadan/llm`.

## D-12 — Image d'outils sur Ubuntu 24.04, multi-architecture
- **Date** : 2026-11-23 — **Statut** : acceptée
- **Pourquoi** : Ubuntu 24.04 fournit clang 18 et CMake 3.28, qui accepte encore les vieux
  `cmake_minimum_required` ; CMake 4 (Ubuntu 26.04) les refuse (constaté à l'étape 0 sur
  muparser). arm64 pour la machine de l'auteur, amd64 pour GitHub et la plupart des utilisateurs.
- **Écarté** : image sur la dernière Ubuntu ; image amd64 seule.

## D-13 — Pas de LangGraph pour les boucles LLM
- **Date** : 2026-11-24 — **Statut** : acceptée ; tranche la question laissée ouverte par D-11
- **Pourquoi** : les quatre usages du LLM (réparation du build, harnais de fuzzing, déclencheurs,
  tri) sont des boucles de 1 à 3 essais, chacune en moins de 60 lignes de Python, sans état à
  reprendre entre deux exécutions. Un framework n'y ajouterait qu'une dépendance.
- **Conséquence** : guadan reste sans dépendance d'exécution (bibliothèque standard seulement).

## D-14 — Un harnais écrit par le LLM ne peut définir que les points d'entrée de libFuzzer
- **Date** : 2026-11-24 — **Statut** : acceptée ; protège D-02
- **Pourquoi** : sur muparser, gpt-oss-120b a bouchonné des fonctions d'OpenMP (`__kmpc_fork_call`
  vide) pour faire lier son harnais. Un harnais qui redéfinit un symbole de la bibliothèque peut
  fabriquer un plantage inexistant, donc une fausse preuve. Le défaut trouvé ce jour-là était réel
  (rejoué avec un harnais propre), mais rien ne le garantissait.
- **Conséquences** : consigne explicite ; liaison avec `-fopenmp` quand le projet l'utilise ; tout
  harnais qui définit une autre fonction à lien C que `LLVMFuzzerTestOneInput` ou
  `LLVMFuzzerInitialize` est refusé et renvoyé au modèle.

## D-15 — Le compilateur de guadan neutralise -Werror et accepte des drapeaux ajoutés en dernier
- **Date** : 2026-11-24 — **Statut** : acceptée
- **Pourquoi** : 7 des 12 cas de la première évaluation ne compilaient pas, même dans leur version
  corrigée : vieux code face à clang 18 (`register` interdit en C++17 dans exiv2, nouveaux
  avertissements changés en erreurs par le `-Werror` de cpp_peglib et du GoogleTest de yaml_cpp).
  Ce ne sont pas des défauts à signaler, et ils empêchent toute analyse. Un `-Wno-error` dans
  `CMAKE_CXX_FLAGS` ne suffit pas : il est placé avant le `-Werror` du projet, qui l'emporte.
- **Choix** : enveloppes `guadan-clang` et `guadan-clang++` dans l'image, qui ajoutent `-Wno-error`
  puis les drapeaux validés (`--drapeau`, ou proposés par le LLM, D-10) après toutes les options du
  projet. Drapeaux permis : `-W…`, `-std=…`, `-D…`, jamais `-f…` (rien ne peut toucher aux
  sanitizers). La réparation par le LLM couvre désormais aussi l'étape de compilation.
- **Vérifié** : exemple `vieux-code` ; Groq propose `-Wno-register` et C++14, 1 157 jetons.
