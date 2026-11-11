"""Persistence for completed NPC dialogue exchanges."""

from .models import DialogueExchange


MAX_HISTORY_CHARS = 20_000


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


def get_history_messages(*, game_session_id, npc_id):
    """Format the most recent complete exchanges within the Claude history budget."""
    exchanges = get_recent_exchanges(game_session_id=game_session_id, npc_id=npc_id)
    messages = []
    remaining_chars = MAX_HISTORY_CHARS
    for exchange in reversed(exchanges):
        size = len(exchange.player_message) + len(exchange.npc_reply)
        if size > remaining_chars:
            break
        remaining_chars -= size
        messages.extend([
            {'role': 'assistant', 'content': exchange.npc_reply},
            {'role': 'user', 'content': exchange.player_message},
        ])
    messages.reverse()
    return messages
