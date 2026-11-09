"""Retrieve the server-owned profile for a dialogue request."""

from rest_framework.exceptions import NotFound

from .models import NPCProfile


class NPCNotFound(NotFound):
    default_detail = 'The requested NPC does not exist.'
    default_code = 'npc_not_found'


def get_npc(npc_id):
    try:
        return NPCProfile.objects.get(npc_id=npc_id)
    except NPCProfile.DoesNotExist:
        raise NPCNotFound() from None
