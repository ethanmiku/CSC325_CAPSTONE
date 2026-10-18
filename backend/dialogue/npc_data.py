"""Temporary story content for the MVP; replace when the team finalizes the case."""

from dataclasses import dataclass

from rest_framework.exceptions import NotFound


@dataclass(frozen=True)
class NPCProfile:
    id: str
    name: str
    personality: str
    background: str
    known_facts: tuple[str, ...]


NPC_PROFILES = {
    'butler': NPCProfile(
        id='butler',
        name='Arthur',
        personality='Formal, reserved, and careful with his words.',
        background='The butler who manages the household at the manor.',
        known_facts=(
            'You were preparing dinner in the kitchen last night.',
            'You heard a loud noise from the hallway while preparing dinner.',
            'You did not see who caused the noise.',
        ),
    ),
}


class NPCNotFound(NotFound):
    default_detail = 'The requested NPC does not exist.'
    default_code = 'npc_not_found'


def get_npc(npc_id):
    try:
        return NPC_PROFILES[npc_id]
    except KeyError:
        raise NPCNotFound() from None
