# Script de la vidéo de démonstration (2 min 30)

Une vidéo d'écran, sans montage compliqué : un terminal Ubuntu (WSL) à gauche, le navigateur à
droite. Tout ce qui est montré a déjà été exécuté et mesuré (voir `JOURNAL.md`) ; refaire les
commandes avant l'enregistrement, les chiffres peuvent varier d'une campagne de fuzzing à l'autre.

## Préparation (hors caméra)

```bash
cd ~/guadan && docker build -t guadan-outils docker/
```

```bash
git -C /root/guadan-travail/muparser checkout -q 9e28c71
```

Avoir la clé Groq dans `~/.bashrc`, le site ouvert dans le navigateur, une police de terminal
grande (18 pt au moins), et rien de personnel à l'écran.

## Scènes

| Temps | À l'écran | Voix |
|---|---|---|
| 0:00 – 0:15 | Le haut du site : « Prouvé ▭ ou rien. » | « Sur un projet C ou C++, les analyseurs statiques sortent des centaines d'alertes. La plupart ne comptent pas. guadan ne vous montre comme prouvé que ce qu'il a vu se produire. » |
| 0:15 – 0:35 | Faire défiler jusqu'aux 38 alertes de muparser | « Sur cette version de muparser, cppcheck et clang-tidy signalent trente-huit alertes. Aucune ne pointe la ligne qui pose vraiment problème. » |
| 0:35 – 1:20 | Terminal : `python3 -m guadan analyse /root/guadan-travail/muparser --sortie /tmp/rapport --fuzz-duree 120`. Accélérer l'attente ×8 | « guadan copie le dépôt, le compile avec AddressSanitizer et UBSan dans un conteneur sans réseau, lance ses tests, puis demande à un modèle gratuit d'écrire un harnais de fuzzing. Le modèle n'a pas le droit de juger : seule l'exécution décide. » |
| 1:20 – 1:50 | Ouvrir `/tmp/rapport/rapport.html`, déplier « Preuve observée » | « Deux minutes plus tard : un comportement indéfini, ligne 158, avec la commande exacte pour le revoir. Les trente-huit alertes restent à part, en non prouvé. » |
| 1:50 – 2:10 | Copier la commande de reproduction, la lancer, montrer la même erreur UBSan | « On relance la commande : même erreur. C'est ça, une preuve. Ce défaut a d'ailleurs été corrigé depuis par les auteurs de muparser. » |
| 2:10 – 2:30 | Le site : section « Ce que guadan promet », puis le pied de page | « Sans clé, guadan fonctionne sans modèle. Il est gratuit, open source, et s'utilise aussi comme action GitHub. Le code et l'évaluation complète sont sur GitHub. » |

## Ce qu'il ne faut pas dire

- Que guadan « trouve des failles de sécurité » : il prouve des défauts à l'exécution ; ce défaut de
  muparser est un comportement indéfini, déjà corrigé en amont.
- Un chiffre qui n'est pas dans `docs/evaluation.md`.
