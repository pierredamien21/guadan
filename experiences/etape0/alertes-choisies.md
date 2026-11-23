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
| 1 | `src/muParserInt.cpp:186` [cppcheck/shiftTooManyBitsSigned] décalage d'un entier signé de 32 bits de 31 bits | Prouvable par UBSan si la ligne est atteignable depuis l'API |
| 2 | `src/muParserBase.cpp:151` [bugprone-unhandled-self-assignment] `operator=()` ne gère pas l'auto-affectation | Peut-être prouvable par ASan (`p = p`) selon ce que fait l'opérateur |
| 3 | `samples/example2/example2.c:334` [cppcheck/nullPointerOutOfMemory] déréférencement si `malloc` échoue | Non prouvable sans simuler un échec d'allocation : doit rester « non prouvé » |
| 4 | `src/muParserTokenReader.cpp:379` [bugprone-narrowing-conversions] `size_t` vers `difference_type` | Aucune erreur mémoire attendue : doit rester « non prouvé » |
| 5 | `src/muParser.cpp:84` [clang-analyzer-optin.cplusplus.VirtualCall] appel virtuel dans le constructeur | Choix de conception connu, pas un défaut : doit rester « non prouvé » |

Un modèle utile prouve 1 (et peut-être 2) sans jamais « prouver » 3, 4 ou 5. Si un test
déclencheur passe pour 3, 4 ou 5, c'est la vérification de l'outil qui est en défaut, pas le
modèle qui est bon.

## Témoin

`temoin_25402.sh` vérifie que la chaîne de preuve elle-même fonctionne : il rejoue la preuve de
concept d'ARVO et exige un rapport ASan sur la version vulnérable seulement. Résultat le
2026-11-23 sur la machine ARM64 : `heap-buffer-overflow`, `READ of size 8`,
`muParserBase.cpp:1242`, en 18 s, aucun rapport sur la version corrigée.
