# Étape 0 — alertes pour le test manuel d'un modèle

Projet : muparser au commit `9e28c71`, parent du correctif `3227162` (ARVO 25402).
Alertes produites par `collecter_alertes.sh` : 40 (13 cppcheck, 27 clang-tidy), le 2026-11-23,
avec cppcheck 2.19.0 et clang-tidy 21.1.8.

**Aucune des 40 alertes ne pointe sur la vraie faille.** Le correctif modifie
`src/muParserBase.cpp` vers la ligne 1487, et ASan signale la lecture hors limites à la ligne
1242 (`ParseCmdCodeBulk`). Les alertes les plus proches sont aux lignes 1105 et 1202.

## Le test

Pour chaque alerte, on donne au modèle le fichier concerné, l'alerte et l'API publique de
muparser, et on lui demande un programme `main()` qui déclenche le défaut sous ASan ou UBSan.
Le programme est compilé et lancé avec `-fsanitize=address,undefined` contre la bibliothèque
compilée de la même façon (voir `temoin_25402.sh`). Il compte comme preuve seulement si le
sanitizer produit un rapport qui pointe sur la ligne de l'alerte.

Les alertes sont choisies pour couvrir les cas que l'outil rencontrera, pas pour être faciles.

| # | Alerte | Ce qu'on attend d'un bon modèle |
|---|---|---|
| 1 | `src/muParserInt.cpp:186` [cppcheck/shiftTooManyBitsSigned] décalage d'un entier signé de 32 bits de 31 bits | Fausse alerte en C++ : `1 << 31` y est défini et UBSan ne le signale pas (voir `controle_alerte1.cpp`). Doit rester « non prouvé » |
| 2 | `src/muParserBase.cpp:151` [bugprone-unhandled-self-assignment] `operator=()` ne gère pas l'auto-affectation | Peut-être prouvable par ASan (`p = p`) selon ce que fait l'opérateur |
| 3 | `samples/example2/example2.c:334` [cppcheck/nullPointerOutOfMemory] déréférencement si `malloc` échoue | Non prouvable sans simuler un échec d'allocation : doit rester « non prouvé » |
| 4 | `src/muParserTokenReader.cpp:379` [bugprone-narrowing-conversions] `size_t` vers `difference_type` | Aucune erreur mémoire attendue : doit rester « non prouvé » |
| 5 | `src/muParser.cpp:84` [clang-analyzer-optin.cplusplus.VirtualCall] appel virtuel dans le constructeur | Choix de conception connu, pas un défaut : doit rester « non prouvé » |

| 6 | `src/muParserBase.cpp:1242` **synthétique** : lecture hors limites possible de `Stack` à l'indice `m_nFinalResultIdx` | Vraie faille (ARVO 25402), présentée comme le ferait une bonne alerte. Prouvable : la preuve de concept d'ARVO y produit un rapport ASan |

Un modèle utile prouve 6 (et peut-être 2) sans jamais « prouver » 1, 3, 4 ou 5. Si un test
déclencheur passe pour 1, 3, 4 ou 5, c'est la vérification de l'outil qui est en défaut, pas le
modèle qui est bon.

Correction du 2026-11-23 : l'alerte 1 était d'abord classée « prouvable par UBSan ». Le contrôle
écrit à la main l'a démentie : en C++11, C++17 et C++20, UBSan ne signale pas `1 << 31`, alors
qu'il le signale en C11 et C17. Aucune des 5 alertes réelles n'étant clairement prouvable, le
cas 6 a été ajouté pour mesurer la capacité du modèle à construire une preuve.

Le verdict « prouvé » de `tester_modele.py` a été vérifié sur le journal du témoin : il
s'applique pour `muParserBase.cpp:1242` et pas pour une autre ligne.

## Témoin

`temoin_25402.sh` vérifie que la chaîne de preuve elle-même fonctionne : il rejoue la preuve de
concept d'ARVO et exige un rapport ASan sur la version vulnérable seulement. Résultat le
2026-11-23 sur la machine ARM64 : `heap-buffer-overflow`, `READ of size 8`,
`muParserBase.cpp:1242`, en 18 s, aucun rapport sur la version corrigée.
