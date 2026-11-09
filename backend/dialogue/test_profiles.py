import os
from io import StringIO
from unittest import skipUnless
from unittest.mock import patch

from django.core.management import call_command
from django.test import TransactionTestCase

from .management.commands.seed_npc_profiles import SEED_PROFILES
from .models import NPCProfile
from .npc_data import NPCNotFound, get_npc


def mock_profile_lookup():
    def lookup(*, npc_id):
        try:
            profile = SEED_PROFILES[npc_id]
        except KeyError:
            raise NPCProfile.DoesNotExist() from None
        return NPCProfile(npc_id=npc_id, **profile)

    return patch('dialogue.npc_data.NPCProfile.objects.get', side_effect=lookup)


RUN_MONGODB_TESTS = os.environ.get('RUN_MONGODB_TESTS') == '1'


@skipUnless(RUN_MONGODB_TESTS, 'Requires a dedicated local MongoDB test server')
class MongoDBProfileTests(TransactionTestCase):
    databases = {'default'} if RUN_MONGODB_TESTS else set()

    def test_seed_and_lookup_profiles(self):
        output = StringIO()
        call_command('seed_npc_profiles', stdout=output)
        call_command('seed_npc_profiles', stdout=output)

        self.assertEqual(NPCProfile.objects.count(), len(SEED_PROFILES))
        for npc_id, expected in SEED_PROFILES.items():
            with self.subTest(npc_id=npc_id):
                profile = get_npc(npc_id)
                for field, value in expected.items():
                    self.assertEqual(getattr(profile, field), value)

        for npc_id in ('unknown', 'Butler', ' butler '):
            with self.subTest(npc_id=npc_id), self.assertRaises(NPCNotFound):
                get_npc(npc_id)
