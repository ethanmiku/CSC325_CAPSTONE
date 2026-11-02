# Backend setup guide

Follow this guide to run the murder mystery backend on Windows with PowerShell.
For macOS, use [the Mac setup guide](SETUP_MAC.md).
The repository already contains the Django project and MongoDB configuration.
Do **not** run `startproject` or download the MongoDB project template again.

## Before you start

You need:

- Python **3.14**, with Python added to PATH during installation.
- Git.
- A code editor, such as VS Code.
- A MongoDB Atlas connection string and database credentials from the project administrator. Ask for these privately; do not post credentials in GitHub.
- For live NPC replies: a Claude API key with API access and an available model ID.
  These are not needed to run the automated dialogue tests.

MongoDB Atlas hosts the database. You do not need to install a local MongoDB server.
MongoDB Compass is optional for viewing database contents.

## 1. Get the repository

For a new checkout, open PowerShell in the folder where you keep your projects:

```powershell
git clone https://github.com/ethanmiku/CSC325_CAPSTONE.git
cd CSC325_CAPSTONE
```

If you already have the repository, open a terminal in its root folder and run:

```powershell
git pull
```

The repository root is the folder containing `README.md` and `backend`.

## 2. Create your Python environment

From the repository root, check Python:

```powershell
python --version
```

It should report `Python 3.14.x`. If you just installed Python, reopen your terminal
so it picks up the updated PATH.

Create a virtual environment (only needed once):

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell says running scripts is disabled, run these commands in that same terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

If prompted, enter `Y`. This policy change lasts only for the current terminal session.
Your terminal prompt should now begin with `(.venv)`.

Confirm that you are using the environment's Python:

```powershell
python -c "import sys; print(sys.executable)"
```

The path should end with `.venv\Scripts\python.exe`.

## 3. Install dependencies

With the environment active, from the repository root:

```powershell
python -m pip install -r backend/requirements.txt
python -m pip check
```

The final command should report `No broken requirements found.`
Use the requirements file so the team installs the same package versions.
It includes the Anthropic Python SDK used for NPC dialogue.

## 4. Create your local configuration

From the repository root, copy the example file:

```powershell
Copy-Item backend/.env.example backend/.env
```

Run this only when creating your configuration for the first time; do not overwrite
an existing `.env` containing your settings.

Open `backend/.env` in your editor. Its filename must be exactly `.env`, not `.env.txt`.
Replace the placeholders:

```dotenv
DJANGO_SECRET_KEY=your-own-generated-development-key
DJANGO_DEBUG=True
MONGODB_URI=your-complete-atlas-connection-string
MONGODB_DATABASE=murder_mystery_dev
ANTHROPIC_API_KEY=replace-with-your-api-key
ANTHROPIC_MODEL=replace-with-selected-model-id
```

Generate your own Django secret key:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output into `DJANGO_SECRET_KEY`. Surround the value with single quotes
in `.env` to preserve any special characters:

```dotenv
DJANGO_SECRET_KEY='paste-the-generated-value-here'
```

For `MONGODB_URI`, use the Atlas connection string supplied for your database user.
Replace any username/password placeholders. If constructing the URI yourself,
special characters in the username or password must be URL-encoded.

Keep `MONGODB_DATABASE=murder_mystery_dev` to use the shared development database.
Changes to this database can affect teammates using it.

For live dialogue, replace the two `ANTHROPIC_` placeholders with your API key and
a model ID available to your Claude API account. Leave them as placeholders if
you only need health checks or automated tests. Dialogue returns a controlled
`503 ai_unavailable` until configured. Restart Django after changing `.env`.

If you already have `.env`, add the new variables to it; do not copy over it.

Never commit `.env`, credentials, or secret keys. Commit `.env.example` with
placeholders only. The repository's `.gitignore` excludes `.env` and `.venv`.

## 5. Confirm Atlas access

Ask the Atlas project administrator to provide a database user with the permissions
needed for development and migrations.

- If Atlas network access includes `0.0.0.0/0`, you can connect from any IP address, but still need valid database credentials.
- Otherwise, ask the administrator to add your current public IP address to the project's network access list.

You do not need an Atlas dashboard invitation just to run Django.
You do not need to create another cluster.

## 6. Check Django and the database

Enter the backend folder:

```powershell
cd backend
python manage.py check
```

Expected result:

```text
System check identified no issues (0 silenced).
```

Apply migrations:

```powershell
python manage.py migrate
```

This command connects to MongoDB and applies any pending database setup.
For an already configured shared database, `No migrations to apply` is normal.
It does not reset the database.

Confirm migration status:

```powershell
python manage.py showmigrations
```

Applied migrations have `[X]` next to them.

## 7. Start the development server

From the backend folder:

```powershell
python manage.py runserver
```

Leave the terminal running and open:

- API health: http://127.0.0.1:8000/api/health/
- Admin login page: http://127.0.0.1:8000/admin/login/

Health should display `{"status":"ok"}`. The root URL `/` has no application view
and returns 404.
You do not need an admin account to view the admin login page.

Press `Ctrl+C` in the terminal to stop Django. Stopping Django does not stop Atlas
or delete its data. This local development server is for your own computer;
it is not the deployed backend for players.

## 8. Verify NPC dialogue

With the virtual environment active, from `backend`, run:

```powershell
python manage.py test dialogue --verbosity 2
```

The suite currently contains 33 tests. It does not call Claude or query MongoDB,
but Django still needs the configuration variables from step 4 to load settings.

Keep the development server running and open a second PowerShell terminal. Follow
the [API contract's PowerShell examples](docs/dialogue-api.md#manual-request-examples-powershell)
to check health, send a first message, and send a follow-up using the actual reply.
Live dialogue requests use your Claude API account and incur API charges.

The contract also includes an invalid-request example that returns `400` without
calling Claude. See the [Godot integration handoff](docs/dialogue-api.md#godot-integration-handoff)
for client responsibilities and a joint verification checklist.

## Returning to work later

Open PowerShell at the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python manage.py runserver
```

If activation is blocked, repeat the session execution policy command from step 2.
You do not need to recreate `.venv` or `.env` each time.

After pulling dependency or migration changes, from the repository root with the
environment active:

```powershell
python -m pip install -r backend/requirements.txt
cd backend
python manage.py migrate
```

## Common problems

| Problem | What to check |
| --- | --- |
| `python` is not recognized | Install Python with PATH enabled, then reopen the terminal. |
| Activation says scripts are disabled | Use the process-scoped execution policy command in step 2. |
| `No module named django` | Activate `.venv` and install `backend/requirements.txt`. |
| Cannot find `manage.py` | Run Django management commands from the `backend` folder. |
| Missing `DJANGO_SECRET_KEY` or another setting | Check that `backend/.env` exists and contains the exact variable names in step 4. |
| MongoDB authentication fails | Check database username, password, and password encoding in the URI. Your Atlas website login is separate from your database user. |
| MongoDB connection times out | Check internet access, Atlas network access, cluster availability, and the connection string. |
| MongoDB says an operation is unauthorized | Ask the administrator to check your database user's permissions. |
| Port 8000 is already in use | Stop the other server or use `python manage.py runserver 8001`, then open port 8001 in your browser. |
| `No module named anthropic` | Activate `.venv` and reinstall `backend/requirements.txt` from the repository root. |
| Dialogue returns `503 ai_unavailable` | Check the key, model ID, API access/billing, provider availability, and network access. Restart Django after editing `.env`. Provider failures intentionally share a generic response. |
| Dialogue returns `504 ai_timeout` | The Claude request timed out. Retry manually when ready; the backend does not retry automatically. |
| Dialogue returns `502 ai_invalid_response` | The provider reply was empty, oversized, or cut off at the token limit. |

When asking for help, share the error message with credentials removed.

## Ready checklist

- [ ] Python 3.14 is installed.
- [ ] The virtual environment activates.
- [ ] Dependencies install and `pip check` passes.
- [ ] Your local `.env` has actual values rather than placeholders.
- [ ] Atlas permits your connection and database user.
- [ ] Django `check` and `migrate` succeed.
- [ ] The local server responds in your browser.
- [ ] The automated dialogue suite passes.
- [ ] If testing live dialogue, a first message and contextual follow-up succeed.

The backend supports the local NPC dialogue MVP. The Godot client integrates with
the endpoints described in the [API contract](docs/dialogue-api.md).
