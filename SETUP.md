# Your setup steps

## Activer le brief TTF de 6 h (2026-09-23)

Les migrations **002 et 003 sont déjà exécutées** et les clés GIE/OpenAI sont
présentes localement. Ne recrée pas les clés et ne relance pas ces migrations.
Morning utilise maintenant des cartes colorées et des graphiques ; la navigation
contient uniquement Market Dashboard et Workspace.

1. Ouvre [la facturation OpenAI Platform](https://platform.openai.com/settings/organization/billing/overview),
   ajoute ton moyen de paiement et active la facturation ou ajoute des crédits.
   Vérifie que la clé utilisée appartient au projet disposant du budget nécessaire.
   Le premier test a reçu HTTP 429 ; aucun nouvel appel ne sera lancé automatiquement
   depuis le dashboard. L'API utilise sa propre facturation.
2. Dans [les secrets Actions de ton dépôt](https://github.com/jmouchet/Dashboard-European-Gas-Options/settings/secrets/actions),
   clique **New repository secret** pour chacune des six lignes :

   | Nom exact | Valeur à saisir dans GitHub |
   | --- | --- |
   | `SUPABASE_URL` | `https://gxnliymqvplnwoahxscf.supabase.co` |
   | `SUPABASE_ANON_KEY` | La clé publique déjà dans ton fichier local |
   | `SUPABASE_BRIEF_EMAIL` | L'email utilisé pour te connecter au dashboard |
   | `SUPABASE_BRIEF_PASSWORD` | Le mot de passe de ce même compte du dashboard |
   | `GIE_API_KEY` | La clé GIE déjà dans ton fichier local |
   | `OPENAI_API_KEY` | La clé OpenAI déjà dans ton fichier local |

   Copie uniquement les valeurs, sans les guillemets TOML. Le compte du dashboard
   est un utilisateur **Supabase Auth**, distinct de ton compte d'administration
   Supabase. Son identité permet d'archiver les briefs dans ton espace privé.
   N'utilise ni le mot de passe PostgreSQL ni une clé service-role.
3. Dans **Settings → Secrets and variables → Actions → Variables**, ajoute
   `MARKET_BRIEF_ENABLED` avec la valeur exacte `true`. Ne l'active qu'une fois
   la facturation et tous les secrets prêts. Le modèle par défaut est
   `gpt-5.6-terra` ; `OPENAI_BRIEF_MODEL` est une variable facultative pour le changer.
4. Ouvre **Actions → Morning TTF brief → Run workflow**, branche `main`.
   Laisse **retry** décoché pour le premier lancement. Attends le résultat vert,
   puis ouvre Morning en étant connecté avec le même compte.
   Vérifie la date du brief, ses sources et sa présence après rechargement.
5. Après un échec, corrige la cause indiquée dans le journal du workflow. Pour
   relancer le même jour, coche **retry** : cela autorise un nouvel appel facturé,
   limité à une seule relance. Un brief déjà réussi n'est pas régénéré.

La tâche est programmée tous les jours à **6 h Europe/Paris**, ordinateur éteint
compris, avec changement d'heure automatique. GitHub peut retarder son démarrage
et la rédaction prend du temps : la disponibilité à 6 h précises n'est pas
garantie. Aucun site hébergé n'est nécessaire pour générer le brief ; l'application
locale doit toujours être ouverte pour le consulter.

Pour suspendre les appels planifiés, passe `MARKET_BRIEF_ENABLED` à `false`.
Ne partage aucune clé ni aucun mot de passe dans le chat. Détails techniques et
dépannage : [docs/MARKET_BRIEF.md](docs/MARKET_BRIEF.md).

## Utiliser les données du Market Dashboard

Migrations 002 and 003 are applied. **Do not run them again.** GIE access is configured.

1. Open [the dashboard](http://127.0.0.1:8501). If it is stopped, double-click
   **Start Dashboard.cmd**. Sign in with your existing app account.
2. Open **Market Dashboard → Morning**. The first signed-in visit fetches the
   available five-year-plus storage history, LNG history and weather forecast.
   Allow the initial retrieval to finish. Check the gas-day dates and feed status.
3. Open **Fundamentals** to select a country, inspect seasonal storage or explore
   LNG and weather. **Physical System** loads GIE infrastructure datasets;
   **Events** loads GIE service announcements.
4. Open **Data / Admin** to inspect/export the loaded raw and normalized snapshots.
   In Supabase Table Editor, confirm `market_feed_batches` and `ingestion_runs`
   contain your user-owned rows. Sign out/in and return to Morning to verify reuse.

Morning refreshes automatically while its session remains active. GIE history is
checked every six hours, weather hourly, directories daily; the refresh buttons
check immediately. Once activated, the brief's GitHub worker refreshes EU storage,
EU LNG and Paris weather with Streamlit closed. No additional weather key is
needed. TTF futures/options remain unavailable until a provider is selected.
Existing manual observations are accessible in Data / Admin.

The environment uses PyArrow 24.0.0: Windows Smart App Control blocked the 25.0.1
compute DLL on this computer. The compatible official wheel was tested without
changing Windows security settings. `requirements.txt` pins that version.

The remaining instructions are for a fresh installation. Full data definitions,
refresh behavior and limitations are in [docs/MARKET_DATA.md](docs/MARKET_DATA.md).

Existing services:

- [GitHub repository](https://github.com/jmouchet/Dashboard-European-Gas-Options)
- [Supabase project dashboard](https://supabase.com/dashboard/project/gxnliymqvplnwoahxscf)
- Supabase API URL: `https://gxnliymqvplnwoahxscf.supabase.co`

The public API key is now configured in the ignored local secrets file and its
connection check passed. Keep keys in local secrets; the scheduled worker also
needs the six GitHub secrets described above. Never send credentials in chat.

On 2026-09-14, you confirmed that sign-in and saving records across sign-out/sign-in
work. Supabase setup is complete for the initial manual workflow, and the first
version is now published to GitHub. The remaining setup instructions serve as a
reference for a fresh installation.

## 1. Install and launch locally

Open PowerShell in `C:\Users\jules\Desktop\Apex\Gas Dashboard`. Run separately:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Run each command to completion before starting the next one. `KeyboardInterrupt`
means the command was interrupted, usually with Ctrl+C. Environment creation can
take time while pip is installed. If interrupted, first check whether pip is ready:

```powershell
.\.venv\Scripts\python.exe -m pip --version
```

If that works, skip environment creation and continue with dependency installation.
If it fails, share the error text before proceeding. No activation command is needed:
these commands call the environment's Python directly. A quoted path alone in
PowerShell only prints text; it does not execute a program or activate an environment.

Open [localhost:8501](http://localhost:8501). The app should show Morning with empty
metric cards. All seven pages are accessible without credentials. API ingestion
requires sign-in to archive data. Keep that terminal
open while using the app; `Ctrl+C` stops it. Use a second terminal for tests.

After installation, you can double-click **Start Dashboard.cmd** in this folder
for later launches. Keep its window open. The browser address works only while
Streamlit is running; a failed-to-load page before launch is expected.

If a package has no wheel for the installed Python 3.14, report the exact error
before changing versions. The GitHub workflows use Python 3.13.

## 2. Create the Supabase schema

Open the project dashboard linked above, then **SQL Editor → New query**.

1. Inspect the table list first. If the project already has any tables named in
   `database/migrations/001_initial.sql`, stop and tell me which ones exist.
2. Open [001_initial.sql](database/migrations/001_initial.sql), copy its contents
   into the SQL editor and run it **once**.
3. Run [002_market_dashboard.sql](database/migrations/002_market_dashboard.sql)
   once after 001. It adds five market tables and preserves existing records.
4. Run [003_market_briefs.sql](database/migrations/003_market_briefs.sql) once
   after 002. It adds private brief archives and daily attempt tracking.
5. Confirm the tables appear in Table Editor. The legacy curriculum seed is
   optional; Build Understanding is no longer registered in the app.

The initial migration creates tables, access policies and one derived view. It does
not delete existing data. If SQL reports an error, share that error before running
further SQL; do not disable RLS to get around it.

## 3. Create your app login

In **Authentication → Users**, use **Add user → Create new user** to create your
personal email/password account. Confirm the user there if required. Keep
self-service sign-ups disabled in the authentication settings for this personal
application. This app has sign-in only; it does not register new users.

The app login is a Supabase Auth user, distinct from your Supabase dashboard login.
Do not share that password with me.

## 4. Add the public connection key locally

In Supabase project settings, open **API Keys** and locate a **publishable key**,
or the legacy **anon** key. [Supabase explains these key types here](https://supabase.com/docs/guides/getting-started/api-keys).

Run this command once, only if `.streamlit/secrets.toml` does not already exist:

```powershell
Copy-Item -LiteralPath .streamlit/secrets.toml.example -Destination .streamlit/secrets.toml
```

Open `.streamlit/secrets.toml` in your editor. The project URL is already filled in.
Replace the key placeholder:

```toml
SUPABASE_URL = "https://gxnliymqvplnwoahxscf.supabase.co"
SUPABASE_ANON_KEY = "your-publishable-or-legacy-anon-key"
GIE_API_KEY = "your-gie-api-key"
```

The variable name remains `SUPABASE_ANON_KEY` for both supported public key types.
Do not use a service-role key, server secret key or database password. The app
rejects privileged key types and the secrets file is ignored by Git. `.env.example`
is a reference only; `.env` files are not loaded automatically.

Restart Streamlit. Export any preview records first, then sign in from the sidebar
using the account from step 3. Signing in clears session-preview state; there is
no automatic import into your permanent records.

## 5. Verify permanent storage

1. In Data / Admin, add one real, public observation with its exact contract/scope, unit and source.
2. Save one short journal entry.
3. Open Morning while signed in and wait for the market feeds to be archived.
4. Reload the browser, sign in again and confirm those records remain.
5. Check **Data / Admin** and download a JSON export.
6. Follow [database/VERIFY.md](database/VERIFY.md) to check account isolation.

Tell me which steps pass and send any error messages with secrets removed. Once
these pass, I can help finish runtime verification and prepare the next increment.

## 6. Connect GitHub after the local tests pass

This local folder now has a Git repository on `main`, with `origin` pointing to
your GitHub repository. The local secrets file and environment are confirmed
ignored. The initial version has been pushed to `main`, which tracks `origin/main`.

The following initialization commands are only for a fresh folder without `.git`;
skip them on this computer:

```powershell
git init -b main
git remote add origin https://github.com/jmouchet/Dashboard-European-Gas-Options.git
git status --short
git check-ignore .streamlit/secrets.toml
```

The last command should print `.streamlit/secrets.toml` after you create it. Check
that no secrets or exports appear in files to be committed. Then:

```powershell
git add .
git diff --cached --stat
git commit -m "Build initial manual gas intelligence dashboard"
git push -u origin main
```

Git may open its normal GitHub sign-in flow. Authenticate there; never paste a
GitHub token into chat. If this folder already has Git metadata, inspect
`git status` and `git remote -v` instead of repeating initialization. If the remote
gains commits, fetch and review them before pushing; do not force-push.

A GitHub Actions test workflow is included. Check its result after pushing. That
workflow tests code; it does not deploy the app or access Supabase credentials.

## 7. Deployment comes after verification

Local use is sufficient for the first manual version. Once tests, persistence and
account isolation pass, choose whether to host the Streamlit app for phone access.
I will ask about deployment then and provide the specific steps for the chosen
host. No hosted app has been created by this build.
