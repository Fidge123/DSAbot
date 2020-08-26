from unittest import TestCase

from bot import wiki


class TestWiki(TestCase):
    def test_find(self):
        results = wiki.find("igni")

        self.assertEqual(results[0]["title"], "Ignifaxius")
        self.assertEqual(
            results[0]["url"],
            "http://ulisses-regelwiki.de/index.php/ZS_Ignifaxius.html",
        )
        self.assertEqual(results[1]["title"], "Ignisphaero")
        self.assertEqual(
            results[1]["url"],
            "http://ulisses-regelwiki.de/index.php/ZS_Ignisphaero.html",
        )

        results = wiki.find("ignifaxius")

        self.assertEqual(results[0]["title"], "Ignifaxius")
        self.assertEqual(results[0]["score"], 1.0)

        results = wiki.find("Wuchtschlag")

        self.assertEqual(results[0]["title"], "Wuchtschlag I-III")
        self.assertEqual(results[0]["score"], 1.0)
