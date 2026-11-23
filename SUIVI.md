# Suivi d'avancement

État courant : **étape 0 en cours ; prochaine action : tester Groq sur les 5 alertes (clé à créer par l'utilisateur)**. Dernière mise à jour : 2026-11-23.

Référence : [fiche projet](docs/ideas/fiche-projet.md). Une case n'est cochée que lorsque le
résultat a été constaté, pas quand le travail est « écrit ».

## Étape 0 — Vérifications (semaine 1)

- [x] WSL 2 fonctionne (Ubuntu 26.04, aarch64)
- [x] Docker installé et fonctionnel dans WSL (29.1.3, `hello-world` réussi)
- [x] Carte graphique et mémoire relevées (pour le modèle local)
- [x] Architecture des jeux de bugs vérifiée : ARVO et BugsC++ sont en amd64 uniquement
- [x] Émulation x86-64 testée : AddressSanitizer y plante, il fonctionne en natif ARM64
- [x] Décision D-07 : jeux de bugs sur les machines GitHub x86-64, développement en natif
- [x] Dépôt GitHub public créé : https://github.com/pierredamien21/guadan
- [x] 3 bugs de BugsC++ reproduits sur une machine GitHub x86-64 (cpp_peglib-1, cpp_peglib-2, exiv2-2 ;
  exécution 44723506671 : boguée échoue, corrigée passe)
- [x] 3 vulnérabilités d'ARVO reproduites sur une machine GitHub x86-64 (25402, 30087, 19324 ;
  rapport ASan sur la version vulnérable, aucun sur la corrigée)
- [x] Offres gratuites de modèles en ligne recensées, avec leurs limites (`docs/research/modeles-gratuits.md`, D-08)
- [x] 5 alertes réelles choisies et chaîne de preuve vérifiée en natif (`experiences/etape0/`, D-09)
- [ ] Un modèle gratuit testé à la main sur l'écriture d'un test déclencheur (au moins 5 alertes)
- [ ] Décision : continuer tel quel, ajuster le périmètre, ou changer de modèle

## Étape 1 — Socle sans LLM (semaines 2 à 4)

- [ ] Conteneur isolé en deux phases (dépendances avec réseau, build sans réseau)
- [ ] Build CMake avec `compile_commands.json`
- [ ] CTest, clang-tidy, cppcheck, AddressSanitizer, UBSan
- [ ] Rapport HTML et JSON avec la commande de reproduction de chaque constat

## Étape 2 — Partie LLM (semaines 5 à 7)

- [ ] Diagnostic d'échec de build
- [ ] Génération de tests déclencheurs, validés par exécution
- [ ] Rapport à deux niveaux : prouvé, non prouvé

## Étape 3 — Évaluation (semaines 8 à 9)

- [ ] Échantillon de bugs connus fixé et figé
- [ ] Chiffres : taux de build, alertes brutes contre constats prouvés, bugs retrouvés
- [ ] Comparaison avec les outils seuls et entre modèles
- [ ] Tout se régénère à l'identique en une commande

## Étape 4 — Distribution (semaines 10 à 11)

- [ ] Image Docker publiée
- [ ] Action GitHub publiée
- [ ] Site vitrine avec galerie de rapports

## Étape 5 — Finition (semaine 12)

- [ ] Nom définitif choisi et vérifié
- [ ] README
- [ ] Vidéo de démonstration
- [ ] Signalement d'un vrai bug à un projet open source

## Points bloquants

- **Clé Groq** : le test du modèle demande un compte Groq et une clé, à créer par l'utilisateur.

## À retenir

- **Pas de carte graphique dédiée, 15,6 Go de mémoire** : un modèle local sera petit et lent.
  Les offres gratuites en ligne deviennent la piste principale.
- **BugsC++ ne compile pas avec AddressSanitizer** (seulement `-fsanitize-recover=all -g`) : ses
  bugs apparaissent comme des tests qui échouent ou des plantages, pas comme des rapports ASan.
  L'outil devra ajouter lui-même les sanitizers.
- **Les analyseurs statiques ratent la vraie faille de muparser** : 40 alertes, aucune sur la
  ligne fautive. Argument central du projet, à mesurer à l'étape 3.
- **CMake 4 refuse les vieux `cmake_minimum_required`** (< 3.5) : premier cas réel d'échec de
  build à diagnostiquer ; contournement `-DCMAKE_POLICY_VERSION_MINIMUM=3.5`.
- À faire avant que d'autres utilisent le dépôt : choisir une licence.
