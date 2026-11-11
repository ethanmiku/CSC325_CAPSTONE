# AGENTS.md

Guidance for AI coding agents working in this repository. `CLAUDE.md` is a symlink to this file.

## Project

A murder-mystery game for CSC 325 (Farmingdale State College). The player explores a manor, collects evidence and interviews suspects whose replies come from Claude.

- `game/`: Godot 4.7 client (GDScript, Mobile renderer, Android target).
- `backend/`: Django REST API on Python 3.14 with MongoDB. It owns NPC data, prompts, validation and all Claude access.
- `.github/workflows/ci-cd.yml`: CI for both sides.

The client talks to the backend over HTTP. The API contract is in `backend/docs/dialogue-api.md`; change the contract and both sides together.

## Layout

- `game/entities/`: player and NPCs. `game/maps/`: rooms and scenes. `game/ui/`: dialogue box, touch controls, settings, and all game UI elements. `game/services/`: autoloads such as `ClaudeDialogue`.
- `game/tests/`: headless test scenes.
- `backend/dialogue/`, `backend/evidence/`: Django apps. `backend/config/`: settings; `settings_ci.py` is what CI uses.

## Checks to run before committing

Backend, from `backend/`:

```sh
python -m pip install -r requirements.txt
python manage.py check --settings=config.settings_ci
python manage.py test --settings=config.settings_ci --verbosity 2
```

Run them from `backend/`. From the repository root Django finds zero tests and still reports success.

Game, from the repository root, with Godot 4.7.2:

```sh
godot --headless --path game --import
godot --headless --path game res://tests/<name>_test.tscn
```

The import must print no `SCRIPT ERROR`. Run it first on a fresh clone: `game/.godot/` is not committed, and without it `class_name` types don't resolve.

## Game tests

CI runs every scene named `game/tests/<name>_test.tscn`. A test scene must call `get_tree().quit(1)` when any check fails and `quit(0)` otherwise. Scenes in `game/tests/` without the `_test` suffix are helpers and are not run.

## Conventions

- Commit messages: `feat:`, `fix:`, `test:`, `docs:` or `ci:`, then a short summary in plain words. One commit per addition, feature, fix or change. Don't bundle unrelated changes into one large commit.
- Documentation: `backend/docs` and `game/docs` exist to document work done by agents. Write one Markdown file per feature or topic (`backend/docs/<topic>.md` or `game/docs/<topic>.md`), and update the existing file when the topic already has one. Each file explains what was done, why it was done, and the author(s) of the change.
- Work on a feature branch and open a pull request to `main`. Don't push to `main`.
- Never commit `.env` files, API keys, `game/.godot/` or `game/android/`.
- Commit the `.import` and `.uid` files Godot writes next to assets and scripts.
- Tests must not call the real Claude API or need a running MongoDB. The default backend suite mocks both.
