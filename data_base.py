import psycopg2
from psycopg2 import Error
import os
import pandas as pd

# Before heroku push, you must create a table using this script


def create_table() -> None:
    cursor.execute(f'''CREATE TABLE CITIES
       (id INT PRIMARY KEY,
        lat TEXT, 
        lon TEXT,
        last_changing TIMESTAMP)''')
    print('TABLE WAS MADE')


def delete_table() -> None:
    cursor.execute(f'DROP TABLE CITIES')
    # cursor.execute(f"DELETE FROM CITIES")


def show_table() -> None:
    my_table = pd.read_sql(f'SELECT * FROM CITIES', connection)
    print(my_table)


try:
    # connecting
    print("START")
    connection = psycopg2.connect(os.getenv('URI'))
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    print("you connected with",cursor.fetchall())

    # main part
    create_table()

    # ending
    cursor.close()
    connection.commit()
    connection.close()
    print("END")
except (Exception, Error) as error:
    print('ERROR', error)
