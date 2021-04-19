from unittest import TestCase
from unittest.mock import MagicMock, patch

from bot import hit_zone
from test.mocks import MockAuthor, MockMessage


def create_response(content):
    res = hit_zone.create_response(MockMessage(MockAuthor("TestUser"), content))
    return res.messages[0]["args"][0]


class TestDiceRoll(TestCase):
    def test_parse_with_d_or_w(self):
        self.assertIsNotNone(hit_zone.parse("hz klein humanoid"))
        self.assertIsNotNone(hit_zone.parse("hitzone small mensch"))
        self.assertIsNotNone(hit_zone.parse("hz medium wesen"))
        self.assertIsNotNone(hit_zone.parse("hitzone groß kreatur"))
        self.assertIsNotNone(hit_zone.parse("hz riesig non-humanoid"))

    @patch("random.randint", new_callable=MagicMock())
    def test_response(self, mock_randint: MagicMock):
        mock_randint.return_value = 5
        self.assertEqual(
            create_response("hz klein humanoid"),
            "@TestUser - Ergebnis: 5\n"
            "Humanoid (klein): Kopf getroffen\n"
            "Wundeffekt ab KO/2 Schadenspunkte: Eine Stufe Betäubung",
        )
        self.assertEqual(
            create_response("hz mittel humanoid"),
            "@TestUser - Ergebnis: 5\n"
            "Humanoid (mittel): Torso getroffen\n"
            "Wundeffekt ab KO/2 Schadenspunkte: Zusätzlich 1W3+1 SP",
        )
        self.assertEqual(
            create_response("hz groß humanoid"),
            "@TestUser - Ergebnis: 5\n"
            "Humanoid (groß): Torso getroffen\n"
            "Wundeffekt ab KO/2 Schadenspunkte: Zusätzlich 1W3+1 SP",
        )
        self.assertEqual(
            create_response("hz klein non-humanoid"),
            "@TestUser - Ergebnis: 5\nNon-Humanoid (klein): Torso getroffen",
        )
        self.assertEqual(
            create_response("hz mittel non-human"),
            "@TestUser - Ergebnis: 5\nNon-Humanoid (mittel): Torso getroffen",
        )
        self.assertEqual(
            create_response("hz groß wesen"),
            "@TestUser - Ergebnis: 5\n"
            "Non-Humanoid, vierbeinig (groß): Kopf getroffen\n"
            "Non-Humanoid, sechs Gliedmaßen (groß): Torso getroffen",
        )
        self.assertEqual(
            create_response("hz riesig kreatur"),
            "@TestUser - Ergebnis: 5\nNon-Humanoid (riesig): Torso getroffen",
        )
