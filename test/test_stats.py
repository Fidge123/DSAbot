from unittest import TestCase
from bot import stats
from mocks import MockAuthor


class TestDiceRoll(TestCase):
    def test_save_roll(self):
        self.assertIsInstance(
            stats.save_check(MockAuthor("TestUser"), "SkillCheck", [1, 1, 1], 20),
            stats.Statistic,
        )

    def test_show_statistics(self):
        result = stats.get_statistics(MockAuthor("TestUser"))
        self.assertIsInstance(result, str)
        self.assertNotEqual(
            result,
            "@TestUser Keine Würfelergebnisse gespeichert.",
        )
