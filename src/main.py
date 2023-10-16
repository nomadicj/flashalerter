import os
import logging
from logging.handlers import TimedRotatingFileHandler

import flash_food

import pushover
import db

from dotenv import load_dotenv


# Set vars
load_dotenv()
flashfood_user = os.getenv('FLASHFOOD_USER')
flashfood_pass = os.getenv('FLASHFOOD_PASS')
flashfood_store_ids = os.getenv('FLASHFOOD_STORE_IDS').split(',')
pushover_apikey = os.getenv('PUSHOVER_APIKEY')
pushover_userkey = os.getenv('PUSHOVER_USERKEY')
pushover_userkeys = os.getenv('PUSHOVER_USERKEYS').split(',')
db_file = os.getenv('DB_FILE')
log_level = os.getenv('LOG_LEVEL', default='info').upper()

# Setup logging
log_dir = 'log'
log_file = 'flashalerter.log'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
  
logging.basicConfig(
    handlers=[TimedRotatingFileHandler(f'{log_dir}/{log_file}', backupCount=10, when='midnight')],
    format='%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s',
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

def main():
    """
    """

    flashfood = flash_food.Api(flashfood_user, flashfood_pass)

    lat: float = 49.2568
    long: float = -122.8255
    distance: int = 5

    stores = flashfood.get_nearest_stores(lat, long, distance)

    logging.debug('Nearest stores: %s', stores)

    conn = init_db()

    for store in stores:
        for item in store.get_items():
            logging.debug('Item [%s]', item._id)
            item_row = db.select_item(conn, item._id)
            logging.debug('Select returned [%s]', item_row)
            push_string = ''

            if len(item_row) == 1:
                logging.debug(f'{item._id} seen before...')
                if item_row[0][1] != item.name_en:
                    logging.debug(f'DB: {item_row[0][1]} != {item.name_en}')
                elif item_row[0][2] != item.discounted_price:
                    logging.debug(f'DB: {item_row[0][2]} != {item.discounted_price}')
                    logging.debug('... and changed. Updating...')
                    db.update_item(conn, [item.name_en, item.discounted_price, item._id])
                    push_string = 'updated.\r'
                else:
                    logging.debug('... and unchanged. Skipping on...')
                    continue
            elif len(item_row) > 1:
                logging.error(f'Primary key constraint violated. Count of rows with {item._id} is {len(item_row)}.')
                continue
            else:
                logging.debug(f'{item._id} not seen before.')
                db.create_item(conn, [item._id, item.name_en, item.discounted_price])
                push_string = '.\r'

            if item.original_price > 0 or item.original_price == item.discounted_price:
                print(f'{item.name_en} ${item.discounted_price:.2f} - {item.discounted_percentage}% discount')
                pushover.notify(
                    pushover_apikey,
                    pushover_userkeys,
                    f"{item.store_id}",
                    f"{item.name_en} {push_string}${item.discounted_price:.2f} - {item.discounted_percentage:.0f}% discount",
                    item.image)
            else:
                print(f"{item.name_en} ${item.discounted_price:.2f}")
                pushover.notify(
                    pushover_apikey,
                    pushover_userkeys,
                    f"{item.store_id}",
                    f"{item.name_en} {push_string}${item.discounted_price:.2f}",
                    item.image)


if __name__ == '__main__':
    main()
