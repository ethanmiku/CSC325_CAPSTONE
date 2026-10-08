# Backend setup on macOS

Follow these steps in the macOS **Terminal** app or your code editor's terminal.
The Django project is already in the repository. Do **not** run `startproject`
or download the MongoDB template again.

## Before you start

You need:

- Python **3.14**. You can install it using the macOS installer from [python.org](https://www.python.org/downloads/macos/).
- Git. Check with `git --version`. If macOS prompts you to install Command Line Tools, follow the prompt.
- A code editor, such as VS Code.
- A MongoDB Atlas connection string and database credentials from the project administrator, shared privately.

MongoDB runs in Atlas, so no local MongoDB server is required.
MongoDB Compass is optional for inspecting data.

## 1. Get the repository

Open Terminal in the folder where you keep your projects, then run:

```bash
git clone https://github.com/ethanmiku/CSC325_CAPSTONE.git
cd CSC325_CAPSTONE
```

If you already cloned the repository, open its root folder in Terminal and run:

```bash
git pull
```

The repository root contains `README.md` and the `backend` folder.
If GitHub asks you to authenticate, use your own GitHub account.

## 2. Check Python and create your environment

From the repository root:

```bash
python3.14 --version
```

Expected: `Python 3.14.x`. If you just installed Python, reopen Terminal.
If `python3.14` is not found, try `python3 --version`. Use `python3` in the next
command only if it reports version 3.14.

Create the environment once:

```bash
python3.14 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Your prompt should show `(.venv)`.

Verify the active interpreter:

```bash
python --version
python -c "import sys; print(sys.executable)"
```

The version should be 3.14 and the path should end with `.venv/bin/python`.
After activation, use `python` for the remaining commands.

## 3. Install dependencies

From the repository root, with the environment active:

```bash
python -m pip install -r backend/requirements.txt
python -m pip check
```

Expected: `No broken requirements found.` Use the committed requirements file
so everyone installs the same package versions.

## 4. Create your local configuration

For your first setup, from the repository root:

```bash
cp backend/.env.example backend/.env
```

Do not repeat this command if `.env` already contains your configuration;
it would overwrite that file. Files starting with a dot are hidden in Finder.
Press `Command+Shift+.` to show them, or open `.env` through your code editor.

Edit `backend/.env` with these values:

```dotenv
DJANGO_SECRET_KEY='your-own-generated-development-key'
DJANGO_DEBUG=True
MONGODB_URI=your-complete-atlas-connection-string
MONGODB_DATABASE=murder_mystery_test
```

Generate your own secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Paste the output between the single quotes for `DJANGO_SECRET_KEY`.
Keep it in `.env`; do not paste it into a shell command.

For `MONGODB_URI`, use the connection string for your database user, with all
username/password placeholders replaced. If constructing the URI yourself,
special characters in the username or password must be URL-encoded.

The filename must be exactly `.env`, not `.env.txt`. Use a plain text editor.
Never commit this file or share its credentials publicly. `.env.example` contains
placeholders and is safe to commit; `.env` and `.venv` are ignored by Git.

## 5. Confirm Atlas access

Ask the project administrator for a database user with permissions for development
and migrations. Your Atlas website account and your database user are separate.

- If the project's network access includes `0.0.0.0/0`, no individual IP entry is needed. You still need valid database credentials.
- Otherwise, ask the administrator to allow your current public IP address.

You do not need to create a new cluster or receive an Atlas dashboard invitation
just to run Django. Using `murder_mystery_test` connects you to the shared development
database, so changes to its data may affect teammates.

## 6. Verify Django and MongoDB

Enter the backend folder and check configuration:

```bash
cd backend
python manage.py check
```

Expected:

```text
System check identified no issues (0 silenced).
```

Apply the database migrations:

```bash
python manage.py migrate
```

This connects to MongoDB and applies pending database setup.
`No migrations to apply` is normal when the shared database is already configured.
It does not reset the database.

Inspect migration status:

```bash
python manage.py showmigrations
```

Applied migrations should have `[X]` next to them.

## 7. Start the server

From the backend folder:

```bash
python manage.py runserver
```

Leave Terminal running and open:

- http://127.0.0.1:8000/ — Django's welcome page while the project has its initial URL setup.
- http://127.0.0.1:8000/admin/login/ — the admin login page. You do not need an admin account to view it.

Stop Django with `Control+C`. Atlas keeps running independently and retains its data.
This server runs locally on your Mac; it is not the deployed backend for players.

## Returning to work later

Open a new terminal at the repository root:

```bash
source .venv/bin/activate
cd backend
python manage.py runserver
```

You do not need to recreate `.venv` or `.env`.
To leave the virtual environment, run `deactivate`.

After pulling dependency or migration changes, from the repository root with the
environment active:

```bash
python -m pip install -r backend/requirements.txt
cd backend
python manage.py migrate
```

## Common problems

| Problem | What to check |
| --- | --- |
| `python3.14: command not found` | Install Python 3.14 and reopen Terminal. Check `python3 --version` before using it instead. |
| Cannot find `.venv/bin/activate` | Make sure you are at the repository root and created `.venv` there. |
| `No module named django` | Activate the environment and install requirements. |
| Cannot find `manage.py` | Run Django management commands inside `backend`. |
| Missing environment variable | Check `backend/.env`, its filename, and the exact variable names in step 4. |
| MongoDB authentication fails | Check your database credentials and URI password encoding. |
| MongoDB connection times out | Check internet access, Atlas network access, cluster availability, and the connection string. |
| MongoDB operation is unauthorized | Ask the administrator to check your database user's permissions. |
| TLS certificate verification fails after installing Python from python.org | Run the installer's `Install Certificates.command` in the Python 3.14 folder under Applications; keep certificate verification enabled. |
| Port 8000 is in use | Stop the other server or run `python manage.py runserver 8001` and open http://127.0.0.1:8001/. |

Share error messages with credentials removed when asking for help.

## Ready checklist

- [ ] Python 3.14 is available.
- [ ] The virtual environment is active.
- [ ] Dependencies install and `pip check` passes.
- [ ] `.env` contains your actual configuration.
- [ ] Atlas permits your connection and database user.
- [ ] Django `check` and `migrate` succeed.
- [ ] The server responds in your browser.

Once these pass, your initial backend setup is complete. Game APIs and AI dialogue
will be added during development.
