import os
import logging
import json
from datetime import datetime
import flash_food
import pushover
import db


# Set vars
flashfood_user = os.getenv('FLASHFOOD_USER')
flashfood_pass = os.getenv('FLASHFOOD_PASS')
flashfood_store_ids = os.getenv('FLASHFOOD_STORE_IDS').split(',')
pushover_apikey = os.getenv('PUSHOVER_APIKEY')
pushover_userkey = os.getenv('PUSHOVER_USERKEY')
pushover_userkeys = os.getenv('PUSHOVER_USERKEYS').split(',')
db_file = os.getenv('DB_FILE')
log_level = os.getenv('LOG_LEVEL', default='info').upper()
logging_filename = f'{datetime.now().replace(microsecond=0).isoformat()}.log'

# Setup logging
logging.basicConfig(
    filename='log/'+logging_filename,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=log_level
    )

# Init messaging
logging.warning('Flashalerter starting...')
logging.debug(f'User set to [{flashfood_user}].')
logging.debug(f'DB file set to [{db_file}].')
logging.info(f'Logging set to [{log_level}].')
logging.info(f'Total [{len(pushover_userkeys)}] users to be notified.')
logging.info(f'Total [{len(flashfood_store_ids)}] stores to be polled.')
logging.debug(f'StoreIDs; [{flashfood_store_ids}]')

print(f"Hello [{flashfood_user}].")


def init_db():
    ''' initialise db connection '''
    logging.info('Initialising db connection')

    # Create DB Connection
    conn = db.create_connection(db_file)
    # Create table, if required
    if conn is not None:
        # create items table
        db.create_table(conn)
    else:
        logging.error('Error! cannot create the database connection.')

    return conn


def init_flashfood_api(flashfood_user, flashfood_pass):
    ''' initialise flashfood api token '''
    logging.info('Initialising FlashFood api')
    access_token = flash_food.get_flash_auth_token(flashfood_user, flashfood_pass)

    return access_token


def main():

    access_token = init_flashfood_api(flashfood_user, flashfood_pass)

    if access_token is False:
        logging.critical('No access token returned. Exiting.')
        print('Critical error getting access token. Exiting.')
        exit(-1)

    lat: float = 49.2568
    long: float = -122.8255
    distance: int = 5

    nearest_stores = flash_food.get_nearest_stores(lat, long, distance, access_token)

    logging.debug(f'Nearest stores: {nearest_stores}')

    items = []

    for store in nearest_stores:
        store_items = flash_food.get_items(store['id'], access_token)
        if 'success' in store_items:
            logging.debug(f"get_items for [{store['name']}] returned successfully")
            store_items_dict = json.loads(store_items)
            for store_item in store_items_dict['success']['items']:
                store_item.update({'store': store['name']})
                items.append(store_item)
        else:
            logging.error(f"get_items for [{store['name']}] failed to return successfully")
            logging.debug(f'{store_items}')

    conn = init_db()

    for item in items:
        logging.debug(f'Item [{item}]')
        item_row = db.select_item(conn, item['_id'])
        logging.debug(f'Select returned [{item_row}]')
        push_string = ''

        if len(item_row) == 1:
            logging.debug("%[item['_id']] seen before...")
            if item_row[0][1] != item['name_en']:
                logging.debug("DB: [%item_row[0][1]] != [%item['name_en']]")
            elif item_row[0][2] != item['discounted_price']:
                logging.debug("DB: [%item_row[0][2]] != [%item['discounted_price']]")
                logging.debug('... and changed. Updating...')
                db.update_item(conn, [item['name_en'], item['discounted_price'], item['_id']])
                push_string = 'updated.\r'
            else:
                logging.debug('... and unchanged. Skipping on...')
                continue
        elif len(item_row) > 1:
            logging.error(f"Primary key constraint violated. Count of rows with {item['_id']} is {len(item_row)}.")
            continue
        else:
            logging.debug("[%item['_id']] not seen before.")
            db.create_item(conn, [item['_id'], item['name_en'], item['discounted_price']])
            push_string = '.\r'

        itemImage = flash_food.get_image(item['image_url'], item['_id'])

        if item['original_price'] > 0 or item['original_price'] == item['discounted_price']:
            discount = 1-(item['discounted_price']/item['original_price'])
            discountPercent = discount*100
            print(f"{item['name_en']} ${item['discounted_price']:.2f} - {discountPercent:.0f}% discount")
            pushover.notify(
                pushover_apikey,
                pushover_userkeys,
                f"FlashAlert - {item['name']}",
                f"{item['name_en']} {push_string}${item['discounted_price']:.2f} - {discountPercent:.0f}% discount",
                itemImage)
        else:
            print(f"{item['name_en']} ${item['discounted_price']:.2f}")
            pushover.notify(
                pushover_apikey,
                pushover_userkeys,
                f"FlashAlert - {item['name']}",
                f"{item['name_en']} {push_string}${item['discounted_price']:.2f}",
                itemImage)


if __name__ == '__main__':
    main()
