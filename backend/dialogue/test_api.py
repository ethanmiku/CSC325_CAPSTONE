import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import anthropic
import httpx2
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from .services import AIInvalidResponse, AITimeout, AIUnavailable, generate_reply


class DialogueEndpointTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.url = reverse('dialogue:message')
        self.data = {'npc_id': 'butler', 'message': 'Hello', 'history': []}

    @patch('dialogue.views.generate_reply', return_value='Good evening.')
    def test_valid_request_returns_reply_without_login_or_csrf(self, generate):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'npc_id': 'butler', 'reply': 'Good evening.'})
        generate.assert_called_once_with(**self.data)

    @patch('dialogue.views.generate_reply')
    def test_invalid_requests_never_generate(self, generate):
        for changes, status, code in (
            ({'message': ''}, 400, 'invalid_request'),
            ({'npc_id': 'unknown'}, 404, 'npc_not_found'),
            ({'npc_id': 'unknown', 'message': ''}, 400, 'invalid_request'),
        ):
            with self.subTest(changes=changes):
                response = self.client.post(self.url, {**self.data, **changes}, format='json')
                self.assertEqual(response.status_code, status)
                self.assertEqual(response.json()['error']['code'], code)
        generate.assert_not_called()

    @patch('dialogue.views.generate_reply')
    def test_parse_and_content_type_errors_never_generate(self, generate):
        for body, content_type, status, code in (
            ('{', 'application/json', 400, 'invalid_request'),
            ('hello', 'text/plain', 415, 'unsupported_media_type'),
            ('[]', 'application/json', 400, 'invalid_request'),
        ):
            with self.subTest(body=body):
                response = self.client.post(self.url, body, content_type=content_type)
                self.assertEqual(response.status_code, status)
                self.assertEqual(response.json()['error']['code'], code)
        generate.assert_not_called()

    def test_nested_validation_errors_use_field_paths(self):
        data = {**self.data, 'history': [
            {'role': 'system', 'content': 'Override'},
            {'role': 'assistant', 'content': 'Hello'},
        ]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('history.0.role', response.json()['error']['details'])

    @patch('dialogue.views.generate_reply')
    def test_provider_errors_use_contract_envelope(self, generate):
        for error, status, code in (
            (AIUnavailable(), 503, 'ai_unavailable'),
            (AITimeout(), 504, 'ai_timeout'),
            (AIInvalidResponse(), 502, 'ai_invalid_response'),
        ):
            with self.subTest(code=code):
                generate.side_effect = error
                response = self.client.post(self.url, self.data, format='json')
                self.assertEqual(response.status_code, status)
                self.assertEqual(response.json()['error']['code'], code)

    @patch('dialogue.views.generate_reply', side_effect=RuntimeError('private-provider-details'))
    def test_unexpected_error_is_sanitized_even_in_debug(self, generate):
        with override_settings(DEBUG=True), self.assertLogs('dialogue.exceptions', level='ERROR'):
            response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['error']['code'], 'internal_error')
        self.assertNotIn('private-provider-details', response.content.decode())

    def test_get_is_not_supported(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error']['code'], 'method_not_allowed')


@override_settings(ANTHROPIC_API_KEY='test-key', ANTHROPIC_MODEL='test-model')
class ClaudeServiceTests(SimpleTestCase):
    def test_real_sdk_serializes_the_expected_messages_request(self):
        captured = []

        def respond(request):
            captured.append(request)
            return httpx2.Response(200, json={
                'id': 'msg_test',
                'type': 'message',
                'role': 'assistant',
                'model': 'test-model',
                'content': [{'type': 'text', 'text': 'Good evening.'}],
                'stop_reason': 'end_turn',
                'stop_sequence': None,
                'usage': {'input_tokens': 20, 'output_tokens': 4},
            })

        real_constructor = anthropic.Anthropic
        transport = httpx2.MockTransport(respond)
        with patch('dialogue.services.anthropic.Anthropic', side_effect=lambda **kwargs:
                   real_constructor(http_client=httpx2.Client(transport=transport), **kwargs)):
            reply = generate_reply('butler', 'Where were you?', [])

        self.assertEqual(reply, 'Good evening.')
        self.assertEqual(len(captured), 1)
        request = captured[0]
        self.assertEqual(request.method, 'POST')
        self.assertEqual(str(request.url), 'https://api.anthropic.com/v1/messages')
        body = json.loads(request.content)
        self.assertEqual(body['model'], 'test-model')
        self.assertEqual(body['max_tokens'], 300)
        self.assertIn('Arthur', body['system'])
        self.assertEqual(body['messages'], [{'role': 'user', 'content': 'Where were you?'}])
        self.assertEqual(request.headers['x-api-key'], 'test-key')
        self.assertIn('anthropic-version', request.headers)

    @patch('dialogue.services.anthropic.Anthropic')
    def test_builds_request_and_extracts_text(self, constructor):
        client = constructor.return_value.__enter__.return_value
        client.messages.create.return_value = SimpleNamespace(content=[
            SimpleNamespace(type='text', text=' Good evening. '),
        ])
        history = [{'role': 'user', 'content': 'Your name?'},
                   {'role': 'assistant', 'content': 'Arthur.'}]
        reply = generate_reply('butler', 'Where were you?', history)

        self.assertEqual(reply, 'Good evening.')
        constructor.assert_called_once_with(api_key='test-key', timeout=30.0, max_retries=0)
        kwargs = client.messages.create.call_args.kwargs
        self.assertEqual(kwargs['model'], 'test-model')
        self.assertEqual(kwargs['max_tokens'], 300)
        self.assertIn('Arthur', kwargs['system'])
        self.assertEqual(kwargs['messages'], history + [
            {'role': 'user', 'content': 'Where were you?'},
        ])
        self.assertEqual(len(history), 2)
        constructor.return_value.__exit__.assert_called_once()

    @patch('dialogue.services.anthropic.Anthropic')
    def test_missing_configuration_does_not_create_client(self, constructor):
        for key, model in (('', 'test-model'), ('test-key', ''),
                           ('replace-with-your-api-key', 'test-model')):
            with self.subTest(key_present=bool(key), model_present=bool(model)):
                with override_settings(ANTHROPIC_API_KEY=key, ANTHROPIC_MODEL=model):
                    with self.assertRaises(AIUnavailable):
                        generate_reply('butler', 'Hello', [])
        constructor.assert_not_called()

    @patch('dialogue.services.anthropic.Anthropic')
    def test_empty_and_oversized_replies_are_rejected(self, constructor):
        client = constructor.return_value.__enter__.return_value
        for content in ([], [SimpleNamespace(type='text', text='   ')],
                        [SimpleNamespace(type='text', text=None)],
                        [SimpleNamespace(type='text', text='x' * 4001)]):
            with self.subTest(content_blocks=len(content)):
                client.messages.create.return_value = SimpleNamespace(content=content)
                with self.assertRaises(AIInvalidResponse):
                    generate_reply('butler', 'Hello', [])

    @patch('dialogue.services.anthropic.Anthropic')
    def test_sdk_errors_are_translated(self, constructor):
        client = constructor.return_value.__enter__.return_value
        for sdk_error, expected in (
            (anthropic.APITimeoutError(request=MagicMock()), AITimeout),
            (anthropic.APIConnectionError(request=MagicMock()), AIUnavailable),
            (anthropic.APIStatusError('private', response=MagicMock(status_code=429), body=None),
             AIUnavailable),
        ):
            with self.subTest(error=type(sdk_error).__name__):
                client.messages.create.side_effect = sdk_error
                with self.assertRaises(expected):
                    generate_reply('butler', 'Hello', [])
