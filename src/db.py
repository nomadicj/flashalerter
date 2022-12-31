import sqlite3
from sqlite3 import Error
import logging


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        logging.info(f'Connection to SQLite {sqlite3.version} successful')
    except Error as e:
        print(e)
        logging.error(f'Connection to SQLite errored: {e}')

    return conn


def create_table(conn):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """

    sql_create_items_table = """ CREATE TABLE IF NOT EXISTS items (
                                        id text PRIMARY KEY,
                                        name text NOT NULL,
                                        discounted_price real NOT NULL
                                    ); """

    try:
        c = conn.cursor()
        c.execute(sql_create_items_table)
    except Error as e:
        print(e)


def create_item(conn, item):
    """
    Create a new project into the projects table
    :param conn:
    :param item:
    :return: item id
    """
    sql = ''' INSERT INTO items(id,name,discounted_price)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, item)
    conn.commit()
    return cur.lastrowid


def update_item(conn, item):
    """
    update name, discounted_price of an item
    :param conn:
    :param item:
    :return: item id
    """
    sql = ''' UPDATE items
              SET name = ? ,
                  discounted_price = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, item)
    conn.commit()
    return cur.lastrowid


def select_item(conn, item_id):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param item_id:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE id=?", (item_id,))

    row = cur.fetchall()
    return row
