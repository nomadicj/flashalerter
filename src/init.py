import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
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
    update priority, begin_date, and end date of a task
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


def select_item(conn, item_id):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param itemId:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE id=?", (item_id,))

    row = cur.fetchall()
    return row
    

def main():
    database = r"flashalerter.db"

    sql_create_items_table = """ CREATE TABLE IF NOT EXISTS items (
                                        id text PRIMARY KEY,
                                        name text NOT NULL,
                                        discounted_price real NOT NULL
                                    ); """

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create items table
        create_table(conn, sql_create_items_table)
    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()
