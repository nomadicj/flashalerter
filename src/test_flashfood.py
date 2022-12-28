import unittest
import flashFood


class TestFlashFood(unittest.TestCase):

    def test_get_items(self):
        dict = flashFood.get_items()
        self.assertDictContainsSubset(dict)


if __name__ == '__main__':
    unittest.main()
