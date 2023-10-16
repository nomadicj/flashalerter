"""
FlashFood Store
"""
import requests

from flash_food.item import Item
from flash_food.session import Session

from dataclasses import dataclass


@dataclass
class Store:
    """
    FlashFood Store Object

    Provides 'get_items' method in addition to standard properties created at initialization
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
                    id=item['_id'],
                    available_qty=item['available_qty'],
                    original_price=item['original_price'],
                    discounted_price=item['discounted_price'],
                    image_gallery=item['image_gallery'],
                    image_url=item['image_url'],
                    is_snap_eligible=item['is_snap_eligible'],
                    name_en=item['name_en'],
                    name_fr=item['name_fr'],
                    sale_over_datetime=item['sale_over_datetime'],
                    same_day_sale=item['same_day_sale'],
                    upc=item['upc'],
                    store_id=item['store_id'],
                    best_before_date=item['best_before_date'],
                    intime=item['intime']
                    )
                )

        return items
