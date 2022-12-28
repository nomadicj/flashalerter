import unittest
import pushover
from datetime import datetime

pushover_apikey = 'ajk7w8hogvf9gmhax9d3ptvp8sf4hg'
pushover_userkeys = 'ui7f2v4oug2f4pwpbwzy68asu3fwxy'
message = f'Test run at {datetime.now().replace(microsecond=0).isoformat()}'
itemImageURL = 'https://images.unsplash.com/photo-1574144611937-0df059b5ef3e'
itemId = '1'


class TestPushover(unittest.TestCase):

    def test_push_notification(self):
        dict = pushover.get_items(
            pushover_apikey,
            pushover_userkeys,
            message,
            itemImageURL,
            itemId)
        self.assertDictContainsSubset(response := dict)


if __name__ == '__main__':
    unittest.main()
