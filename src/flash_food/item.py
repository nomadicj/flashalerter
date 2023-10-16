import logging
import requests
import shutil

from dataclasses import dataclass


@dataclass
class Item:
    """
    """
    _id: str
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
    def image(self):
        ''' get image for notification '''
        itemImage = f'{self._id}.jpg'
        itemImageRequestResponse = requests.get(
                                            self.image_url,
                                            stream=True,
                                            timeout=(5, None)
                                            )

        if itemImageRequestResponse.status_code == 200:
            with open(itemImage, 'wb') as imageFile:
                shutil.copyfileobj(itemImageRequestResponse.raw, imageFile)
            logging.info('Image successfully Downloaded: %s', {itemImage})
            return itemImage
        else:
            logging.error('Image Couldn\'t be retrieved')
            return 'no-image-available.png'

    @property
    def discounted_percentage(self):
        return self.discounted_price // self.original_price