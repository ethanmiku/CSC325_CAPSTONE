"""Persistence for completed NPC dialogue exchanges."""

from .models import DialogueExchange


def save_exchange(*, game_session_id, npc_id, player_message, npc_reply):
    return DialogueExchange.objects.create(
        game_session_id=game_session_id,
        npc_id=npc_id,
        player_message=player_message,
        npc_reply=npc_reply,
    )


def get_recent_exchanges(*, game_session_id, npc_id, limit=10):
    """Return the newest exchanges for one session and NPC, oldest first."""
    newest_first = DialogueExchange.objects.filter(
        game_session_id=game_session_id,
        npc_id=npc_id,
    ).order_by('-created_at', '-id')[:limit]
    exchanges = list(newest_first)
    exchanges.reverse()
    return exchanges
