import requests

from flash_food.item import Item
from flash_food.session import Session

from dataclasses import dataclass


@dataclass
class Store:
    """
    """
    id: str
    name: str

    def get_items(self) -> list:
        ''' get store items '''
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {Session.access_token}',
        }

        params = {
            'store_id': self.id,
        }

        available_items = requests.get(
            'https://api.flashfood.com/api/v1/item/list',
            params=params,
            headers=headers,
            timeout=(5, None)
        )

        items = []

        for item in available_items.json()['success']['items']:
            items.append(
                Item(
                    item['_id'],
                    item['available_qty'],
                    item['original_price'],
                    item['discounted_price'],
                    item['image_gallery'],
                    item['image_url'],
                    item['is_snap_eligible'],
                    item['name_en'],
                    item['name_fr'],
                    item['sale_over_datetime'],
                    item['same_day_sale'],
                    item['upc'],
                    item['store_id'],
                    item['best_before_date'],
                    item['intime']
                    )
                )     

        return items
