''' FlashFood module '''
import logging
import requests
import json
import shutil


def get_flash_auth_token(username, password):
    ''' get flashfood auth token'''
    logging.debug(f'Getting flash auth token for user {username}.')
    headers = {
        'Content-Type': 'application/json',
    }

    payload = json.load(open('payload.json'))
    payload['username'] = username
    payload['password'] = password

    response = requests.post(
        'https://identity.flashfood.com/oauth/token',
        headers=headers,
        data=json.dumps(payload)
        )

    if response.status_code == 200:
        logging.info('FlashFood api auth successful')
        response_json = json.loads(response.text)
        access_token = response_json['access_token']
        logging.debug(f'FlashFood api auth access code; [{access_token}]')
        return access_token
        
    logging.error(f'FlashFood api auth failed. Response code; [{response.status_code}]')
    return False


def get_nearest_store(lat, long, access_token):
    ''' get store nearest to location '''
    headers = {
        'accept': '*/*',
        'Authorization': f'Bearer {access_token}',
    }

    params = {
        # 'latitude': lat,
        'latitude': '49.283764',
        # 'longitude': long,
        'longitude': '-122.793205',
    }

    nearest_store = requests.get(
        'https://api.flashfood.com/api/v1/store/nearest',
        params=params,
        headers=headers,
    )

    return nearest_store


def get_items(store_id: str, access_token: str):
    ''' get store items '''
    headers = {
        'accept': '*/*',
        'Authorization': f'Bearer {access_token}',
    }

    params = {
        'store_id': store_id,
    }

    available_items = requests.get(
        'https://api.flashfood.com/api/v1/item/list',
        params=params,
        headers=headers,
    )

    return available_items.text


def get_nearest_stores(lat, long, distance, access_token):
    ''' get store nearest to location '''
    headers = {
        'accept': '*/*',
        'Authorization': f'Bearer {access_token}'
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
    )

    nearest_stores = json.loads(response.text)
    stores = []

    for store in nearest_stores['success']:
        logging.debug(f'Store data: {store}')
        stores.append({'id': store['_id'], 'name': store['name']})

    return stores


def get_image(itemImageURL, itemId):
    ''' get image for notification '''
    itemImage = f'{itemId}.jpg'
    itemImageRequestResponse = requests.get(itemImageURL, stream=True)

    if itemImageRequestResponse.status_code == 200:
        with open(itemImage, 'wb') as imageFile:
            shutil.copyfileobj(itemImageRequestResponse.raw, imageFile)
        logging.info(f'Image successfully Downloaded: {itemImage}')
        return itemImage
    else:
        logging.error('Image Couldn\'t be retrieved')
        return 'no-image-available.png'
