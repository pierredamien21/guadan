# guadan sur quatre projets open source actuels (T21)

Le 2026-11-26, sur la machine ARM64 de développement, avec Groq (gpt-oss-120b), tri des alertes
et 120 s de fuzzing avec un harnais écrit par le LLM. Ces projets sont fuzzés en continu par
OSS-Fuzz : ne rien y trouver était le résultat attendu, et c'est ce que montre le tableau, à une
exception près, qui était une erreur de guadan.

| Projet | Version | Tests (échoués) | Prouvés | Alertes | Fuzzing | Jetons | Durée |
|---|---|---|---|---|---|---|---|
| muparser | `430ce5c` (2026-11-19) | 2 (0) | 0 | 41 | 202 924 exécutions, aucun plantage | 11 006 | 166 s |
| tinyxml2 | `8224e42` (2026-05-23) | 1 (0) | 0 | 9 | 74 247 841 exécutions, aucun plantage | 7 525 | 149 s |
| cJSON | `6d9f244` (2026-09-16) | 19 (1, puis 0) | 1, puis 0 | 96 | harnais de Groq non compilable en 3 essais | 16 920 | 95 s |
| yaml-cpp | `f473f3b` (2026-11-08) | 0 | 0 | 21 | 256 507 exécutions, aucun plantage | 8 736 | 168 s |

## Ce que ces quatre analyses ont appris

- **muparser** : la version actuelle ne déclenche plus le comportement indéfini de la ligne 158
  trouvé sur `9e28c71` ; cohérent avec sa correction en amont.
- **cJSON : une fausse preuve, trouvée et corrigée.** Le test `misc_tests` échouait avec un
  `stack-overflow` ASan dans `cJSON_Duplicate_rec`. En rejouant le test dans trois configurations
  (sans sanitizer, ASan seul, options de guadan avec 8 puis 64 Mo de pile), il est apparu que seule
  l'instrumentation était en cause : à `-O0` avec ASan et UBSan, la récursion voulue de 10 000
  niveaux (`CJSON_CIRCULAR_LIMIT`) dépassait les 8 Mo de pile. guadan donne maintenant 64 Mo de pile
  à tout ce qu'il exécute (D-16) ; cJSON passe alors ses 19 tests, sans aucun constat prouvé.
- **cJSON** : le harnais de fuzzing écrit par Groq n'a pas compilé en trois essais ; le fuzzing n'a
  donc pas eu lieu. Limite du modèle gratuit, signalée dans le rapport.
- **yaml-cpp** : ses tests sont désactivés par défaut (`YAML_CPP_BUILD_TESTS`) ; guadan ne les active
  pas tout seul. Avec `-DYAML_CPP_BUILD_TESTS=ON`, ils tourneraient ; ce réglage n'a pas été essayé ici.
- **Coût** : de 7 500 à 17 000 jetons par projet, soit 44 187 pour les quatre, sur 200 000 par jour.

## Rien à signaler en amont (T22)

Aucun de ces quatre projets n'a de défaut prouvé dans sa version actuelle, et le défaut trouvé sur
muparser `9e28c71` est déjà corrigé. Il n'y a donc pas de bug à signaler pour l'instant : en
inventer un serait contraire à tout ce que guadan défend.
