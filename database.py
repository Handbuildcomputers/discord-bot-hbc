from env import *
import mysql.connector

# Database class
class Database:

    db = mysql.connector.connect(
    host = database_values.HOSTNAME,
    user = database_values.USERNAME,
    password = database_values.PASSWORD,
    database = database_values.DBNAME,
    auth_plugin="mysql_native_password"
    )
    cursor = db.cursor(buffered=False)
