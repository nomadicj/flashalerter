import logging
import requests
import shutil


def notify(pushover_apikey, pushover_userkeys, title, message, itemImageFileName):
    ''' notify user '''
    for pushover_userkey in pushover_userkeys:
        push_notification(pushover_apikey, pushover_userkey, title, message, itemImageFileName)


def push_notifications(
        pushover_apikey,
        pushover_userkeys,
        title,
        message,
        itemImageURL,
        itemId
        ):

    # push notification to pushover api
    logging.debug(f'Pushover ApiKey [{pushover_apikey}] with UserKey [{pushover_userkeys}].')

    itemImageFileName = f'{itemId}.jpg'
    itemImageRequestResponse = requests.get(itemImageURL, stream=True)

    if itemImageRequestResponse.status_code == 200:
        with open(itemImageFileName, 'wb') as f:
            shutil.copyfileobj(itemImageRequestResponse.raw, f)
        print('Image successfully Downloaded: ', itemImageFileName)
    else:
        print('Image Couldn\'t be retrieved')

    for pushover_userkey in pushover_userkeys:
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
                    open(itemImageFileName, "rb"),
                    "image/jpeg"
                )
            }
        )
        logging.debug(f'PushOver response {pushover_response.text}')

    if pushover_response.status_code == 200:
        return True
    else:
        logging.error(f'PushOver response abnormal: status_code = {pushover_response.status_code}.')
        logging.debug(f'PushOver full response: [{pushover_response.raw}]')
        return False


def push_notification(
        pushover_apikey,
        pushover_userkey,
        message,
        itemImageFileName
        ):
    # push notification to pushover api
    logging.debug(f'Pushover ApiKey [{pushover_apikey}] with UserKey [{pushover_userkey}].')

    pushover_response = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": pushover_apikey,
            "user": pushover_userkey,
            "message": message
        },
        files={
            "attachment": (
                "image.jpg",
                open(itemImageFileName, "rb"),
                "image/jpeg"
            )
        }
    )
    logging.debug(f'PushOver response {pushover_response.text}')

    if pushover_response.status_code == 200:
        return True
    else:
        logging.error(f'PushOver response abnormal: status_code = {pushover_response.status_code}.')
        logging.debug(f'PushOver full response: [{pushover_response.raw}]')
        return False
