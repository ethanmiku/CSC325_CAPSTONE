"""Claude integration for validated dialogue requests."""

import anthropic
from django.conf import settings
from rest_framework.exceptions import APIException

from .npc_data import get_npc
from .prompts import build_npc_prompt


class AIUnavailable(APIException):
    status_code = 503
    default_code = 'ai_unavailable'
    default_detail = 'The character cannot respond right now. Please try again.'


class AITimeout(APIException):
    status_code = 504
    default_code = 'ai_timeout'
    default_detail = 'The character took too long to respond. Please try again.'


class AIInvalidResponse(APIException):
    status_code = 502
    default_code = 'ai_invalid_response'
    default_detail = 'The character returned an unusable reply. Please try again.'


def generate_reply(npc_id, message, history):
    npc = get_npc(npc_id)
    api_key = settings.ANTHROPIC_API_KEY.strip()
    model = settings.ANTHROPIC_MODEL.strip()
    if not api_key or not model or api_key.startswith('replace-with-') or model.startswith('replace-with-'):
        raise AIUnavailable()

    messages = [dict(turn) for turn in history]
    messages.append({'role': 'user', 'content': message})

    try:
        with anthropic.Anthropic(api_key=api_key, timeout=30.0, max_retries=0) as client:
            result = client.messages.create(
                model=model,
                max_tokens=300,
                system=build_npc_prompt(npc),
                messages=messages,
            )
    except anthropic.APITimeoutError:
        raise AITimeout() from None
    except anthropic.APIResponseValidationError:
        raise AIInvalidResponse() from None
    except anthropic.APIError:
        raise AIUnavailable() from None

    # A token-limited response can contain text but still end mid-sentence.
    if getattr(result, 'stop_reason', None) == 'max_tokens':
        raise AIInvalidResponse()

    content = getattr(result, 'content', None)
    if not isinstance(content, list):
        raise AIInvalidResponse()
    text_blocks = []
    for block in content:
        if getattr(block, 'type', None) == 'text':
            text = getattr(block, 'text', None)
            if not isinstance(text, str):
                raise AIInvalidResponse()
            text_blocks.append(text)
    reply = '\n'.join(text_blocks).strip()
    if not reply or len(reply) > 4000:
        raise AIInvalidResponse()
    return reply
