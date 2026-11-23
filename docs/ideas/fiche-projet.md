# Guadan (nom de travail)

Diagnostic prouvé de dépôts C/C++ CMake : chaque constat est livré avec la commande qui le reproduit.

> « CodeGuardian » est à abandonner : Rubrik et Akamai ont chacun un produit « Code Guardian ».
> « Guadan » vient du nom du dossier ; sa disponibilité n'a pas été vérifiée.

## Problème

Comment permettre à un développeur qui récupère un dépôt C/C++ inconnu de savoir en une commande
ce qui est réellement cassé, sans trier des centaines d'avertissements dont la plupart ne comptent pas ?

## Direction retenue

Un outil en ligne de commande qui prend un dépôt CMake, le compile dans un conteneur isolé, lance
les tests et les analyseurs, puis produit un rapport court à deux niveaux :

- **Prouvé** : le constat est accompagné d'une commande et de sa sortie (échec de build, test qui
  échoue, rapport AddressSanitizer/UBSan obtenu par les tests du projet ou par fuzzing). Ce filtre est appliqué par
  du code, pas par un LLM.
- **Non prouvé** : alertes d'analyse statique que l'outil n'a pas réussi à déclencher, dans une
  annexe séparée, triées par vraisemblance.

Le LLM ne prouve rien lui-même (D-10). Il diagnostique les échecs de build, écrit les harnais,
graines et dictionnaires de fuzzing, tente de façon bornée un test déclencheur, trie les alertes
non prouvées en expliquant pourquoi, et explique les preuves.
Tout le reste est un pipeline déterministe en Python (D-11). Le plan de réalisation est dans
`docs/plan.md`.

Le positionnement n'est pas « idée inédite » (Codex Security d'OpenAI et les systèmes du concours
AIxCC prouvent déjà par exécution), mais « petit, ouvert, local, centré sur CMake, mesuré
honnêtement ».

## Hypothèses à valider

- [ ] Un dépôt CMake courant se compile automatiquement dans le conteneur dans une majorité de cas.
      Test : 20 dépôts de BugsC++ ou choisis sur GitHub, compter les réussites.
- [ ] Les images Docker de BugsC++ et d'ARVO fonctionnent réellement sur ta machine.
      Test : en reproduire 3 de chaque avant d'écrire du code.
- [ ] Un LLM arrive à écrire un test déclencheur pour une part utile des alertes
      (la littérature annonce 20 à 30 % en un essai). Test : 30 alertes, plusieurs essais chacune.
- [ ] Un test déclencheur validé ne confirme pas de fausse alerte (résultat d'arXiv 2607.09979).
      Test : le vérifier sur des versions corrigées des mêmes bugs.

## Périmètre de la première version

Dans le périmètre :

- Dépôt local, C/C++, CMake, Linux, dans un conteneur Docker.
- Deux phases d'isolation : récupération des dépendances avec réseau, puis build et tests sans
  réseau, sans secrets, avec limites de temps et de mémoire.
- Build avec `compile_commands.json`, CTest, clang-tidy, cppcheck, AddressSanitizer et UBSan.
- Fuzzing sous sanitizers (harnais écrits avec l'aide du LLM), campagnes longues sur GitHub.
- Tentative bornée de tests déclencheurs ; tri expliqué des alertes non prouvées.
- Rapport Markdown ou HTML à deux niveaux, avec la commande de reproduction de chaque constat.
- Évaluation publiée : taux de build réussi, nombre d'alertes brutes contre constats prouvés,
  bugs connus retrouvés sur un échantillon de BugsC++, comparaison avec les outils seuls.

Critère de fin : sur un échantillon fixé de bugs connus, le rapport et ses chiffres se régénèrent
à l'identique avec une seule commande.

## Forme du rendu (tout gratuit, dépôt public)

1. **Outil installable** : image Docker publiée sur le registre de conteneurs GitHub, contenant
   CMake, Clang et les analyseurs. Une commande pour analyser un dépôt local.
2. **Action GitHub** : l'analyse tourne sur les machines GitHub de l'utilisateur, avec sa propre
   clé de modèle. Publiée sur le Marketplace.
3. **Site vitrine statique** (GitHub Pages) : galerie de rapports sur de vrais projets open source,
   chiffres de l'évaluation, vidéo de démonstration.

Le rapport est une page HTML autonome. Pas de serveur à héberger, pas d'application de bureau.

Gratuité vérifiée dans la documentation GitHub le 2026-11-13 : Actions sur dépôts publics avec les
machines standard, paquets publics et registre de conteneurs (« currently free »), Pages sur
dépôts publics.

**Modèle de langage** : tout service compatible avec le format d'API d'OpenAI, au choix de
l'utilisateur (modèle local via Ollama ou offre gratuite en ligne). Un modèle plus faible produit
moins de constats prouvés, jamais de faux, puisque chaque preuve est vérifiée par exécution.

## Plan

Voir `docs/plan.md` (tâches T1 à T22) et `SUIVI.md` (avancement).

## Ce qu'on ne fait pas, et pourquoi

- **Service web où l'on colle son dépôt** : serveurs et modèle à payer pour tout le monde, et
  exécution de code inconnu chez soi.

- **Python** : la preuve y est moins objective et les jeux de bugs moins exploitables.
- **Six agents spécialisés** : lancer CMake ou CTest ne demande pas de LLM.
- **« Erreurs logiques » et « respect de l'architecture »** : aucun outil ne peut les prouver.
- **Revue de Pull Request et intégration GitHub** : terrain déjà occupé ; à envisager après.
- **Correction automatique du code** : hors sujet tant que le diagnostic n'est pas fiable.
- **Autres systèmes de build (Make, Meson, Bazel), Windows, macOS** : chaque ajout multiplie
  les cas d'échec du build.
- **Mesure du « temps gagné »** : non mesurable sérieusement par une personne seule.

## Questions ouvertes

- Quel modèle gratuit donne des résultats suffisants, et ta machine peut-elle faire tourner un
  modèle local ? (étape 0)
- Quelles offres gratuites en ligne existent, avec quelles limites ? (non vérifié)
- Quel nom définitif ?

Sources et chiffres : [choix-cible-codeguardian.md](../research/choix-cible-codeguardian.md).
