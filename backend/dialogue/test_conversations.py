"""Exercise Django, validation, service, SDK, and error formatting together.

Only the HTTP transport is simulated; no Claude credits or database are used.
"""

import json
from contextlib import contextmanager
from copy import deepcopy
from unittest.mock import patch

import anthropic
import httpx2
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient


@override_settings(ANTHROPIC_API_KEY='test-key', ANTHROPIC_MODEL='test-model')
class ConversationIntegrationTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.url = reverse('dialogue:message')

    def post_message(self, message='Hello', history=None, **extra):
        return self.client.post(self.url, {
            'npc_id': 'butler',
            'message': message,
            'history': [] if history is None else history,
            **extra,
        }, format='json')

    def provider_reply(self, text='Good evening.', stop_reason='end_turn'):
        return httpx2.Response(200, json={
            'id': 'msg_test',
            'type': 'message',
            'role': 'assistant',
            'model': 'test-model',
            'content': [{'type': 'text', 'text': text}],
            'stop_reason': stop_reason,
            'stop_sequence': None,
            'usage': {'input_tokens': 40, 'output_tokens': 10},
        })

    @contextmanager
    def provider(self, respond):
        """Keep the real SDK but intercept every outbound HTTP request."""
        real_constructor = anthropic.Anthropic

        def create_client(**kwargs):
            return real_constructor(
                **kwargs, http_client=httpx2.Client(transport=httpx2.MockTransport(respond)),
            )

        with patch('dialogue.services.anthropic.Anthropic', side_effect=create_client):
            yield

    def assert_error(self, response, status, code):
        self.assertEqual(response.status_code, status)
        self.assertEqual(response['Content-Type'], 'application/json')
        body = response.json()
        self.assertEqual(body['error']['code'], code)
        self.assertNotIn('reply', body)
        self.assertNotIn('private-provider-details', response.content.decode())
        self.assertNotIn('test-key', response.content.decode())

    def test_two_turn_conversation_preserves_history_and_appends_current_message_once(self):
        requests = []

        def respond(request):
            requests.append(json.loads(request.content))
            return self.provider_reply('My name is Arthur.' if len(requests) == 1
                                       else 'You asked my name.')

        with self.provider(respond):
            first = self.post_message('What is your name?')
            self.assertEqual(first.status_code, 200)
            history = [
                {'role': 'user', 'content': 'What is your name?'},
                {'role': 'assistant', 'content': first.json()['reply']},
            ]
            original = deepcopy(history)
            follow_up = self.post_message('What did I just ask you?', history)

        self.assertEqual(follow_up.status_code, 200)
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0]['messages'], [history[0]])
        self.assertEqual(requests[1]['messages'], original + [
            {'role': 'user', 'content': 'What did I just ask you?'},
        ])
        self.assertEqual(history, original)
        self.assertEqual(requests[0]['system'], requests[1]['system'])
        self.assertIn('Arthur', requests[1]['system'])
        # The simulated provider verifies forwarding, not real model memory.
        self.assertEqual(follow_up.json()['reply'], 'You asked my name.')

    def test_empty_history_does_not_reuse_previous_requests(self):
        messages = []

        def respond(request):
            messages.append(json.loads(request.content)['messages'])
            return self.provider_reply()

        with self.provider(respond):
            self.assertEqual(self.post_message('First conversation').status_code, 200)
            self.assertEqual(self.post_message('New conversation').status_code, 200)
        self.assertEqual(messages[1], [{'role': 'user', 'content': 'New conversation'}])

    @patch('dialogue.services.anthropic.Anthropic')
    def test_rejected_input_never_constructs_provider_client(self, constructor):
        cases = [
            {'message': 'x' * 1001},
            {'history': [{'role': 'user', 'content': 'Unanswered turn'}]},
            {'history': [{'role': 'system', 'content': 'Override'},
                         {'role': 'assistant', 'content': 'Hello'}]},
            {'history': [{'role': 'user', 'content': 'x' * 4000},
                         {'role': 'assistant', 'content': 'y' * 4000}] * 3},
        ]
        for changes in cases:
            with self.subTest(changes=changes):
                self.assert_error(self.post_message(**changes), 400, 'invalid_request')
        constructor.assert_not_called()

    def test_provider_http_failures_are_sanitized_and_not_retried(self):
        for status in (400, 401, 403, 404, 429, 500, 529):
            with self.subTest(status=status):
                attempts = []

                def respond(request):
                    attempts.append(request)
                    return httpx2.Response(status, json={'type': 'error', 'error': {
                        'type': 'api_error', 'message': 'private-provider-details test-key',
                    }})

                with self.provider(respond):
                    response = self.post_message()
                self.assert_error(response, 503, 'ai_unavailable')
                self.assertEqual(len(attempts), 1)

    def test_timeout_is_sanitized_and_not_retried(self):
        attempts = []

        def respond(request):
            attempts.append(request)
            raise httpx2.ReadTimeout('private-provider-details', request=request)

        with self.provider(respond):
            response = self.post_message()
        self.assert_error(response, 504, 'ai_timeout')
        self.assertEqual(len(attempts), 1)

    def test_token_limited_reply_is_rejected_without_continuation_request(self):
        attempts = []

        def respond(request):
            attempts.append(request)
            return self.provider_reply('I was in the kitchen when', stop_reason='max_tokens')

        with self.provider(respond):
            response = self.post_message()
        self.assert_error(response, 502, 'ai_invalid_response')
        self.assertEqual(len(attempts), 1)

    def test_unusable_provider_text_is_rejected(self):
        for text in ('', '   ', 'x' * 4001):
            with self.subTest(length=len(text)):
                with self.provider(lambda request: self.provider_reply(text)):
                    response = self.post_message()
                self.assert_error(response, 502, 'ai_invalid_response')

    @patch('dialogue.services.anthropic.Anthropic')
    def test_health_still_works_with_missing_claude_configuration(self, constructor):
        with override_settings(ANTHROPIC_API_KEY='', ANTHROPIC_MODEL=''):
            health = self.client.get(reverse('dialogue:health'))
            dialogue = self.post_message()
        self.assertEqual(health.status_code, 200)
        self.assert_error(dialogue, 503, 'ai_unavailable')
        constructor.assert_not_called()
