from datetime import timedelta
from unittest import skipUnless
from uuid import uuid4

from django.test import TransactionTestCase
from django.utils import timezone

from .history import get_recent_exchanges, save_exchange
from .models import DialogueExchange
from .test_profiles import RUN_MONGODB_TESTS


@skipUnless(RUN_MONGODB_TESTS, 'Requires a dedicated local MongoDB test server')
class MongoDBConversationHistoryTests(TransactionTestCase):
    databases = {'default'} if RUN_MONGODB_TESTS else set()

    def setUp(self):
        self.session_id = uuid4()

    def save(self, message, *, npc_id='butler', session_id=None):
        return save_exchange(
            game_session_id=session_id or self.session_id,
            npc_id=npc_id,
            player_message=message,
            npc_reply='I was in the kitchen.',
        )

    def history(self, **kwargs):
        return get_recent_exchanges(
            game_session_id=self.session_id, npc_id='butler', **kwargs,
        )

    def test_stores_both_messages_under_the_session_and_npc(self):
        exchange = self.save('Where were you?')

        stored, = self.history()
        self.assertEqual(stored.pk, exchange.pk)
        self.assertEqual(stored.game_session_id, self.session_id)
        self.assertEqual(stored.npc_id, 'butler')
        self.assertEqual(stored.player_message, 'Where were you?')
        self.assertEqual(stored.npc_reply, 'I was in the kitchen.')

    def test_isolates_history_by_both_session_and_npc(self):
        expected = self.save('Where were you?')
        self.save('A different NPC', npc_id='clara_blackwood')
        self.save('A different session', session_id=uuid4())

        self.assertEqual(self.history(), [expected])
        self.assertEqual(get_recent_exchanges(
            game_session_id=self.session_id, npc_id='unknown',
        ), [])

    def test_limits_to_newest_exchanges_and_returns_them_oldest_first(self):
        first = self.save('First')
        second = self.save('Second')
        third = self.save('Third')
        # Give two exchanges the same timestamp and order the first by time.
        tied_at = timezone.now()
        DialogueExchange.objects.filter(pk__in=[second.pk, third.pk]).update(created_at=tied_at)
        DialogueExchange.objects.filter(pk=first.pk).update(created_at=tied_at - timedelta(seconds=1))

        self.assertEqual(self.history(), [first, second, third])
        self.assertEqual(self.history(limit=2), [second, third])
