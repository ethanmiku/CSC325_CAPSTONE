#!/bin/bash
# macOS setup: downloads Godot, sets up the Python virtual environment, and
# sets up backend/.env for local development. Windows uses install-prereqs.ps1.
# Usage: bash install-prereqs.sh

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_EXAMPLE="$SCRIPT_DIR/backend/.env.example"
ENV_FILE="$SCRIPT_DIR/backend/.env"
REQUIREMENTS="$SCRIPT_DIR/backend/requirements.txt"
VENV_DIR="$SCRIPT_DIR/.venv"

GODOT_URL="https://downloads.godotengine.org/?version=4.7.2&flavor=stable&slug=macos.universal.zip&platform=macos.universal"

# Characters Django uses for its generated secret keys.
SECRET_KEY_CHARS='a-z0-9!@#$%^&*(_=+)-'

# Edit these to change what each step shows.
GODOT_TITLE="Step 1: Download Godot 4.7.2 for macOS"
GODOT_PROMPT="Opens the Godot 4.7.2 macOS download in your browser.
Choose Skip if you already have Godot 4.7.2 installed."

VENV_TITLE="Step 2: Python virtual environment"
VENV_PROMPT="Creates .venv in the repository root with Python 3.14 and
installs the packages from backend/requirements.txt into it."

ENV_TITLE="Step 3: Set up backend/.env"
ENV_PROMPT="Copies backend/.env.example to backend/.env and can walk you
through filling in each value."

show_banner() {
    echo
    echo "=================================================="
    echo "  $1"
    echo "=================================================="
    echo "$2"
    echo "=================================================="
}

# Shows a step's title and message, then asks to continue.
# Returns 0 to run the step, 1 to skip it.
show_prompt() {
    show_banner "$1" "$2"
    confirm "Do you wish to continue?"
}

# Asks a y/N question. Returns 0 for yes, 1 for anything else.
confirm() {
    local answer
    read -r -p "$1 [y/N]: " answer
    case "$answer" in
        [yY] | [yY][eE][sS]) return 0 ;;
        *) return 1 ;;
    esac
}

open_url() {
    if [ "$(uname -s)" = "Darwin" ]; then
        open "$1"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$1" >/dev/null 2>&1
    else
        return 1
    fi
}

godot_step() {
    local choice
    show_banner "$GODOT_TITLE" "$GODOT_PROMPT"
    echo "  1) Download"
    echo "  2) Skip"
    echo "  3) Exit"
    while true; do
        read -r -p "Enter 1, 2, or 3: " choice
        case "$choice" in
            1) download_godot; return ;;
            2) echo "Skipping Godot download."; return ;;
            3) echo "Exiting."; exit 0 ;;
            *) echo "Invalid choice." ;;
        esac
    done
}

download_godot() {
    echo
    echo "Opening the Godot download in your browser:"
    echo "  $GODOT_URL"
    if ! open_url "$GODOT_URL"; then
        echo "Could not open a browser. Copy the link above into your browser instead."
    fi
    echo "When it finishes, unzip it and move Godot.app to your Applications folder."
}

# Prints the first Python command that runs, or nothing if none do.
find_python() {
    local p
    for p in python3.14 python3 python; do
        if command -v "$p" >/dev/null 2>&1 && "$p" --version >/dev/null 2>&1; then
            echo "$p"
            return
        fi
    done
}

setup_venv() {
    local python version activate

    echo
    python="$(find_python)"
    if [ -z "$python" ]; then
        echo "Python 3.14 was not found. Install it (see backend/SETUP_MAC.md)"
        echo "and rerun this script."
        return
    fi

    version="$("$python" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')"
    echo "Using $python (Python $version)."
    case "$version" in
        3.14.*) ;;
        *) echo "Warning: this project expects Python 3.14. Continuing with $version." ;;
    esac

    if [ -f "$VENV_DIR/bin/activate" ] || [ -f "$VENV_DIR/Scripts/activate" ]; then
        echo "Reusing existing .venv."
    else
        echo "Creating .venv..."
        if ! "$python" -m venv "$VENV_DIR" </dev/null; then
            echo "Error: could not create .venv."
            return
        fi
    fi

    # Git Bash on Windows puts the activate script in Scripts/ instead of bin/.
    if [ -f "$VENV_DIR/bin/activate" ]; then
        activate="$VENV_DIR/bin/activate"
    else
        activate="$VENV_DIR/Scripts/activate"
    fi

    # Activate scripts can reference unset variables such as PS1.
    set +u
    # shellcheck disable=SC1090
    . "$activate"
    set -u

    echo
    echo "Installing packages from backend/requirements.txt..."
    if ! python -m pip install --upgrade pip </dev/null; then
        echo "Error: could not upgrade pip."
        echo "Activate .venv and run: python -m pip install --upgrade pip"
        return
    fi
    if ! python -m pip install -r "$REQUIREMENTS" </dev/null; then
        echo "Error: could not install the packages."
        echo "Activate .venv and run: python -m pip install -r backend/requirements.txt"
        return
    fi
    if ! python -m pip check </dev/null; then
        echo "Error: pip check found dependency problems."
        return
    fi
    echo "Packages installed."
}

# Prints a random 50-character Django secret key.
generate_secret_key() {
    LC_ALL=C tr -dc "$SECRET_KEY_CHARS" < /dev/urandom | head -c 50
}

# Prints each KEY from an env file, skipping blank lines and comments.
list_env_keys() {
    local line
    while IFS= read -r line || [ -n "$line" ]; do
        case "$line" in
            '' | '#'*) continue ;;
            *=*) echo "${line%%=*}" ;;
        esac
    done < "$1"
}

fill_env_interactively() {
    local tmp_file line key default value
    local set_keys="" blank_keys=""
    tmp_file="$(mktemp "${ENV_FILE}.XXXXXX")" || exit 1

    echo
    echo "Press Enter to keep the value shown in [brackets], or enter 1 to leave it blank."
    # The env file is read on fd 3 so the prompts can still read from stdin.
    while IFS= read -r line <&3 || [ -n "$line" ]; do
        case "$line" in
            [A-Za-z_]*=*) ;;
            *)
                printf '%s\n' "$line" >> "$tmp_file"
                continue ;;
        esac
        key="${line%%=*}"
        default="${line#*=}"

        if [ "$key" = "DJANGO_SECRET_KEY" ]; then
            read -r -p "$key [Enter = generate a new key]: " value
            if [ -z "$value" ]; then
                # Single quotes keep characters like # and $ literal for dotenv.
                default="'$(generate_secret_key)'"
                echo "Generated a new secret key."
            fi
        else
            read -r -p "$key [$default]: " value
        fi

        if [ "$value" = "1" ]; then
            value=""
            blank_keys="$blank_keys $key"
        elif [ -z "$value" ]; then
            value="$default"
            set_keys="$set_keys $key"
        else
            set_keys="$set_keys $key"
        fi
        printf '%s=%s\n' "$key" "$value" >> "$tmp_file"
    done 3< "$ENV_FILE"

    mv "$tmp_file" "$ENV_FILE"

    echo
    echo "Saved $ENV_FILE"
    echo "  Set:${set_keys:- (none)}"
    echo "  Left blank:${blank_keys:- (none)}"
}

setup_env() {
    local choice key

    echo
    if [ ! -f "$ENV_EXAMPLE" ]; then
        echo "Error: $ENV_EXAMPLE was not found."
        return
    fi

    if [ -f "$ENV_FILE" ]; then
        if ! confirm "backend/.env already exists. Overwrite it?"; then
            echo "Keeping the existing backend/.env."
            return
        fi
    fi

    cp "$ENV_EXAMPLE" "$ENV_FILE"
    echo "The env file has been set up at backend/.env and is ready to be filled out."
    echo
    echo "How would you like to fill it out?"
    echo "  1) Manually (edit backend/.env yourself)"
    echo "  2) Be prompted for each value"
    while true; do
        read -r -p "Enter 1 or 2: " choice
        case "$choice" in
            1)
                echo "Open $ENV_FILE in your editor and replace the placeholder values."
                return ;;
            2) break ;;
            *) echo "Invalid choice." ;;
        esac
    done

    echo
    echo "You will be asked for the following values:"
    for key in $(list_env_keys "$ENV_FILE"); do
        echo "  - $key"
    done
    echo
    if ! confirm "Do you wish to continue?"; then
        echo "Open $ENV_FILE in your editor and replace the placeholder values."
        return
    fi

    fill_env_interactively
}

show_next_steps() {
    cat <<'EOF'

==================================================
  Setup complete
==================================================
To start the backend, run these from the repository root:
  source .venv/bin/activate
  cd backend
  python manage.py check
  python manage.py migrate
  python manage.py runserver

check and migrate need your real MONGODB_URI in backend/.env.
Then open http://127.0.0.1:8000/api/health/ in your browser.
It should show {"status":"ok"}. Stop the server with Control+C.

To run the game:
  1. Open Godot and click Import.
  2. Choose game/project.godot from this repository.
  3. Press Cmd+B to run the project.
==================================================
EOF
}

godot_step

if show_prompt "$VENV_TITLE" "$VENV_PROMPT"; then
    setup_venv
else
    echo "Skipping virtual environment setup."
fi

if show_prompt "$ENV_TITLE" "$ENV_PROMPT"; then
    setup_env
else
    echo "Skipping env file setup."
fi

show_next_steps
