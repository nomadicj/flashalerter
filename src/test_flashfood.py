import unittest
import flash_food


class TestFlashFood(unittest.TestCase):

    def test_get_items(self):
        dict = flash_food.get_items()
        self.assertDictContainsSubset(dict)


if __name__ == '__main__':
    unittest.main()
