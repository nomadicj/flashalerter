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
    else:
        logging.error(f'FlashFood api auth failed. Response code; [{response.status_code}]')
        return False


def get_nearestStore(lat, long, access_token):
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


def get_items(storeId, access_token):
    ''' get store items '''
    headers = {
        'accept': '*/*',
        'Authorization': f'Bearer {access_token}',
    }

    params = {
        'store_id': storeId,
    }

    available_items = requests.get(
        'https://api.flashfood.com/api/v1/item/list',
        params=params,
        headers=headers,
    )

    return available_items.text


def get_store


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
