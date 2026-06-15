# import mysql.connector

# def get_db_connection():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="",   # XAMPP default
#         database="travelsite"
#     )

import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="travel_db",
        port=3306
    )

#     return conn
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",   # XAMPP password မရှိရင် blank
    database="travel_db"
)