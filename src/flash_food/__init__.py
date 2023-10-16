"""
FlashFood module

Provides session, store and item objects
"""
import logging
import json

import requests

from flash_food.store import Store
from flash_food.session import Session


class Api:
    """
    FlashFood API Object

    Provides initialization for API access and get_nearest_stores
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password
        logging.info('Initializing FlashFood api')

        self.session = Session()
        self.session.authenticate(username=username, password=password)

    def get_nearest_stores(self, lat, long, distance):
        ''' get store nearest to location '''
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {Session.access_token}'
        }

        params = {
            'food_images': '1',
            'latitude': lat,
            'longitude': long,
            'distance': distance,
            'show_all': '1'
        }

        response = requests.get(
            'https://api.flashfood.com/api/v1/store/list',
            params=params,
            headers=headers,
            timeout=(5, None)
        )

        nearest_stores = json.loads(response.text)
        stores = []

        for store in nearest_stores['success']:
            logging.debug('Store data: %s', store)
            store_object = Store(id=store['_id'], name=store['name'])
            stores.append(store_object)

        return stores
