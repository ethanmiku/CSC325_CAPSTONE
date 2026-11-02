from django.test import SimpleTestCase
from django.urls import reverse


class ClueAPITests(SimpleTestCase):

    def test_get_clues(self):
        response = self.client.get(reverse("get_clues"))

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data["clues"]), 2)
        self.assertEqual(data["clues"][0]["name"], "Bloody Knife")