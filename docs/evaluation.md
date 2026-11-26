# Évaluation

Mesures de guadan sur des bugs réels, publiées avec leurs limites. Tout se régénère : voir
« Reproduire » en bas de page.

## 1. Douze bugs de BugsC++, sans LLM

### Méthode

- **Jeu figé** : [`eval/jeu.json`](../eval/jeu.json), 12 bugs de [BugsC++](https://github.com/Suresoft-GLaDOS/bugscpp)
  dans 4 projets CMake : cpp_peglib (1, 2, 3, 6), yaml_cpp (1, 10), exiv2 (2, 3, 4, 5), md4c (1, 2).
  Choisis parmi les projets CMake de BugsC++, en privilégiant les défauts mémoire.
- **Pour chaque bug**, guadan analyse la version boguée et la version corrigée, que BugsC++ fournit
  (`bugscpp checkout`), sans LLM et sans fuzzing.
- **Où** : machines GitHub x86-64, workflow [`evaluation.yml`](../.github/workflows/evaluation.yml),
  exécution `45574336860` du 2026-11-25, sur le commit `dd0d3b7`.
- **Réglages déclarés à la main**, comme le ferait un utilisateur qui connaît son projet :
  - exiv2 : paquets `libexpat1-dev zlib1g-dev`, drapeau `-Wno-register` (mot-clé interdit en C++17) ;
  - cpp_peglib : drapeau `-DCATCH_CONFIG_NO_POSIX_SIGNALS` (Catch 2.2.2 embarqué, incompatible avec
    glibc 2.34 et plus).
  Le LLM sait proposer ce genre de réglage (vérifié sur `exemples/vieux-code`), mais il n'a pas été
  utilisé ici : le quota gratuit ne couvre pas 24 analyses avec tri, et la mesure doit être
  reproductible sans clé.

Définitions :

- **Bug retrouvé** : au moins un constat prouvé sur la version boguée qui n'existe pas sur la version
  corrigée.
- **Localisé** : un tel constat, ou un cadre de sa pile, tombe dans une ligne modifiée par le
  correctif (± 2 lignes), lue dans le patch de BugsC++.
- **Alertes dans la zone du bug** : alertes de cppcheck ou clang-tidy qui tombent dans cette même
  zone, c'est-à-dire ce que les outils seuls auraient pu montrer.

### Résultats

| Cas | Build | Tests CTest | Prouvés | Bug retrouvé | Localisé | Échecs déjà présents | Alertes | Alertes dans la zone du bug |
|---|---|---|---|---|---|---|---|---|
| cpp_peglib-1 | oui | 1 | 1 | oui | non | 0 | 393 | 0 |
| cpp_peglib-2 | oui | 1 | 1 | oui | oui | 0 | 384 | 0 |
| cpp_peglib-3 | oui | 1 | 1 | oui | non | 0 | 391 | 0 |
| cpp_peglib-6 | non | 0 | 1 | non | non | 1 | 0 | 0 |
| exiv2-2 | oui | 0 | 0 | non | non | 0 | 558 | 1 |
| exiv2-3 | oui | 0 | 0 | non | non | 0 | 557 | 0 |
| exiv2-4 | oui | 0 | 0 | non | non | 0 | 554 | 0 |
| exiv2-5 | oui | 0 | 0 | non | non | 0 | 552 | 1 |
| md4c-1 | oui | 0 | 0 | non | non | 0 | 116 | 0 |
| md4c-2 | oui | 0 | 0 | non | non | 0 | 116 | 0 |
| yaml_cpp-1 | oui | 1 | 1 | oui | non | 0 | 78 | 0 |
| yaml_cpp-10 | oui | 1 | 1 | oui | non | 0 | 69 | 0 |

Rapports bruts : [`eval/resultats/`](../eval/resultats/) (`rapport.json` par version, patch du bug).

### Lecture

- **11 builds sur 12.** cpp_peglib-6 échoue à l'édition de liens dans ses deux versions
  (`undefined reference to peg::enabler`, vieux code face à clang 18 et aux informations de
  débogage) ; aucun drapeau permis ne le corrige. Cet échec apparaît comme « déjà présent » : il
  existe aussi sur la version corrigée, ce n'est donc pas une fausse preuve du bug.
- **5 bugs retrouvés sur 12, et 5 sur 5 là où les tests du projet tournent sous CTest.** Tous les
  cas de cpp_peglib (sauf le 6) et de yaml_cpp sont retrouvés. Les six cas d'exiv2 et de md4c ne le
  sont pas, parce que ces projets lancent leurs tests par leurs propres scripts (`python runner.py`,
  commandes shell) et non par CTest : guadan n'a rien à exécuter.
- **Nature des preuves.** cpp_peglib-2 : `reference binding to null pointer` relevé par UBSan.
  yaml_cpp-1 : `stack-overflow` relevé par ASan. Les trois autres sont des tests qui échouent sans
  rapport de sanitizer : des bugs de logique, prouvés par le test, mais sans emplacement.
- **1 bug localisé sur 5.** Seul cpp_peglib-2 donne une pile qui traverse la zone du correctif. Pour
  yaml_cpp-1, la pile s'arrête dans GoogleTest, au fond d'une récursion. Les trois échecs de logique
  n'ont pas d'emplacement.
- **Outils seuls : 3 768 alertes, dont des alertes dans la zone du bug pour 2 cas sur 12** (exiv2-2
  et exiv2-5), chacune noyée parmi environ 555 alertes. Aucune ne dit laquelle compte. guadan les
  garde au niveau « non prouvé ».
- **Aucune fausse preuve** : aucun constat de la version boguée n'est attribué au bug alors qu'il
  existe aussi dans la version corrigée.

## 2. Avec un LLM gratuit (Groq, gpt-oss-120b)

Mesuré en local (ARM64), les 2026-11-23 et 2026-11-24. Ces cas montrent ce que le LLM ajoute ;
ce n'est pas un échantillon statistique.

| Projet | Ce que le LLM a fait | Résultat | Jetons |
|---|---|---|---|
| `exemples/dep-manquante` | Réparation de la configuration : `zlib1g-dev` | Build et test réussis | 611 à 807 |
| `exemples/vieux-code` | Réparation de la compilation : `-Wno-register`, C++14 | Build et test réussis | 980 à 1 157 |
| `exemples/parseur-fragile` | Harnais de fuzzing, graines | `stack-buffer-overflow` prouvé à `parseur.cpp:12` après 9 170 exécutions | 7 294 à 8 000 |
| `exemples/alertes` | Test déclencheur et tri des 3 alertes | Alerte réelle de la ligne 4 prouvée, division de la ligne 8 refusée à juste titre | 2 334 à 2 418 |
| muparser `9e28c71` | Harnais de fuzzing et tri de 38 alertes | Comportement indéfini prouvé à `muParserBytecode.cpp:158` (entrée `88e8&&2`), absent des 38 alertes | 15 366 à 20 695 |

Le défaut de muparser a été confirmé en rejouant l'entrée avec un harnais écrit à la main, sans
OpenMP, et il est corrigé dans la version actuelle (`430ce5c`). Le premier harnais de Groq
bouchonnait des fonctions d'OpenMP : d'où la règle D-14, qui refuse tout harnais redéfinissant un
symbole.

Test préalable (étape 0, `experiences/etape0/`) : sur 6 alertes, Groq n'a produit aucune fausse
preuve et a écarté 5 fausses alertes avec une raison juste, mais il a déclaré la vraie faille d'ARVO
25402 impossible à déclencher. D'où D-10 : le LLM outille, il ne prouve pas.

## 3. Comparaisons (T16)

| Question | Réponse mesurée |
|---|---|
| Outils seuls contre guadan | Sur les 12 bugs : les outils seuls ont des alertes dans la zone du bug pour 2 cas, parmi plus de 550 chacune ; guadan prouve 5 bugs, dont 1 localisé. Sur muparser : 38 alertes, aucune sur la ligne 158 ; guadan avec fuzzing prouve le défaut. |
| Avec ou sans LLM | Sans LLM, guadan prouve ce que les tests du projet montrent. Avec LLM, il répare des builds et trouve par fuzzing ce qu'aucun test ne couvre (muparser, parseur-fragile). Non mesuré sur les 12 bugs (quota). |
| Groq contre un modèle local | **Non mesuré.** La machine de développement n'a pas de GPU dédié ; un modèle local y serait lent. |

## 4. Limites

- **Échantillon petit** : 12 bugs, 4 projets. Les chiffres décrivent ces cas, pas l'ensemble des
  projets C/C++.
- **Tests hors CTest invisibles** : 6 des 12 bugs ne peuvent pas être retrouvés pour cette raison
  seule.
- **Réglages manuels** pour exiv2 et cpp_peglib, déclarés ci-dessus.
- **Le fuzzing n'entre pas dans les 12 bugs** : il demande un harnais par projet (ou le LLM).
- **La localisation est une mesure grossière** : ± 2 lignes autour des lignes modifiées par le
  correctif ; un bug peut se manifester loin de sa correction.
- **Une seule architecture par partie** : x86-64 pour les 12 bugs, ARM64 pour les cas avec LLM.

## Reproduire

```bash
gh workflow run evaluation.yml
```

```bash
python3 -m eval.agreger eval/resultats
```
