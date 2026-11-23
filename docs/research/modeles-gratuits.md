# Modèles de langage gratuits pour Guadan : API en ligne, GitHub Actions, modèles locaux

Recherche documentaire du 23 novembre 2026. Toutes les pages citées ont été lues ce jour-là.

**Légende de fiabilité** (même convention que `choix-cible-codeguardian.md`)

- **[V]** : page primaire lue pendant cette recherche (documentation, page de tarifs, carte de modèle, dépôt, fichier de données d'un classement). Les pages ont été lues par extraction automatique ou téléchargées et filtrées ; les chiffres cités sont ceux de la page.
- **[E]** : seul l'extrait du moteur de recherche a été vu, ou une réponse d'employé sur un forum officiel, sans page de documentation.
- **[NC]** : non confirmé (source secondaire, souvenir, ou déduction de ma part).
- **Calcul** : chiffre que j'ai dérivé à partir de chiffres [V] ; la formule est donnée.

---

## 1. Recommandation

1. **Développement : Groq (offre gratuite), `openai/gpt-oss-120b` ou `qwen/qwen3.8-27b`.** Les limites sont publiées : 30 requêtes/min, 1 000/jour. Mais il n'y a que 8 000 jetons/min et 200 000/jour, donc l'outil doit tronquer les logs à environ 6 000 jetons. **Second choix : Gemini** (`gemini-3.8-flash`, contexte de 1 M de jetons) pour les gros logs. Son quota gratuit n'est pas publié, environ 20 requêtes/jour selon des utilisateurs, et les données servent à l'entraînement.
2. **Action GitHub : aucun modèle gratuit n'est plus accessible avec le seul `GITHUB_TOKEN`.** GitHub Models a été retiré le 30 juillet 2026. L'action doit demander une clé à l'utilisateur (secret, service compatible OpenAI, Groq documenté par défaut). Sans clé, elle doit fonctionner sans modèle de langage.
3. **Secours : OpenRouter (modèles `:free`, 50 requêtes/jour) puis SambaNova (20 requêtes/jour).** L'outil passe de l'un à l'autre en changeant seulement l'URL de base et la clé.
4. **Modèle local : utile comme mode « rien ne sort de la machine », pas comme défaut.** Par exemple Qwen3.5-9B ou Gemma 4 12B en Q4 via llama.cpp ou Ollama, qui ont tous deux des binaires ARM64. Vitesse attendue : 15 à 20 jetons/s sur Snapdragon X Elite (extrapolation), beaucoup moins sur un runner GitHub à 4 cœurs.
5. Mistral, Hugging Face, Together, Cerebras et GitHub Models **ne sont plus gratuits sans carte ou sans achat**. Ils sont à exclure de la documentation « gratuit ».

---

## 2. Tableau comparatif des offres en ligne

| Fournisseur | Meilleur modèle gratuit pour le code | Limites gratuites | Carte bancaire | Compatible OpenAI (URL de base) | Restrictions | Lien |
|---|---|---|---|---|---|---|
| **Groq** | `openai/gpt-oss-120b`, `qwen/qwen3.8-27b` | 30 RPM, 1 000 RPD, **8 000 TPM**, 200 000 TPD par modèle [V]. Contexte 131 072 jetons [V] | Non publié sur la page des limites [NC : non exigée selon l'usage courant] | `https://api.groq.com/openai/v1` [V] | Usage des données non vérifié | [rate-limits](https://console.groq.com/docs/rate-limits), [models](https://console.groq.com/docs/models) |
| **Google Gemini (AI Studio)** | `gemini-4-hydrogen`, `gemini-3.8-flash` (tous deux « Free of charge ») [V] | **Non publiées** : « can be viewed in Google AI Studio » [V]. 3.8 Flash : 20 RPD selon un fil d'utilisateur [E]. Contexte 1 048 576 jetons [V] | Non (le niveau Free exige un projet actif, parfois une vérification) [V] | `https://generativelanguage.googleapis.com/v1beta/openai/` [V] | Données utilisées pour améliorer les produits et lues par des humains [V] ; services gratuits interdits pour des clients API proposés à des utilisateurs de l'EEE, de Suisse et du Royaume-Uni [V] ; 18 ans minimum [V] | [pricing](https://aistudio.google.com/docs/pricing), [rate-limits](https://aistudio.google.com/docs/rate-limits), [terms](https://aistudio.google.com/docs/terms) |
| **OpenRouter** (`:free`) | `google/gemma-4-31b-it:free`, `nvidia/nemotron-3-ultra-550b-a55b:free` (11 modèles `:free` en tout) [V] | 20 RPM, **50 RPD** ; 1 000 RPD si au moins 10 crédits achetés [V] | Non précisé [NC] | `https://openrouter.ai/api/v1` [V] | Les fournisseurs qui journalisent ne sont utilisés que si l'option d'entraînement est activée [V] | [limits](https://openrouter.ai/docs/api-reference/limits), [FAQ](https://openrouter.ai/docs/faq), [liste](https://openrouter.ai/api/v1/models) |
| **SambaNova Cloud** | `gpt-oss-120b`, `gemma-4-31B-it` [V] | 20 RPM, **20 RPD**, 200 000 TPD [V] | **Non** : le niveau Free s'applique justement sans moyen de paiement [V] | Oui ; URL de base donnée dans la console [V] (`https://api.sambanova.ai/v1` [NC]) | Modèles « Preview », pas pour la production [V] | [rate-limits](https://docs.sambanova.ai/docs/en/models/rate-limits.md), [openai](https://docs.sambanova.ai/docs/en/features/openai-compatibility.md) |
| **Cloudflare Workers AI** | `@cf/openai/gpt-oss-120b`, `@cf/qwen/qwen2.5-coder-32b-instruct` [V] | 10 000 « Neurons »/jour [V], soit environ 50 requêtes de 4 000 + 1 000 jetons avec gpt-oss-120b (calcul) | Non précisé [NC] | `https://api.cloudflare.com/client/v4/accounts/<ID>/ai/v1` [V] | Usage des données non vérifié | [pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/), [openai](https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/) |
| **NVIDIA (build.nvidia.com)** | Catalogue NIM (non détaillé ici) | Plus de crédits ; limites par modèle **non publiées** (employé NVIDIA) [E] ; 40 RPM souvent cité [NC] | Non vérifié | `https://integrate.api.nvidia.com/v1` [E] | Prototypage seulement : la production exige NVIDIA AI Enterprise [V] ; compte NVIDIA Developer Program | [FAQ](https://docs.api.nvidia.com/nim/docs/product) |
| Mistral | — | **Pas d'API en mode Free** [V] | Activation de la facturation exigée [V] | — | — | [usage-limits](https://docs.mistral.ai/admin/billing-usage/usage-limits) |
| Hugging Face Inference Providers | — | **0 crédit mensuel** pour un compte gratuit [V] | Achat de crédits exigé [V] | `https://router.huggingface.co/v1` [V] | — | [pricing](https://huggingface.co/docs/inference-providers/pricing) |
| Together AI | — | Pas d'essai gratuit ; achat minimal de 5 $ [V] | Oui | — | — | [support](https://support.together.ai/articles/1862638756-changes-to-free-tier-and-billing-july-2025) |
| Cerebras | (`gpt-oss-120b`, `qwen-3.8-27b` pendant l'essai) | Crédit unique de 5 $, valable 30 jours [V] | **Oui**, moyen de paiement exigé [V] | `https://api.cerebras.ai/v1` [V] | « not intended for production » [V] | [pricing](https://www.cerebras.ai/pricing), [rate-limits](https://inference-docs.cerebras.ai/support/rate-limits) |
| GitHub Models | — | **Service retiré le 30 juillet 2026** [V] | — | — | — | [changelog](https://github.blog/changelog/2026-07-30-github-models-is-now-retired/) |

RPM = requêtes/minute, RPD = requêtes/jour, TPM = jetons/minute, TPD = jetons/jour.

---

## 3. Détail par point

### 3.1 Offres gratuites d'API en ligne

#### Groq — vérifié

- La page des limites contient deux tableaux. Le tableau « Free Plan Limits » (champ `freeRows` du code de la page) donne pour `openai/gpt-oss-120b`, `openai/gpt-oss-20b` et `qwen/qwen3.8-27b` : 30 RPM, 1 000 RPD, 8 000 TPM et 200 000 TPD [V] ([rate-limits](https://console.groq.com/docs/rate-limits)). Le plan Developer (payant) monte à 1 000 RPM et 250 000 TPM [V].
- La page renvoie aussi à la page des limites du compte pour les valeurs exactes de l'organisation [V].
- Contexte : 131 072 jetons pour gpt-oss-120b et qwen3.8-27b ; sortie maximale 65 536 et 16 384 jetons [V] ([models](https://console.groq.com/docs/models)).
- qwen3.8-27b est rangé parmi les modèles « Preview », qui peuvent être retirés à bref délai ; gpt-oss-120b est un modèle « Production » [V].
- **Conséquence pratique (calcul)** : 8 000 jetons/min, entrée et sortie comprises [NC sur ce mode de comptage], interdisent d'envoyer un log CMake de 20 000 jetons. Les 200 000 jetons/jour font environ 25 diagnostics de 8 000 jetons par jour.
- Les en-têtes `x-ratelimit-*` et le code 429 avec `retry-after` sont documentés [V]. L'outil peut donc lire le quota restant.
- Carte bancaire et usage des données pour l'entraînement : rien sur les pages lues [NC].

#### Google Gemini API — vérifié, sauf les quotas

- Modèles « Free of charge » au niveau gratuit, entre autres : Gemini 4 Hydrogen, Gemini 3.8 Flash, Gemini 3.6 Flash, Gemini 3.5 Flash-Lite, Gemini 3.1 Flash-Lite, Gemini 2.5 Flash, Gemini 2.5 Pro [V] ([pricing](https://aistudio.google.com/docs/pricing)). Gemini 4 Carbon, Argon, Neon et 3.1 Pro Preview n'ont pas de niveau gratuit [V].
- Gemini 4 Hydrogen : présenté pour le « everyday coding and agentic workflows », contexte de 1 M de jetons, statut Stable, mis à jour en novembre 2026 [V] ([modèle](https://aistudio.google.com/docs/models/gemini-4-hydrogen)).
- Gemini 3.8 Flash (`gemini-3.8-flash`) : 1 048 576 jetons en entrée, 65 536 en sortie, appel de fonctions et sorties structurées, statut Stable [V] ([modèle](https://aistudio.google.com/docs/models/gemini-3.8-flash)). Sortie le 2 septembre 2026 [V] ([blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/3-8-flash-and-3-8-flash-cyber/)).
- **Quotas gratuits non publiés.** La page des limites dit seulement : « Rate limits depend on a variety of factors (such as your usage tier) and can be viewed in Google AI Studio. » [V] ([rate-limits](https://aistudio.google.com/docs/rate-limits)). Aucun tableau par modèle n'y figure pour le niveau Free. Un fil du forum officiel de Google, daté du 3 septembre 2026, se plaint de **20 RPD** pour 3.8 Flash et cite 500 RPD pour Flash-Lite [E] ([fil](https://discuss.ai.google.dev/t/gemini-3-8-flash-free-tier-20-rpd-is-too-limited-for-practical-evaluation/180609)). Aucun employé de Google n'y répond.
- Compatibilité OpenAI : `https://generativelanguage.googleapis.com/v1beta/openai/`, avec `/chat/completions`, flux, appel de fonctions, sortie structurée et `reasoning_effort` [V] ([openai](https://aistudio.google.com/docs/openai)).
- **Données** : la ligne « Used to improve our products » vaut « Yes » au niveau gratuit et « No » au niveau payant [V]. D'après les conditions (en vigueur au 23 mars 2026), Google utilise les contenus envoyés aux services gratuits pour améliorer ses produits, des « human reviewers may read, annotate, and process your API input and output », et il ne faut pas y envoyer d'informations sensibles, confidentielles ou personnelles [V] ([terms](https://aistudio.google.com/docs/terms)).
- **Restriction géographique** : « You may use only Paid Services when making API Clients available to users in the European Economic Area » ; la restriction couvre aussi la Suisse et le Royaume-Uni [V]. Cela touche directement un outil distribué en France. La lecture que j'en fais [NC, à faire confirmer] : un utilisateur européen qui met sa propre clé gratuite dans l'outil pour son usage personnel est dans un cas moins clair qu'un service qui expose Gemini à des tiers. Il ne faut pas présenter Gemini gratuit comme le défaut pour des utilisateurs européens.

#### OpenRouter — vérifié

- 476 modèles listés, dont 11 en `:free` le 23 novembre 2026 [V] ([API models](https://openrouter.ai/api/v1/models)) : `google/gemma-4-31b-it:free` (262 144 jetons), `google/gemma-4-26b-a4b-it:free`, `nvidia/nemotron-3-ultra-550b-a55b:free` (1 000 000), `nvidia/nemotron-3.5-super-vl:free`, `nvidia/nemotron-3.5-lightning:free`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`, `baidu/ernie-5.5-flash-preview:free`, `inclusionai/ling-3.2-flash:free`, et trois autres plus marginaux. **Aucun modèle spécialisé en code** (Qwen Coder, DeepSeek, GLM) n'y est gratuit.
- Limites : 20 RPM et 50 RPD avec moins de 10 crédits achetés ; 1 000 RPD au-delà [V] ([limits](https://openrouter.ai/docs/api-reference/limits)). La FAQ confirme « 50 requests per day total » [V] ([FAQ](https://openrouter.ai/docs/faq)).
- Données : prompts et réponses non journalisés par défaut par OpenRouter. Les fournisseurs qui journalisent, ou dont la politique est inconnue, ne sont utilisés que si l'option d'entraînement est activée dans les réglages [V]. Il est possible qu'un modèle `:free` exige cette option [NC] : à vérifier modèle par modèle.

#### SambaNova Cloud — vérifié

- Niveau Free « Applied when there is no payment method linked with your account » [V].
- `gpt-oss-120b` et `gemma-4-31B-it` : 20 RPM, 20 RPD, 200 000 TPD [V] ([rate-limits](https://docs.sambanova.ai/docs/en/models/rate-limits.md)).
- Tous les modèles sont des « Preview models », réservés à l'évaluation, qui « may be removed at short notice » [V].
- Compatible OpenAI (et Responses, et Anthropic Messages) ; l'URL de base est donnée dans la console [V] ([openai](https://docs.sambanova.ai/docs/en/features/openai-compatibility.md)).

#### Cloudflare Workers AI — vérifié pour le quota

- 10 000 Neurons par jour, sur les plans Workers Free et Paid [V] ([pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/)).
- Coût en Neurons par million de jetons : `@cf/openai/gpt-oss-120b` 31 818 en entrée, 68 182 en sortie ; `@cf/qwen/qwen2.5-coder-32b-instruct` 60 000 et 90 909 [V].
- Calcul : une requête de 4 000 jetons en entrée et 1 000 en sortie sur gpt-oss-120b coûte 4 000 × 0,031818 + 1 000 × 0,068182 ≈ 196 Neurons, soit environ 50 requêtes par jour.
- URL OpenAI : `https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/ai/v1` [V] ([openai](https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/)).
- Carte bancaire et usage des données : non vérifiés [NC].

#### NVIDIA build.nvidia.com — partiellement vérifié

- « Members of the NVIDIA Developer Program have free access to NIM API endpoints for prototyping » ; la production exige une licence NVIDIA AI Enterprise [V] ([FAQ](https://docs.api.nvidia.com/nim/docs/product)). Un outil open source utilisé par d'autres sur leur code est un usage au moins discutable [NC].
- Une réponse d'employé NVIDIA sur le forum dit que le système de crédits a été abandonné, que les limites varient selon le modèle et qu'elles ne sont pas publiées [E] ([forum](https://forums.developer.nvidia.com/t/request-more-4-000-credits-option-on-build-nvidia-com/344567), page inaccessible en lecture directe, code 403). Le chiffre de 40 RPM vient de dizaines de messages d'utilisateurs [NC].

#### Offres exclues (plus gratuites sans carte ou sans achat)

- **Mistral** : « Free mode includes a monthly usage budget for trying Vibe and Studio. It doesn't include API access. Creating API keys and using the API require billing activation and pay-as-you-go. » [V] ([usage-limits](https://docs.mistral.ai/admin/billing-usage/usage-limits)). Des sites tiers affirment encore qu'une offre « Experiment » existe avec vérification par téléphone [NC]. La page officielle de l'aide qui la décrivait renvoie maintenant une erreur 404.
- **Hugging Face Inference Providers** : comptes gratuits « None » en crédits mensuels, « credits purchase required » ; 2 $/mois pour PRO [V] ([pricing](https://huggingface.co/docs/inference-providers/pricing)).
- **Together AI** : « Together AI does not currently offer free trials. » et « Access to the Together platform requires a minimum $5 credit purchase. » [V] ([support](https://support.together.ai/articles/1862638756-changes-to-free-tier-and-billing-july-2025)).
- **Cerebras** : « Add a valid payment method to receive a one-time $5 promotional credit. », valable 30 jours, puis accès suspendu [V] ([pricing](https://www.cerebras.ai/pricing)). Pendant l'essai : `qwen-3.8-27b` à 300 RPM, `gpt-oss-120b` à 5 RPM [V] ([rate-limits](https://inference-docs.cerebras.ai/support/rate-limits)).

### 3.2 GitHub Models dans GitHub Actions

**Réponse courte : non, plus maintenant.**

- Le 16 juin 2026, GitHub Models a été fermé aux nouveaux clients [E]. Le 1er juillet, GitHub a annoncé le retrait complet. Le 30 juillet 2026, « The playground, model catalog, inference API, and bring your own key (BYOK) are no longer available to any customer » [V] ([annonce](https://github.blog/changelog/2026-07-01-github-models-is-being-fully-retired-on-july-30-2026/), [retrait](https://github.blog/changelog/2026-07-30-github-models-is-now-retired/)). La page de documentation sur le prototypage le confirme : « GitHub Models has been fully retired. » [V] ([docs](https://docs.github.com/en/github-models/use-github-models/prototyping-with-ai-models)).
- Les exemples `permissions: models: read` avec `GITHUB_TOKEN` vers `models.github.ai` sont donc caducs.
- GitHub oriente vers Microsoft Foundry (payant) et vers GitHub Copilot [V].
- **`actions/ai-inference`** : la v3 (29 juillet 2026) est « Copilot-only ». Elle exige d'installer le Copilot CLI et de l'authentifier ; l'exemple du README utilise `COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_PAT }}` [V] ([README](https://github.com/actions/ai-inference), lu via `gh api`).
- **Copilot CLI avec `GITHUB_TOKEN`** : possible depuis juillet 2026, avec la permission `copilot-requests: write`, mais seulement dans un dépôt d'organisation dont la politique « Allow use of Copilot CLI billed to the organization » est active. Les crédits sont facturés à l'organisation [V] ([changelog](https://github.blog/changelog/2026-07-02-copilot-cli-no-longer-needs-a-personal-access-token-in-github-actions/), [docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli-in-actions)).
- Les pages lues ne disent pas si cela marche dans un dépôt personnel ni avec Copilot Free, ni quel quota s'applique.
- Sinon, il faut un jeton personnel à grain fin avec la permission « Copilot Requests » [E]. Ce n'est de toute façon pas une API `/v1/chat/completions` : c'est un CLI d'agent.
- **Conséquence pour Guadan** : l'action GitHub ne peut pas offrir de modèle gratuit « sans clé ». Il reste trois possibilités :
  1. une clé fournie par l'utilisateur (secret), pour un service compatible OpenAI, par exemple Groq ;
  2. un modèle local lancé dans le runner (lent, voir 3.3) ;
  3. un mode sans modèle de langage.

### 3.3 Modèles locaux (16 Go de RAM, sans GPU)

#### Outils — vérifié

- **Ollama v0.40.17** (10 novembre 2026) publie `ollama-windows-arm64.zip` et `ollama-linux-arm64.tar.zst` [V] (assets de la [release](https://github.com/ollama/ollama/releases)). La page Windows ne mentionne pas ARM64 dans ses prérequis [V] ([docs](https://docs.ollama.com/windows)). Le support existe donc, mais il n'est pas documenté. API OpenAI : `http://localhost:11434/v1/` [V] ([docs](https://docs.ollama.com/api/openai-compatibility.md)).
- **llama.cpp b12638** (23 novembre 2026) publie `win-cpu-arm64`, `win-vulkan-arm64`, `win-opencl-adreno-arm64`, `ubuntu-arm64`, `linux-arm64-snapdragon` [V] ([releases](https://github.com/ggml-org/llama.cpp/releases)). `llama-server` expose une API compatible OpenAI [V] (README).

#### Modèles candidats — cartes lues sur Hugging Face

| Modèle | Paramètres | Licence | Chiffres de code publiés par l'éditeur | Remarque |
|---|---|---|---|---|
| [Qwen/Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B) (fév. 2026) | 9,65 G (poids totaux) | Apache-2.0 [V] | LiveCodeBench v6 : 65,6 (4B : 55,8 ; GPT-OSS-20B : 74,6 dans le même tableau) [V] | Le plus téléchargé de sa taille |
| [XiaomiMiMo/MiMo-V2.6-Distill-Qwen-9B](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Distill-Qwen-9B) (sept. 2026) | 9,4 G | MIT [V] | SWE Verified 61,1 (avg@3), contre 60,0 pour Qwen3.5-9B ; Terminal Bench 2.1 : 37,1 [V] | Affinage de Qwen3.5-9B. Chiffres de l'éditeur, outillage d'agent non précisé dans la carte. Sur Ollama : `mimo-v2.6`, 6,6 à 8,7 Go, contexte 256 K [V] ([ollama](https://ollama.com/library/mimo-v2.6)) |
| [google/gemma-4-12B-it](https://huggingface.co/google/gemma-4-12B-it) (mai 2026) | 12 G | Apache-2.0 (champ licence de la carte) [V] | LiveCodeBench v6 : 72,0 % ; Codeforces 1659 [V] | GGUF officiel [Q4_0 QAT](https://huggingface.co/google/gemma-4-12B-it-qat-q4_0-gguf) [V] |
| [google/gemma-4-E4B-it](https://huggingface.co/google/gemma-4-E4B-it) | ~8 G de poids totaux, « E4B » | Apache-2.0 [V] | LiveCodeBench v6 : 52,0 % [V] | Plus rapide, nettement plus faible |
| [mistralai/Ministral-3-14B-Instruct-2512](https://huggingface.co/mistralai/Ministral-3-14B-Instruct-2512) (oct. 2025) | 13,9 G | Apache-2.0 [V] | LiveCodeBench 0,646 (variante Reasoning ; 8B : 0,616) [V] | Plus ancien |

Trop gros pour 16 Go en Q4 [NC, estimation] : Qwen3.8-27B, Qwen3.6-35B-A3B, Gemma 4 26B-A4B (25,2 G de paramètres au total, même si 3,8 G seulement sont actifs [V]), Gemma 4 31B. Un modèle MoE doit garder tous ses experts en mémoire.

Mémoire (estimation, [NC]) : un poids en Q4 occupe environ 0,55 à 0,6 octet par paramètre. Cela donne environ 5,5 à 6 Go pour 9 B, 7 à 8 Go pour 12 B et 8,5 à 9 Go pour 14 B, plus le cache KV, qui grossit avec le contexte. Sous Windows avec 16 Go, 9 à 12 B est le maximum confortable.

#### Vitesse — chiffres publiés

- Snapdragon X Elite (Surface Laptop 7), llama.cpp sur CPU, Llama 8B Q4_0, 10 fils : **pp128 = 198 jetons/s, tg64 = 23 jetons/s**. Mesure d'un contributeur du projet, 17 décembre 2024 [V] ([discussion #8336](https://github.com/ggml-org/llama.cpp/discussions/8336)). Llama 7B Q4_0 : tg128 = 24,8 jetons/s sous Windows natif, 22,6 sous WSL2 [V].
- Extrapolation [NC] : la génération est limitée par la bande passante mémoire, donc elle varie à peu près à l'inverse de la taille du fichier. Cela donne environ 18 à 20 jetons/s pour un 9 B en Q4 et 13 à 15 pour un 12 B. Un Snapdragon X Plus ou X (8 cœurs) sera plus lent [NC]. Je n'ai pas vérifié la référence exacte de la puce de l'auteur.
- Les modèles « à réflexion » (Qwen3.5, Gemma 4, MiMo) génèrent souvent des milliers de jetons de réflexion. À 20 jetons/s, une réponse peut prendre une à plusieurs minutes [NC]. Il faudra désactiver ou limiter la réflexion.
- Runner GitHub Linux x86-64 (4 cœurs, 16 Go) : **aucun chiffre publié trouvé**. Ma déduction [NC] : quelques jetons par seconde pour un 8 B en Q4, plus le téléchargement de 5 à 8 Go à chaque exécution, sauf si le modèle est mis en cache.

### 3.4 Qualité pour la tâche : classements publics

Aucun classement public ne mesure précisément « diagnostiquer un échec CMake » ou « écrire un programme qui déclenche une alerte sous ASan ». Les plus proches :

**CyberGym** (reproduction de vulnérabilités réelles par un programme de preuve, niveau 1). Données lues dans [cybergym.json](https://www.cybergym.io/assets/data/cybergym.json), via la [page du classement](https://www.cybergym.io/cybergym/), le 23 novembre 2026 [V]. Les projets viennent d'OSS-Fuzz, majoritairement en C/C++ [NC]. Les scores dépendent fortement de l'agent et des options, comme l'image Docker « dynamic » ou la mémoire entre tâches.

| Modèle (agent) | Score | Date | Accessible gratuitement ? |
|---|---|---|---|
| Gemini 3.8 Flash Cyber (Google Antigravity) | 86,3 % | 2026-09-10 | Non : réservé au programme Fairwind [V] ([blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/3-8-flash-and-3-8-flash-cyber/)) |
| GLM-5.3 (Claude Code) | 84,5 % | 2026-08-14 | Pas parmi les offres gratuites trouvées |
| Feyospace-v1.1, affiné depuis Qwen3.8-27B | 84,4 % | 2026-09-23 | La base Qwen3.8-27B est gratuite sur Groq, mais la base seule n'est pas classée |
| DeepSeek-V4-Pro (DeepSeek Agent) | 83,3 % | 2026-08-13 | Non trouvé en gratuit |
| DeepSeek-V4-Flash (DeepSeek Agent) | 76,7 % | 2026-07-31 | Non trouvé en gratuit |
| Gemini 2.5 Flash Preview (OpenHands) | 4,8 % | 2025-05-15 | Ancien |
| Qwen3-235B-A22B (OpenHands) | 1,9 % | 2025-05-15 | Ancien |

Aucune entrée pour gpt-oss-120b, Gemma 4, Nemotron, Gemini 3.8 Flash (version standard) ni Gemini 4 Hydrogen.

**SWE-bench Verified** : données lues dans [leaderboards.json](https://github.com/SWE-bench/swe-bench.github.io/blob/master/data/leaderboards.json) [V]. Dernier commit du dépôt le 1er septembre 2026, mais l'entrée la plus récente date du 26 février 2026. Les tâches sont en Python, pas en C/C++.

- Gemini 3 Flash (high) : 75,8 % (2026-02-17).
- Devstral Small (2512) : 56,4 % (2025-12-09).
- gpt-oss-120b : 26,0 % (2025-08-07).

Les modèles gratuits actuels (Gemini 3.8 Flash, 4 Hydrogen, Qwen3.8) n'y figurent pas.

**Aider polyglot** : 225 exercices Exercism en C++, Go, Java, JavaScript, Python et Rust [V] ([classement](https://aider.chat/docs/leaderboards/)). La dernière entrée date du 3 octobre 2025, donc le classement est figé. gpt-oss-120b (high) : 41,8 % (2025-08-06) ; Gemini 2.5 Flash Preview 05-20 (réflexion) : 55,1 %.

**LiveCodeBench** : les données du site public n'ont pas été mises à jour depuis le 1er août 2025 (dernier commit du dépôt [V]). Il ne reste que les chiffres des cartes de modèles (tableau 3.3), publiés par les éditeurs eux-mêmes. La version v6 est la même pour Qwen et Gemma, mais les réglages d'évaluation ne sont pas forcément identiques.

**BigCodeBench** : non consulté.

**Conclusion** : aucun classement à jour ne permet de comparer les modèles gratuits actuels sur du C/C++. La seule mesure crédible pour Guadan est sa propre évaluation sur BugsC++ et ARVO (déjà prévue au projet), avec le modèle comme paramètre.

---

## 4. Risques et signalement à l'utilisateur

| Risque | Constat | Ce que l'outil doit faire |
|---|---|---|
| **Offres qui changent** | En cinq mois : GitHub Models retiré, API de Mistral sortie de l'offre gratuite, quotas gratuits de Gemini non publiés et réduits selon les utilisateurs [E], crédits NVIDIA supprimés [E]. Les modèles « Preview » de Groq et SambaNova peuvent disparaître sans préavis [V] | Aucun fournisseur codé en dur : URL de base, modèle et clé en configuration. Message clair sur les codes 429, 401 et 404 (« quota atteint » ou « modèle retiré »). Lecture des en-têtes `x-ratelimit-*` quand ils existent. Liste des services documentée avec sa date de vérification |
| **Données utilisées pour l'entraînement** | Gemini gratuit : oui, avec relecture humaine possible [V]. OpenRouter : dépend du fournisseur et de l'option d'entraînement [V]. Groq, SambaNova, Cloudflare : non vérifié | Avant le premier envoi, afficher le fournisseur, et si sa politique est connue, « vos données peuvent servir à l'entraînement », avec un lien vers ses conditions. Refuser par défaut d'envoyer à un service marqué « entraînement : oui » sans option explicite (`--allow-training-provider`) |
| **Code d'utilisateurs envoyé à un tiers** | Les logs de build et les extraits contiennent des chemins, des noms internes et parfois des secrets. Gemini demande de ne rien envoyer de confidentiel aux services gratuits [V] | Mode local ou sans modèle par défaut dans l'action GitHub. Masquage des secrets évidents (jetons, chemins personnels) avant envoi. Journal local de ce qui a été envoyé (option `--show-payload`). Avertissement explicite pour les dépôts privés |
| **Restriction EEE, Suisse et Royaume-Uni (Gemini gratuit)** | « only Paid Services » pour des clients API proposés à des utilisateurs de l'EEE [V] | Ne pas proposer Gemini gratuit comme défaut ; mentionner la clause dans la documentation |
| **Usage « prototypage seulement »** | NVIDIA [V], SambaNova (« evaluation ») [V], Cerebras [V] | Le signaler dans la documentation ; ne pas présenter ces services comme une solution de production |
| **Quotas trop bas pour une CI** | 20 à 50 requêtes/jour chez SambaNova et OpenRouter [V] ; environ 25 gros diagnostics/jour chez Groq (calcul) | Limiter le nombre d'appels par exécution, avec un plafond configurable ; ne pas échouer le build si le modèle est indisponible, rendre les constats sans explication |

---

## 5. Ce qui n'a pas pu être vérifié

- **Quotas gratuits exacts de Gemini** (RPM, RPD, TPM par modèle) : Google ne les publie plus que dans AI Studio, derrière connexion. Le chiffre de 20 RPD pour 3.8 Flash vient d'un fil d'utilisateur.
- **Groq** : exigence ou non d'une carte bancaire, usage des données pour l'entraînement, mode de comptage des 8 000 TPM (entrée seule ou entrée et sortie).
- **Cloudflare, OpenRouter, NVIDIA** : exigence ou non d'une carte bancaire, politique d'entraînement.
- **NVIDIA** : limites actuelles (non publiées, selon un employé) et URL de base, vue seulement dans des extraits.
- **SambaNova** : URL de base exacte (renvoyée vers la console).
- **Copilot dans Actions** : fonctionnement dans un dépôt personnel, avec Copilot Free, et quota applicable.
- **Mistral** : des sources tierces disent qu'une offre « Experiment » avec vérification par téléphone existe encore ; la documentation officielle dit le contraire. J'ai retenu la documentation.
- **Vitesse sur runner GitHub x86-64 à 4 cœurs** et **sur Snapdragon X Plus ou X** : aucune mesure publiée trouvée ; les chiffres donnés sont des extrapolations. À mesurer avec `llama-bench` sur les deux machines.
- **Classements** : pas de mesure récente des modèles gratuits actuels sur du code C/C++. SWE-bench, Aider et LiveCodeBench sont figés avant leur sortie ; CyberGym ne les contient pas. Les chiffres des cartes de modèles sont publiés par les éditeurs eux-mêmes et ne sont pas reproduits.
- **BigCodeBench** non consulté.
- **Licences** : seul le champ licence des cartes Hugging Face a été lu, pas le texte complet. Par exemple, d'éventuelles conditions d'usage propres à Gemma n'ont pas été vérifiées.
