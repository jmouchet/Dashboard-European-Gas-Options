# Brief TTF quotidien

Le brief répond à la demande d'une synthèse du marché européen du gaz pour un
trader d'options, centrée sur le TTF et ses facteurs directs ou indirects. Morning
affiche l'édition archivée ; un worker GitHub distinct la prépare chaque matin.

## Mise en service

Suivre les étapes détaillées en haut de [SETUP.md](../SETUP.md). État au 23 septembre
2026 : migration 003 exécutée, clé OpenAI locale présente, test réel refusé avec
HTTP 429. L'utilisateur doit encore activer la facturation ou ajouter des crédits.
La génération réelle et l'archivage authentifié restent à valider. Ne relancer
aucun test API avant cette activation.

Les six secrets GitHub sont `SUPABASE_URL`, `SUPABASE_ANON_KEY`,
`SUPABASE_BRIEF_EMAIL`, `SUPABASE_BRIEF_PASSWORD`, `GIE_API_KEY`, `OPENAI_API_KEY`.
Utiliser le même compte Supabase Auth que dans l'application : les politiques RLS
réservent les briefs à son propriétaire. Aucune clé service-role n'est nécessaire.
Les clés restent dans les secrets ; aucun mot de passe ni journal personnel ne
fait partie de la requête OpenAI.

Le workflow est désactivé tant que la variable de dépôt `MARKET_BRIEF_ENABLED`
n'est pas égale à `true`. `OPENAI_BRIEF_MODEL` permet de remplacer explicitement
le modèle par défaut, `gpt-5.6-terra`, dans GitHub et dans les secrets locaux.
Il n'existe pas de changement automatique de modèle en cas d'erreur d'accès.

## Horaire et déroulement

Le workflow `.github/workflows/market_brief.yml` utilise `cron: '0 6 * * *'` et
`timezone: Europe/Paris`. Le fuseau gère les changements d'heure ; le traitement
s'exécute sur la branche par défaut, même si l'application et le PC sont fermés.
GitHub peut retarder ou manquer un lancement sous forte charge : l'horaire est
une cible, pas une garantie de disponibilité à 06:00 précises. Les dépôts publics
inactifs peuvent voir leur planification suspendue après 60 jours.
Voir [les règles officielles GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

Le worker :

1. S'authentifie auprès de Supabase avec le compte du dashboard.
2. Vérifie si l'édition existe ou si une tentative est déjà en cours.
3. Actualise et archive les instantanés GIE AGSI UE, ALSI UE et météo Paris.
4. Réserve atomiquement une tentative, puis appelle l'API OpenAI avec recherche web.
5. Archive le résultat et ferme uniquement sa propre session Supabase.

Un retard ou un lancement manuel conserve l'heure réelle des données et de la
génération ; le brief n'est jamais antidaté à 6 h. Avant 6 h, aucun nouveau brief
n'est généré et Morning affiche, si disponible, l'édition précédente.

## Contenu et provenance

La consigne vise **180–260 mots en français**, avec quatre blocs : À retenir,
Ce qui fait bouger le TTF, Lecture options, À surveiller aujourd'hui. Les faits
portent sur les dernières 24 heures, week-end inclus le lundi. Les sources
primaires sont prioritaires. Les implications pour les échéances, la volatilité
ou le skew sont conditionnelles et distinguées des observations de marché.

L'API [Responses avec recherche web](https://developers.openai.com/api/docs/guides/tools-web-search)
est appelée avec `tool_choice="required"`, `external_web_access=true`, au maximum
cinq appels d'outils et 2 400 tokens de sortie. `store=false` désactive le stockage
de la réponse pour récupération ultérieure via l'API ; cela n'est pas une promesse
d'absence de toute rétention côté fournisseur. L'application conserve sa propre
archive Supabase. Le modèle par défaut est documenté sur
[la page officielle GPT-5.6 Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra).

Le contexte envoyé contient uniquement les métriques publiques normalisées des
trois flux autorisés : valeurs, unités, dates, variations, statut estimé, écarts
saisonniers, prévision Paris et indicateur d'échec d'actualisation. Les URL des
sources sont prédéfinies. Les réponses brutes des fournisseurs, les notes libres,
le journal et les autres tables personnelles ne sont pas envoyés.

Le parseur exige une réponse terminée, une recherche web terminée et des citations
URL valides. Il préserve le texte des faits annotés et ajoute des liens cliquables
au fil du texte. Une réponse tronquée ou sans citations est refusée. Cette
validation structurelle ne garantit pas l'exactitude ou l'exhaustivité des faits :
les liens et l'heure de génération restent visibles pour vérifier l'analyse.

Aucun fournisseur de prix TTF/options n'est connecté. Le modèle ne doit pas
inventer de prix, IV, RR, Greeks ou flux. Un prix cité dans l'actualité doit être
daté et attribué à un contrat et une source. Paris reste un indicateur météo local,
sans pondération de la demande européenne ni calcul de révision des prévisions.
Un flux indisponible reste signalé, avec le dernier instantané de même source.

## Archivage et contrôle des appels

`market_brief_runs` réserve une tentative unique par utilisateur/date/numéro.
`market_briefs` conserve son résultat : statut, texte, citations, contexte public,
réponse API brute, usage, modèle, version de consigne et horodatages. Un résultat
est lié à une tentative du même propriétaire et de la même date. Les deux tables
autorisent uniquement SELECT/INSERT pour leur propriétaire ; aucune modification
de l'historique n'est prévue.

L'ouverture de Morning ne génère rien. Après un succès, un nouveau lancement
réutilise l'édition existante. En cas d'échec, aucune relance payante automatique
n'est effectuée. Une seule relance manuelle est possible, via le bouton du
dashboard ou l'entrée **retry** du workflow. Une tentative sans résultat doit
avoir plus de 15 minutes pour être considérée interrompue. La limite porte sur
chaque utilisateur et chaque date ; les appels web et les tokens ont un coût
variable. Les bornes de requête ne constituent pas un plafond monétaire de compte.

Un timeout OpenAI peut avoir été facturé : le POST n'est jamais retenté
automatiquement. En cas d'échec de sauvegarde locale, le résultat reste dans la
session avec un bouton de sauvegarde sans nouvel appel API. Ne ferme pas cette
session avant de l'avoir enregistré. Si la sauvegarde échoue dans GitHub, le job
échoue et le texte n'est pas exposé dans les logs ; une interruption peut donc
laisser une tentative facturée sans brief récupérable.

## Vérifications et dépannage

- **HTTP 429** : vérifier crédits, budget du projet et limite de débit sur
  [OpenAI Platform Billing](https://platform.openai.com/settings/organization/billing/overview).
- **Clé refusée / modèle inaccessible** : vérifier le projet de la clé et les
  droits du modèle choisi, sans partager la clé dans les journaux ou le chat.
- **Job ignoré** : vérifier `MARKET_BRIEF_ENABLED=true` dans les variables de dépôt.
- **Authentification Supabase refusée** : vérifier email/mot de passe de
  l'utilisateur Auth du dashboard, distincts des identifiants administrateur.
- **Aucun brief visible** : vérifier le propriétaire des lignes et se connecter
  au dashboard avec ce même compte ; suivre [VERIFY.md](../database/VERIFY.md).
- **Échec déjà enregistré aujourd'hui** : corriger la cause, puis autoriser
  explicitement l'unique relance. Une nouvelle exécution ordinaire ne suffit pas.

`python -m pytest -q` teste citations, contexte public, RLS côté dépôt, dates
Paris/été/hiver, concurrence, absence de doublons et sauvegarde sans nouvel appel.
Les tests utilisent des réponses factices, jamais des appels payants.
`python scripts/check_supabase.py` vérifie l'accès anonyme sans tester les écritures
authentifiées. `python scripts/check_openai_brief.py --generate` effectue un vrai
appel payant et écrit, si réussi, une archive locale ignorée par Git dans
`local_exports/` ; il ne crée pas d'édition dans Supabase et n'est pas soumis au
compteur des tentatives du jour. Le lancement GitHub constitue le test complet.
