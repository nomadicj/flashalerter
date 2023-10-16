"""
FlashFood Item
"""
import logging
import shutil
import os
from dataclasses import dataclass
import requests


@dataclass
class Item:
    """
    FlashFood Item Object

    Provides 'image' and 'discounted_percentage' properties
    in addition to standard properties created at initialization
    """
    id: str
    available_qty: int
    original_price: float
    discounted_price: float
    image_gallery: str
    image_url: str
    is_snap_eligible: bool
    name_en: str
    name_fr: str
    sale_over_datetime: str
    same_day_sale: bool
    upc: str
    store_id: str
    best_before_date: str
    intime: str

    @property
    def image(self) -> str:
        ''' Returns path to image for item '''
        item_image = f'images/{self.id}.jpg'
        response = requests.get(
            self.image_url,
            stream=True,
            timeout=(5, None)
            )

        if response.status_code == 200:
            if not os.path.exists('images'):
                os.makedirs('images')
            with open(item_image, 'wb') as image_file:
                shutil.copyfileobj(response.raw, image_file)
            logging.info('Image successfully Downloaded: %s', {item_image})
        else:
            logging.error('Image Couldn\'t be retrieved')
            item_image = 'images/no-image-available.png'

        return item_image

    @property
    def discounted_percentage(self) -> int:
        """ Returns discounted price / original price """
        return self.discounted_price // self.original_price
