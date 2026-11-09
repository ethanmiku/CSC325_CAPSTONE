from django.core.management.base import BaseCommand

from dialogue.models import NPCProfile


# Provisional story content until the team finalizes the case.
SEED_PROFILES = {
    'butler': {
        'name': 'Arthur',
        'personality': 'Formal, reserved, and careful with his words.',
        'background': 'The butler who manages the household at the manor.',
        'known_facts': [
            'You were preparing dinner in the kitchen last night.',
            'You heard a loud noise from the hallway while preparing dinner.',
            'You did not see who caused the noise.',
        ],
    },
    'clara_blackwood': {
        'name': 'Clara Blackwood',
        'personality': 'Direct, observant, and impatient with evasive questions.',
        'background': "Edmund Blackwood's daughter.",
        'known_facts': [
            'You were reading in the library when you heard the hallway noise.',
            'You heard hurried footsteps pass the library shortly after the noise.',
            'You could not identify who passed the library.',
        ],
    },
}


class Command(BaseCommand):
    help = 'Create the default dialogue profiles that are missing from MongoDB.'

    def handle(self, *args, **options):
        for npc_id, profile in SEED_PROFILES.items():
            _, created = NPCProfile.objects.get_or_create(npc_id=npc_id, defaults=profile)
            self.stdout.write(f'{"Created" if created else "Already exists"}: {npc_id}')
