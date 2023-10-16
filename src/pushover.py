"""
Pushover Module

Created to interact with Pushover API
Enables push notification capability
"""
import logging
import requests


def notify(pushover_apikey: str, pushover_userkeys: list, title: str, message: str, item_image_file_name: str) -> bool:
    ''' notify user '''
    for pushover_userkey in pushover_userkeys:
        # push notification to pushover api
        logging.debug('Pushover ApiKey [%s] with UserKey [%s].', pushover_apikey, pushover_userkey)

        pushover_response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": pushover_apikey,
                "user": pushover_userkey,
                "title": title,
                "message": message
            },
            files={
                "attachment": (
                    "image.jpg",
                    open(item_image_file_name, "rb"),
                    "image/jpeg"
                )
            },
            timeout=(5, None)
        )
        logging.debug('PushOver response %s', pushover_response.text)

        if pushover_response.status_code == 200:
            return True

        logging.error('PushOver response abnormal: status_code = %s.', pushover_response.status_code)
        logging.debug('PushOver full response: [%s]', pushover_response.raw)
        return False
