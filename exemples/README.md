# Projets d'exemple

Petits projets CMake au résultat connu d'avance. Ils servent de tests de bout en bout à guadan.

| Projet | Ce qui doit se passer |
|---|---|
| `sain` | Build et tests réussis : aucun constat prouvé |
| `debordement-tas` | Le test `copie_longue` déclenche ASan `heap-buffer-overflow` dans `texte.cpp`, à la ligne marquée `DEFAUT` |
| `ub-entier` | Le test `moyenne_grands` déclenche UBSan `signed integer overflow` dans `calcul.cpp`, à la ligne marquée `DEFAUT` |
| `dep-manquante` | La configuration échoue : zlib est exigé mais absent de l'image (réparable en installant `zlib1g-dev`) |
| `alertes` | Pas de test : cppcheck signale `arrayIndexOutOfBounds` à la ligne 4 de `alertes.cpp` (constat « non prouvé ») |
