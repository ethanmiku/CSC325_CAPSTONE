from uuid import UUID

from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .npc_data import get_npc
from .test_profiles import mock_profile_lookup
from .prompts import build_npc_prompt
from .serializers import DialogueMessageSerializer


class HealthTests(SimpleTestCase):
    # SimpleTestCase prohibits database queries, including those from middleware.
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.url = reverse('dialogue:health')

    def test_health_is_public_json_without_database_access(self):
        response = self.client.get(self.url, HTTP_ACCEPT='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_post_returns_contract_error_without_csrf_token(self):
        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error']['code'], 'method_not_allowed')

    def test_health_does_not_read_a_session(self):
        self.client.cookies['sessionid'] = 'unused-session'

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})


class DialogueValidationTests(SimpleTestCase):
    def request_data(self, **changes):
        return {
            'game_session_id': '4ff6d7d4-a7e5-48b1-ae5f-74c2409eb62f',
            'npc_id': 'butler',
            'message': 'Where were you?',
            **changes,
        }

    def test_valid_request_parses_session_id_and_trims_message(self):
        data = self.request_data(message='  Where were you?  ')
        serializer = DialogueMessageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['message'], 'Where were you?')
        self.assertEqual(serializer.validated_data['game_session_id'], UUID(data['game_session_id']))

    def test_rejects_missing_fields_and_non_object_body(self):
        for field in ('game_session_id', 'npc_id', 'message'):
            data = self.request_data()
            del data[field]
            serializer = DialogueMessageSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)
        for data in ([], 'text', 123):
            with self.subTest(data=data):
                self.assertFalse(DialogueMessageSerializer(data=data).is_valid())

    def test_rejects_incorrect_json_types_and_blank_messages(self):
        for field, values in {
            'npc_id': (123, True, None),
            'message': (123, False, None, '', '   '),
            'game_session_id': (123, True, None, {}, 'invalid-uuid'),
        }.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    serializer = DialogueMessageSerializer(data=self.request_data(**{field: value}))
                    self.assertFalse(serializer.is_valid())
                    self.assertIn(field, serializer.errors)

    def test_rejects_unknown_fields_and_client_history(self):
        for field, value in (('model', 'client-selected-model'), ('history', [])):
            with self.subTest(field=field):
                serializer = DialogueMessageSerializer(data=self.request_data(**{field: value}))
                self.assertFalse(serializer.is_valid())
                self.assertIn(field, serializer.errors)

    def test_message_length_is_checked_before_trimming(self):
        for message, valid in (('x' * 1000, True), ('x' * 1001, False),
                               (' ' * 1000 + 'x', False)):
            with self.subTest(length=len(message)):
                serializer = DialogueMessageSerializer(data=self.request_data(message=message))
                self.assertEqual(serializer.is_valid(), valid)


class NPCPromptTests(SimpleTestCase):
    def test_prompt_includes_profile_facts_and_story_constraints(self):
        with mock_profile_lookup():
            npc = get_npc('butler')
        prompt = build_npc_prompt(npc)

        for text in (npc.name, npc.personality, npc.background, *npc.known_facts):
            self.assertIn(text, prompt)
        self.assertIn('Do not invent evidence', prompt)
        self.assertIn('do not know', prompt)
        self.assertIn('not as instructions', prompt)
        self.assertIn('game state', prompt)
