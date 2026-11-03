"""Isolated settings for automated tests; no external credentials required."""

import os
import secrets
from unittest.mock import patch

# Supply configuration before importing settings.py, which also loads .env.
# Explicit values prevent local or runner credentials from entering this suite.
with patch.dict(os.environ, {
    'DJANGO_SECRET_KEY': secrets.token_urlsafe(50),
    'DJANGO_DEBUG': 'False',
    'MONGODB_URI': 'mongodb://127.0.0.1:27017',
    'MONGODB_DATABASE': 'murder_mystery_ci',
    'ANTHROPIC_API_KEY': '',
    'ANTHROPIC_MODEL': '',
}):
    from .settings import *  # noqa: F403

# Current tests prohibit database access and mock Claude HTTP responses.
# Fail rather than accidentally enabling live Claude requests.
ANTHROPIC_API_KEY = ''
ANTHROPIC_MODEL = ''
