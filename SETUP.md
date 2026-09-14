# Your setup steps

The local environment was repaired and dependencies installed on 2026-09-14.
All 48 tests passed, including the UI workflows. On this computer, you can now
skip installation and use **Start Dashboard.cmd** for subsequent launches. The
commands below remain available for setting up a fresh environment.

Existing services:

- [GitHub repository](https://github.com/jmouchet/Dashboard-European-Gas-Options)
- [Supabase project dashboard](https://supabase.com/dashboard/project/gxnliymqvplnwoahxscf)
- Supabase API URL: `https://gxnliymqvplnwoahxscf.supabase.co`

The public API key is now configured in the ignored local secrets file and its
connection check passed. Keep keys in local secrets and enter the app password
only in the sign-in form. Never send credentials in chat.

On 2026-09-14, you confirmed that sign-in and saving records across sign-out/sign-in
work. Supabase setup is complete for the initial manual workflow. The next step is
the first GitHub commit; the remaining setup instructions serve as a reference.

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
metric cards. All six pages are accessible without credentials. Keep that terminal
open while using the app; `Ctrl+C` stops it. Use a second terminal for tests.

After installation, you can double-click **Start Dashboard.cmd** in this folder
for later launches. Keep its window open. The browser address works only while
Streamlit is running; a failed-to-load page before launch is expected.

If a package has no wheel for the installed Python 3.14, report the exact error
before changing versions. Python 3.13 is configured in the prepared GitHub test
workflow, but it has not been run yet.

## 2. Create the Supabase schema

Open the project dashboard linked above, then **SQL Editor → New query**.

1. Inspect the table list first. If the project already has any tables named in
   `database/migrations/001_initial.sql`, stop and tell me which ones exist.
2. Open [001_initial.sql](database/migrations/001_initial.sql), copy its contents
   into the SQL editor and run it **once**.
3. Open [seed.sql](database/seed.sql), copy its contents into a new query and run it.
4. In Table Editor, verify `knowledge_articles` contains 10 rows and `questions`
   contains 20. Personal-data tables should initially be empty.

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
```

The variable name remains `SUPABASE_ANON_KEY` for both supported public key types.
Do not use a service-role key, server secret key or database password. The app
rejects privileged key types and the secrets file is ignored by Git. `.env.example`
is a reference only; `.env` files are not loaded automatically.

Restart Streamlit. Export any preview records first, then sign in from the sidebar
using the account from step 3. Signing in clears session-preview state; there is
no automatic import into your permanent records.

## 5. Verify permanent storage

1. Add one real, public observation with its exact contract/scope, unit and source.
2. Save one short journal entry.
3. Answer a quiz question, reveal the answer and save a self-assessment.
4. Reload the browser, sign in again and confirm those records remain.
5. Check **Data / Admin** and download a JSON export.
6. Follow [database/VERIFY.md](database/VERIFY.md) to check account isolation.

Tell me which steps pass and send any error messages with secrets removed. Once
these pass, I can help finish runtime verification and prepare the next increment.

## 6. Connect GitHub after the local tests pass

This local folder now has a Git repository on `main`, with `origin` pointing to
your GitHub repository. The local secrets file and environment are confirmed
ignored. No branch or commit has been pushed.

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
