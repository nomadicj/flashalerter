import logging
import json
import requests


class Session:
    """
    """
    access_token = None

    def __init__(self):
        """
        """
        pass

    @classmethod
    def authenticate(cls, username: str, password: str) -> bool:
        ''' get flashfood auth token'''
        logging.debug('Getting flash auth token for user %s.', username)

        headers = {
            'Content-Type': 'application/json',
        }

        payload = json.load(open('src/flash_food/payload.json'))
        payload['username'] = username
        payload['password'] = password

        response = requests.post(
                'https://identity.flashfood.com/oauth/token',
                headers=headers,
                data=json.dumps(payload),
                timeout=(5, None)
                )

        if response.status_code == 200:
            logging.info('FlashFood api auth successful')
            response_json = response.json()
            cls.access_token = response_json['access_token']
            logging.debug('FlashFood api auth access code; [%s]', cls.access_token)
            return True

        logging.error('FlashFood api auth failed. Response code; [%s]', response.status_code)
        return False
