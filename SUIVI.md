# Suivi d'avancement

État courant : **étape 3 en cours (T14)**. Dernière mise à jour : 2026-11-24.

Références : [fiche projet](docs/ideas/fiche-projet.md), [plan](docs/plan.md). Une case n'est cochée que lorsque le
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
- [x] Script de test du modèle prêt et banc contrôlé (`experiences/etape0/tester_modele.py`)
- [x] Un modèle gratuit testé sur l'écriture d'un test déclencheur (6 alertes) : 0 fausse preuve,
  5 fausses alertes bien écartées, vraie faille manquée (`experiences/etape0/resultats-groq/`)
- [x] Fuzzing court testé : 2 × 5 min sans trouver la faille
- [x] Décision : D-10 acceptée (le LLM trie et outille, les preuves viennent des tests et du fuzzing)

## Étape 1 — Socle sans LLM (détail des tâches : `docs/plan.md`)

- [x] T1. Squelette du paquet et intégration continue
- [x] T2. Image d'outils (arm64 et amd64)
- [x] T3. Projets d'exemple
- [x] T4. Bac à sable en deux phases
- [x] T5. Build avec sanitizers
- [x] T6. Tests sous sanitizers et lecture des rapports
- [x] T7. Analyseurs statiques
- [x] T8. Rapport JSON et HTML
- [x] Point de contrôle 1 : bout en bout sur les exemples et muparser, ARM64 et amd64 (CI 45233209609)

## Étape 2 — LLM et fuzzing

- [x] T9. Client LLM
- [x] T10. Réparation des échecs de build
- [x] T11. Fuzzing
- [x] T12. Tests déclencheurs, tentative bornée
- [x] T13. Tri expliqué des alertes
- [x] Point de contrôle 2 : rapports avec et sans clé

## Étape 3 — Évaluation

- [x] T14. Jeu de bugs figé (`eval/jeu.json`, 12 bugs BugsC++)
- [ ] T15. Évaluation automatisée
- [ ] T16. Comparaisons
- [ ] Point de contrôle 3 : chiffres publiés, limites écrites

## Étape 4 — Distribution

- [ ] T17. Image publiée : workflow prêt (`publier-image.yml`, sur étiquette), en attente de la licence et du nom
- [x] T18. Action GitHub (`action.yml`, essai vert : 1 prouvé sur debordement-tas, 0 sur sain)
- [ ] T19. Site vitrine

## Étape 5 — Finition

- [ ] T20. README écrit ; reste licence et nom définitif (à choisir par l'auteur)
- [ ] T21. Démonstration sur de vrais projets
- [ ] T22. Signalement d'un vrai bug

## Résultats marquants

- **guadan a trouvé seul un vrai défaut de muparser** (version `9e28c71`) : conversion d'un
  flottant hors limites en `int` dans `muParserBytecode.cpp:158` (entrée `88e8&&2`), par fuzzing
  avec un harnais écrit par Groq, en 90 à 120 s. Aucune des 38 alertes statiques ne le signale.
  Rejoué avec un harnais propre ; déjà corrigé en amont (`430ce5c`), donc rien à signaler.

## Points bloquants

Aucun.

## À retenir

- **Pas de carte graphique dédiée, 15,6 Go de mémoire** : un modèle local sera petit et lent.
  Les offres gratuites en ligne deviennent la piste principale.
- **BugsC++ ne compile pas avec AddressSanitizer** (seulement `-fsanitize-recover=all -g`) : ses
  bugs apparaissent comme des tests qui échouent ou des plantages, pas comme des rapports ASan.
  L'outil devra ajouter lui-même les sanitizers.
- **Quota Groq gratuit** : le test des 6 alertes a consommé environ 44 000 jetons et 10 min
  (attentes dues à la limite de 8 000 jetons/min). Avec 200 000 jetons/jour, environ 25 alertes
  par jour au plus.
- **cppcheck se trompe sur `1 << 31` en C++** : défini en C++, signalé à tort comme comportement
  indéfini. Une alerte n'est jamais une preuve, même quand elle parle de comportement indéfini.
- **Les analyseurs statiques ratent la vraie faille de muparser** : 40 alertes, aucune sur la
  ligne fautive. Argument central du projet, à mesurer à l'étape 3.
- **CMake 4 refuse les vieux `cmake_minimum_required`** (< 3.5) : premier cas réel d'échec de
  build à diagnostiquer ; contournement `-DCMAKE_POLICY_VERSION_MINIMUM=3.5`.
- À faire avant que d'autres utilisent le dépôt : choisir une licence.
