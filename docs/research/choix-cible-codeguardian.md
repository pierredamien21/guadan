# Choix de la cible de « CodeGuardian AI » : C/C++ (CMake), Python, ou les deux ?

Recherche documentaire du 13 novembre 2026.

**Légende de fiabilité**

- **[V]** : page primaire lue pendant cette recherche (documentation, dépôt, article, annonce de l'éditeur). Les pages ont été interrogées par extraction automatique ; les chiffres cités sont ceux renvoyés par la page, mais je n'ai pas relu chaque article en entier.
- **[E]** : seul l'extrait renvoyé par le moteur de recherche a été vu, sur le site primaire lui-même. Fiable sur le chiffre cité, pas sur son contexte.
- **[NC]** : non confirmé (source secondaire, ou souvenir non revérifié).

---

## 1. Verdict

**Recommandation : C/C++ avec CMake uniquement.** Confiance : **moyenne à bonne** (de l'ordre de 70 à 75 %).

- C'est le seul des trois choix où la règle « pas de preuve, pas de constat » repose sur un oracle objectif et binaire : un rapport AddressSanitizer/UBSan. En Python, la « preuve » se réduit à un test qui échoue, ce qui est beaucoup plus discutable.
- C'est aussi là que les jeux de données exécutables sont les meilleurs (ARVO, BugsC++, CyberGym), donc là qu'une évaluation chiffrée crédible est possible.
- Deux réserves importantes, qui empêchent une confiance plus haute :
  1. Le créneau « preuve par reproduction » **n'est plus vide** : OpenAI Codex Security, Rubrik Code Guardian, Greptile TREX et les systèmes de l'AIxCC le font déjà. La différenciation ne peut pas être « personne ne le fait », seulement « outil ouvert, local, spécialisé C/C++, avec des chiffres publiés ».
  2. La compilation automatique de dépôts C/C++ quelconques échoue souvent (27 à 66 % d'échec selon les travaux). Le projet n'est faisable seul que si le périmètre est restreint et annoncé comme tel.
- « Les deux langages » est le plus mauvais choix pour une personne seule : deux chaînes d'outils, deux oracles, deux évaluations, sans gain de différenciation.

---

## 2. Tableau comparatif

| Critère | C/C++ (CMake) | Python | Les deux |
|---|---|---|---|
| **Différenciation** | Bonne mais pas totale. Les outils de revue grand public lisent le code ou lancent des linters sans compiler. Les outils qui prouvent par exécution existent, mais sont fermés, payants ou en préversion (Codex Security, Rubrik), ou lourds (AIxCC). | Faible. Python est le langage le mieux couvert par tous les outils de revue ; aucun oracle équivalent aux sanitizers. | Dilue le message. |
| **Faisabilité seul** | Difficile sur des dépôts quelconques (34 à 73 % de builds réussis selon l'agent, 78 % pour CXXCrafter). Raisonnable si le périmètre est limité à CMake + dépendances déclarées. | Plus facile à installer (86 % pour Repo2Run sur 420 dépôts), mais le plus dur est ailleurs : définir ce qu'est un bug prouvé. | Double la charge. |
| **Évaluation chiffrée** | Forte. ARVO (plus de 6 000 vulnérabilités recompilables, images Docker), BugsC++ (209 à 215 bugs, Docker, MIT), CyberGym (1 507 tâches). Oracle : le sanitizer plante ou non. | Moyenne. BugsInPy (493 bugs) et SWE-bench (2 294 tâches) existent, mais SWE-bench mesure la correction d'un ticket, pas la détection d'un bug. | Deux protocoles à construire. |

Attention : les taux de build C/C++ et Python viennent de bancs d'essai différents, avec des critères de succès différents. Ils donnent un ordre de grandeur, pas une comparaison rigoureuse.

---

## 3. Détail par point

### 3.1 Concurrence : qui compile et exécute, qui lit seulement ?

| Outil | Ce qu'il fait réellement | Compile / exécute ? | C/C++ |
|---|---|---|---|
| **GitHub Copilot code review** | Revue par LLM « dans n'importe quel langage », avec collecte du contexte du dépôt par appels d'outils, exécutée sur des runners GitHub Actions [V] ([doc](https://docs.github.com/en/copilot/concepts/agents/code-review)). Intégration de CodeQL et d'ESLint annoncée en préversion en octobre 2025 [V] ([changelog](https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/)). | La doc ne dit nulle part qu'il compile le projet, lance les tests ou exécute le code [V]. | Oui (générique). |
| **CodeQL / code scanning** | Analyse statique par requêtes. Pour C/C++, C#, Java et Rust, la configuration par défaut crée la base **sans build** (`build-mode: none`) ; la doc prévient que c'est moins précis si les dépendances sont mal devinées ou si du code est généré au build [V] ([doc](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/manage-your-configuration/codeql-for-compiled-languages)). | Build possible (autobuild, manuel), jamais d'exécution du programme. | Oui. |
| **Copilot Autofix** | Propose des correctifs pour les alertes. Langages : C#, C/C++, Go, Java/Kotlin, Swift, JavaScript/TypeScript, Python, Ruby, Rust [V] ([doc](https://docs.github.com/en/code-security/responsible-use/security-and-quality-ai-features)). | Non pour l'utilisateur. GitHub évalue le système en interne avec un banc de test, mais la doc reconnaît que les correctifs peuvent être syntaxiquement faux, changer la sémantique ou ne pas corriger la faille [V]. | Oui. |
| **CodeRabbit** | LLM + linters. Pour C et C++ : Infer, Clang-Tidy, Cppcheck. Pour Python : Ruff, Pylint, Flake8 [V] ([catalogue](https://docs.coderabbit.ai/tools/list)). | Les pages lues ne mentionnent ni build, ni tests, ni sanitizers [V]. Comment clang-tidy et Infer tournent sans `compile_commands.json` : non documenté sur les pages lues [NC]. | Oui (linters). |
| **Sourcery** | Revue par LLM de « tout langage reconnu par GitHub », exemples cités : Python, TypeScript, Java, Go, Rust [E] ([site](https://www.sourcery.ai/)). | Rien n'indique une exécution [NC]. | Générique, non mis en avant. |
| **Qodo / PR-Agent** | PR-Agent : chaque commande fait **un seul appel LLM** sur le diff compressé [V] ([dépôt](https://github.com/The-PR-Agent/pr-agent)). Le projet a été donné à la communauté par Qodo [V]. | Non. | Générique. |
| **Snyk Code** | SAST. C/C++ pris en charge ; « ne nécessite ni compilation ni build », analyse le source directement [E] ([doc](https://docs.snyk.io/supported-languages/supported-languages-list/c-c++)). | Non. | Oui. |
| **SonarQube AI CodeFix** | Correctifs par LLM pour un sous-ensemble de règles en Java, JavaScript, TypeScript, Python, HTML, CSS, C#, C++ ; éditions Enterprise et Data Center [E] ([doc](https://docs.sonarsource.com/sonarqube-server/project-administration/ai-features/enable-ai-codefix)). | Non. | C++ partiel. |
| **Amazon CodeGuru Reviewer** | **Java et Python uniquement.** Fermé aux nouvelles associations de dépôts depuis le 7 novembre 2025 [V] ([doc](https://docs.aws.amazon.com/codeguru/latest/reviewer-ug/welcome.html)). | Non. | Non. |
| **Amazon Q Developer** | L'intégration GitHub est annoncée en fin de support ; fin des plugins IDE annoncée pour le 30 avril 2027 [E] ([doc](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/github-code-reviews.html), [page produit](https://aws.amazon.com/q/developer/)). | Non établi [NC]. | Non établi [NC]. |
| **Greptile** | Graphe du dépôt + LLM. C et C++ dans la liste des langages « pleinement pris en charge » [E] ([site](https://www.greptile.com/)). Depuis le 15 juin 2026, **TREX** lance le code dans un bac à sable jetable et joint la preuve au commentaire (journaux, captures, traces d'API, scripts) ; bêta publique [V] ([annonce](https://www.greptile.com/blog/trex)). | **Oui.** Mais l'annonce est orientée web/UI et ne mentionne ni C/C++, ni CMake, ni sanitizers [V]. | Lecture oui, exécution non démontrée. |

**Conclusion du point 1.** Les outils de revue généralistes lisent le diff (éventuellement tout le dépôt) et, au mieux, lancent des linters. Aucun de ceux examinés ne documente une compilation avec sanitizers ni un test généré qui reproduit le bug. Le C/C++ est partout « pris en charge » en lecture, mais Python est mieux servi en outillage (CodeGuru ne faisait que Java et Python). Seule exception dans cette catégorie : Greptile TREX, qui exécute, sans cibler le natif.

### 3.2 Travaux proches en C/C++ : le créneau « preuve par reproduction » est-il pris ?

**Produits qui valident par exécution**

- **OpenAI Codex Security** (ex-Aardvark). Tente de déclencher la vulnérabilité dans un bac à sable isolé pour confirmer qu'elle est exploitable ; avec un environnement configuré, produit des preuves de concept fonctionnelles [V] ([Aardvark](https://openai.com/index/introducing-aardvark/), [Codex Security](https://openai.com/index/codex-security-now-in-research-preview/)). Préversion de recherche pour ChatGPT Pro, Enterprise, Business et Edu. Projets cités : OpenSSH, GnuTLS, libssh, PHP, Chromium, donc du C/C++. Chiffres annoncés par l'éditeur : 92 % de rappel sur des dépôts de référence, 14 CVE attribuées, faux positifs réduits de plus de 50 % [V]. Chiffres non vérifiés par un tiers.
- **Rubrik Code Guardian**. Fait attaquer une copie du dépôt par un modèle d'Anthropic et ne remonte que les « chaînes exploitables confirmées ». Préversion privée, partenaires sélectionnés [V] ([page produit](https://www.rubrik.com/products/rubrik-code-guardian)).
- **Claude Security** (Anthropic). Analyse des dépôts et propose des correctifs ; réservé aux clients Claude Enterprise [E] ([fiche système](https://assets.claude.com/27d60918d218125e7504bc7354c4b4626ec56b11.pdf)). Validation par exécution : non vérifiée [NC].

**Recherche lourde**

- **Google Big Sleep** (ex-Naptime, Project Zero + DeepMind). Première vulnérabilité réelle trouvée par l'agent : un dépassement de pile exploitable dans SQLite, que ni OSS-Fuzz ni les tests du projet n'avaient trouvé [V] ([billet](https://projectzero.google/2024/10/from-naptime-to-big-sleep.html)). Outil interne, non distribué.
- **Google OSS-Fuzz-Gen**. Génère des harnais de fuzzing par LLM ; 30 bugs nouveaux signalés [V] ([dépôt](https://github.com/google/oss-fuzz-gen)). Premier essai : 14 projets sur 31 obtenaient un harnais qui compile et augmente la couverture [V] ([rapport](https://google.github.io/oss-fuzz/research/llms/target_generation/)). Open source, mais lié à l'infrastructure OSS-Fuzz.
- **DARPA AIxCC** (finale d'août 2025). 54 vulnérabilités synthétiques trouvées sur 63 (86 %), 43 corrigées, 18 vulnérabilités réelles dont 6 en C ; coût moyen d'environ 152 dollars par tâche ; les sept systèmes sont publiés en open source [V] ([DARPA](https://www.darpa.mil/news/2025/aixcc-results)). Exemple : Buttercup de Trail of Bits, 28 vulnérabilités, 19 correctifs [V] ([page](https://trailofbits.com/buttercup/)). Ces systèmes exigent une preuve de vulnérabilité (PoV), exactement le principe du projet. Ce sont des systèmes distribués conçus par des équipes entières.
- **LLM + analyse statique** : KNighter synthétise des vérificateurs pour le Clang Static Analyzer avec un agent de tri des faux positifs [E] ([arXiv 2503.09002](https://arxiv.org/html/2503.09002v2)). IRIS combine LLM et CodeQL [E] ([arXiv 2405.17238](https://arxiv.org/abs/2405.17238)).
- **Le travail le plus proche de la règle du projet** : une étude (Klieber, Svoboda, Flynn, Martins, juillet 2026) fait synthétiser par le LLM un programme qui déclenche dynamiquement le défaut signalé par l'analyseur statique. Résultat : un contrôle de validité a rejeté tous les déclencheurs visant une fausse alerte, donc un déclencheur valide est une preuve forte d'un vrai défaut [V] ([arXiv 2607.09979](https://arxiv.org/abs/2607.09979)). C'est une validation directe de l'idée centrale, sur des suites de test et non sur des dépôts réels.

**Conclusion du point 2.** Le créneau est occupé, mais pas par un outil que n'importe qui peut cloner et lancer sur son dépôt CMake : les produits sont fermés, payants ou en préversion ; la recherche est lourde. La place libre est étroite et précise : un outil ouvert, exécutable en local, spécialisé C/C++, qui publie ses propres chiffres. Annoncer l'idée comme inédite serait faux et facile à démentir par un recruteur informé.

### 3.3 Jeux de données utilisables comme vérité terrain

**C/C++**

| Jeu | Existe ? Taille | Licence | Reproductible ? | Entretien | Utilité ici |
|---|---|---|---|---|---|
| **ARVO** | Oui. Plus de 6 000 vulnérabilités réelles issues d'OSS-Fuzz, recompilables [E] ([arXiv 2606.17283](https://arxiv.org/html/2606.17283v1)). Chiffre secondaire : 6 138 dans 311 projets [NC]. | BSD-2-Clause [V] ([dépôt](https://github.com/n132/ARVO-Meta)) | Oui, images Docker réutilisables (confirmé par l'article CyberGym [V]). | Dernier push : 6 octobre 2026 [V] | **Très forte** : chaque cas a un PoC et un rapport de sanitizer. |
| **CyberGym** | Oui. 1 507 tâches, 188 projets, bâti sur ARVO/OSS-Fuzz, surtout des bugs mémoire C/C++ [V] ([arXiv 2506.02548](https://arxiv.org/pdf/2506.02548)). | Non vérifiée [NC] | Oui (Docker). | 2025-2026 | **Forte** : la tâche est précisément « générer un PoC qui reproduit ». Donne des chiffres de comparaison. |
| **BugsC++** | Oui. 209 bugs dans 22 projets selon l'article ASE 2023 [E] ([ACM](https://dl.acm.org/doi/10.1109/ASE56229.2023.00208)) ; 215 selon le README actuel [V]. | MIT [V] ([dépôt](https://github.com/Suresoft-GLaDOS/bugscpp)) | Oui : Docker, AMD64, Python 3.9 ou plus. | Dernier push : 25 mars 2024 ; 64 étoiles [V]. Peu actif. | **Forte** pour les bugs fonctionnels (tests qui échouent). |
| **Magma** | Oui. Version 1.0 : 118 bugs dans 7 cibles [E] ([arXiv 2608.28016](https://arxiv.org/html/2608.28016v1)). Taille actuelle non vérifiée [NC]. | Non détectée par GitHub [V] ; à vérifier | Oui, mais pensé pour comparer des fuzzers. | Dernier push : 11 octobre 2026 [V] ([dépôt](https://github.com/HexHive/magma)) | Moyenne. |
| **ManyBugs** | Oui. 185 défauts dans 9 programmes C [E] ([site](https://repairbenchmarks.cs.umass.edu/)). | Non détectée [V] | Archives par scénario ; environnements anciens. Docker : non vérifié [NC]. | Dernier push du dépôt : septembre 2019 [V] ([dépôt](https://github.com/squaresLab/ManyBugs)) | Faible (vieux). |
| **Juliet C/C++ 1.3 (NIST SARD)** | Oui. 118 CWE [E] ([NIST](https://samate.nist.gov/SARD/test-suites/112)). Nombre de cas (environ 64 000) non revérifié [NC]. | Non vérifiée [NC] | Oui, facile à compiler. | Figé. | **Faible comme preuve** : synthétique, et un LLM (o4-mini) peut souvent retrouver l'identité des cas, donc mémorisation [V] ([arXiv 2607.09979](https://arxiv.org/abs/2607.09979)). Bon pour des tests de non-régression. |
| **CVEfixes** | Oui. 5 365 CVE, 1 754 projets, 5 495 commits correctifs (version initiale, juin 2021) [V] ([arXiv 2107.08760](https://arxiv.org/abs/2107.08760)). Multi-langage. | « Other » selon GitHub [V] | Non exécutable : des commits, pas d'environnement. | Dernier push : juillet 2024 [V] | Faible ici. |
| **Big-Vul** | Oui [V] ([dépôt](https://github.com/ZeoVan/MSR_20_Code_vulnerability_CSV_Dataset)). | MIT | Non exécutable (fonctions en CSV). | Dernier push : mars 2021 | Faible, étiquettes bruitées (voir PrimeVul). |
| **PrimeVul** | Oui [V] ([dépôt](https://github.com/DLVulDet/PrimeVul)). L'article montre que les anciens jeux surestiment les modèles : 68,26 % de F1 sur BigVul contre 3,09 % sur PrimeVul [V] ([arXiv 2403.18624](https://arxiv.org/abs/2403.18624)). | MIT | Non exécutable (niveau fonction). | Dernier push : septembre 2024 | Faible ici, utile comme mise en garde. |

**Python**

| Jeu | Existe ? Taille | Licence | Reproductible ? | Entretien | Utilité ici |
|---|---|---|---|---|---|
| **BugsInPy** | Oui. 493 bugs réels, 17 projets [V] ([arXiv 2401.15481](https://arxiv.org/abs/2401.15481)). | Aucune licence détectée [V] ([dépôt](https://github.com/soarsmu/BugsInPy)) | Docker pris en charge [V]. Fiabilité réelle des environnements anciens : non vérifiée [NC]. | Dernier push : février 2026 ; 155 étoiles [V] | Moyenne. |
| **SWE-bench** | Oui. 2 294 tâches, 12 dépôts Python ; sous-ensemble Verified de 500 [V] ([site](https://www.swebench.com/)). | MIT [V] ([dépôt](https://github.com/SWE-bench/SWE-bench)) | Oui, Docker [V]. | Actif (septembre 2026) | Faible ici : mesure la résolution d'un ticket connu, pas la découverte d'un bug. |

**Conclusion du point 3.** Les jeux exécutables avec oracle objectif sont du côté C/C++. Plan d'évaluation réaliste : un sous-ensemble d'ARVO ou de CyberGym pour les bugs mémoire, BugsC++ pour les bugs fonctionnels, Juliet uniquement en test de fumée.

### 3.4 Faisabilité : compiler automatiquement des dépôts C/C++

- **CXXCrafter** (FSE 2025) : les projets C/C++ populaires rencontrent en moyenne cinq erreurs avec les seules commandes de build par défaut ; l'agent atteint 78 % de succès. Sur le Top 100 : 72 projets compilés par l'agent et à la main, 3 par l'agent seul, 14 à la main seulement [V] ([arXiv 2505.21069](https://arxiv.org/abs/2505.21069)).
- **Build-Bench** (2025-2026) : 148 dépôts vérifiés à la main parmi 385 dépôts C/C++ tirés au hasard sur GitHub. Succès validé strict [V] ([arXiv 2509.25248](https://arxiv.org/html/2509.25248v2)) :
  - outils à règles : 10,1 % (GHCC) et 6,0 % (Assemblage) ;
  - un seul appel LLM : 30 à 37 % ;
  - CompileAgent : 50,7 % ;
  - meilleur agent (OSS-Build-Agent avec Claude 3.7 Sonnet) : 67,6 % strict, 73,0 % souple.
  - Causes d'échec : paquets manquants ou versions incompatibles, dépannage insuffisant, options de build inventées.
- **OSS-Fuzz** : une génération de scripts de build par agent sur 225 projets a produit 88 scripts fonctionnels, soit 39 % [E] ([billet](https://blog.oss-fuzz.com/posts/oss-fuzz-integrations-via-agent-based-build-generation/)).
- **Python, pour comparaison** : Repo2Run construit un environnement exécutable pour 361 dépôts sur 420, soit 86,0 % [E] ([arXiv 2502.13681](https://arxiv.org/abs/2502.13681)).

Données introuvables pendant cette recherche : un taux de réussite publié **spécifique à CMake**, et un taux spécifique à vcpkg ou Conan. L'hypothèse « CMake seul est nettement plus facile » est plausible mais non chiffrée [NC].

**Conclusion du point 4.** Sur des dépôts quelconques, il faut s'attendre à un échec de build sur un quart à deux tiers des cas, même avec un agent. Python s'installe plus facilement. C'est le principal argument contre C/C++, et il se traite par le périmètre, pas par plus de code.

### 3.5 Faux positifs des analyseurs statiques C/C++ et tri par LLM

**Bruit des analyseurs**

- Sur des programmes réels, les analyseurs statiques C de pointe **manquent entre 47 % et 80 %** des vulnérabilités, alors qu'ils brillent sur les bancs synthétiques (Lipp, Banescu, Pretschner, ISSTA 2022) [E] ([ACM](https://dl.acm.org/doi/10.1145/3533767.3534380)).
- Sur 815 commits ayant introduit 319 vulnérabilités réelles dans 92 projets C/C++ : un seul outil signale la fonction vulnérable dans 52 % des cas, **au moins 76 % des alertes dans les fonctions vulnérables sont sans rapport** avec la faille, et 22 % des commits ne sont détectés par aucun outil [V] ([arXiv 2407.12241](https://arxiv.org/abs/2407.12241)).
- Chez Tencent, sur 433 alertes d'un analyseur interne : 328 faux positifs pour 105 vrais, soit 76 % de fausses alertes, et 10 à 20 minutes d'inspection humaine par alerte [V] ([arXiv 2601.18844](https://arxiv.org/abs/2601.18844)). Le langage n'est pas précisé dans le résumé.
- Sur 8 918 programmes C++, l'analyse statique (cppcheck, clang-tidy) et l'analyse dynamique (ASan/UBSan) détectent des classes de défauts largement différentes ; aucune ne suffit seule [V] ([arXiv 2607.00107](https://arxiv.org/abs/2607.00107)).

Donnée introuvable : **un taux de faux positifs publié propre à clang-tidy ou à cppcheck** sur de grands projets réels. Les chiffres ci-dessus portent sur des « analyseurs statiques C/C++ » en général ou sur un outil interne. Cppcheck affiche seulement l'objectif « aucun faux positif » [E] ([site](https://cppcheck.sourceforge.io/)).

**Tri par LLM**

- Tencent : les techniques hybrides LLM + analyse statique éliminent 94 à 98 % des faux positifs avec un rappel élevé, pour 0,0011 à 0,12 dollar et 2 à 110 secondes par alerte [V] ([arXiv 2601.18844](https://arxiv.org/abs/2601.18844)).
- Klieber et al. : au moins 98 % de rappel et 94,8 % de spécificité sur Juliet, FormAI et SV-COMP avec vérification de cohérence entre plusieurs passes. Les auteurs signalent eux-mêmes la mémorisation de Juliet [V] ([arXiv 2607.09979](https://arxiv.org/abs/2607.09979)).
- Limite côté génération de preuve : sur CyberGym, les meilleurs agents ne reproduisaient qu'environ 20 % des vulnérabilités à partir de leur description [V] ([arXiv 2506.02548](https://arxiv.org/pdf/2506.02548)) ; un modèle plus récent atteint 28,9 % en un essai et 66,7 % en 30 essais [E] ([Berkeley RDI](https://rdi.berkeley.edu/blog/cybergym/)). Sans description, 3,5 % seulement [V].

**Conclusion du point 5.** Le problème du bruit est réel et chiffré, et le tri par LLM marche bien en publication. En revanche, produire une preuve exécutable reste difficile : avec la règle stricte, le rapport contiendra peu de constats.

### 3.6 Le nom « CodeGuardian »

Le nom est **déjà pris, y compris sur le même créneau** :

- **Rubrik Code Guardian** : produit commercial de sécurité du code par IA, dont l'argument est justement de ne remonter que des failles prouvées exploitables [V] ([page produit](https://www.rubrik.com/products/rubrik-code-guardian)).
- **Akamai Code Guardian** (propulsé par Apiiro) : sécurité du développement assisté par IA [E] ([fiche](https://www.akamai.com/resources/solution-brief/akamai-code-guardian-solution-brief)).
- **GitHub** : 406 dépôts contiennent « codeguardian » dans leur nom. Aucun n'est notable (maximum 11 étoiles), mais plusieurs sont des relecteurs de code par IA, dont un « CodeGuardianAI » et un « CodeGuardian AI, an autonomous agentic PR reviewer » [V] ([recherche](https://github.com/search?type=repositories&q=codeguardian%20in%3Aname)).
- Un domaine `codeguardian.info` est utilisé par un bot GitHub/Discord [V] (même recherche).

Non vérifié : dépôts de marque (INPI, EUIPO, USPTO), disponibilité des noms de paquet PyPI/npm.

**Conclusion du point 6.** Changer de nom. « CodeGuardian AI » est à la fois banal, introuvable dans un moteur de recherche et en collision avec deux éditeurs connus.

---

## 4. Risques du choix C/C++ et moyens de les réduire

| Risque | Gravité | Réduction |
|---|---|---|
| **Le build échoue sur le dépôt de l'utilisateur.** | Haute | Périmètre annoncé : CMake, Linux, dépendances déclarées (vcpkg ou Conan en mode manifeste, ou paquets système listés). Refuser proprement le reste avec un diagnostic. Publier le taux de build réussi comme une métrique, pas le cacher. |
| **Trop peu de constats avec la règle stricte** (20 à 30 % de reproduction en un essai dans la littérature). | Haute | Deux niveaux dans le rapport : « prouvé » (commande de reproduction) et « non prouvé » en annexe, clairement séparés. Réutiliser les tests et harnais existants du projet. Partir des alertes statiques pour cibler la génération de tests. Plusieurs essais par constat. |
| **L'idée n'est pas nouvelle** (Codex Security, Rubrik, AIxCC, Greptile TREX). | Moyenne | Ne pas la présenter comme telle. Se positionner sur : ouvert, local, C/C++/CMake, chiffres reproductibles. Citer ces travaux dans le README. |
| **Évaluation contestable** (mémorisation des jeux publics par le LLM). | Moyenne | Éviter Juliet comme résultat principal. Prendre dans ARVO des cas postérieurs à la date de coupure du modèle. Publier le protocole et les scripts. |
| **Exécuter du code non fiable.** | Haute | Conteneur sans réseau, utilisateur non root, limites de CPU, mémoire et durée, système de fichiers jetable. |
| **Coût en appels LLM.** | Moyenne | Budget par dépôt, cache, tri statique avant toute génération. |
| **Poste de développement sous Windows.** | Faible | Tout faire tourner dans Docker ou WSL ; les jeux de données ciblent Linux AMD64. |
| **Jeux de données peu entretenus** (BugsC++ : dernier push en mars 2024). | Faible | Figer les versions d'images ; commencer par vérifier que 10 à 20 cas se reproduisent avant de s'engager. |

---

## 5. Ce qui n'a pas pu être vérifié

1. Aucun outil n'a été installé ni lancé. Tout repose sur la documentation et les articles.
2. Comment CodeRabbit exécute Clang-Tidy et Infer (avec ou sans build, avec ou sans `compile_commands.json`).
3. Ce qu'exécute exactement Copilot code review sur ses runners au-delà de CodeQL et des linters ; la doc ne dit pas qu'il compile, mais ne dit pas non plus le contraire.
4. Si Greptile TREX fonctionne sur du C/C++ natif.
5. Le fonctionnement interne de Claude Security et de Rubrik Code Guardian (validation par exécution, langages).
6. L'état actuel d'Amazon Q Developer pour la revue de code et ses langages.
7. Un taux de faux positifs publié propre à clang-tidy ou cppcheck : non trouvé.
8. Un taux de réussite de build automatique propre à CMake, vcpkg ou Conan : non trouvé.
9. Le nombre exact de cas de Juliet 1.3, la taille actuelle de Magma, les licences de Magma, ManyBugs, CyberGym et Juliet.
10. Le chiffre « 6 138 vulnérabilités dans 311 projets » pour ARVO (source secondaire) ; seul « plus de 6 000 » vient de l'article.
11. La reproductibilité réelle des images Docker de BugsC++, BugsInPy et ARVO aujourd'hui.
12. Les chiffres annoncés par les éditeurs (OpenAI : 92 % de rappel ; Greptile ; Rubrik) ne sont confirmés par aucun tiers.
13. Les dépôts de marque sur « Code Guardian » et la disponibilité du nom sur PyPI/npm.
14. Les pages ont été lues par extraction automatique ciblée. Un chiffre peut avoir été sorti de son contexte ; relire l'article avant de le citer publiquement.
