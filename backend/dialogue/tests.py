from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework.test import APIClient


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
