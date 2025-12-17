import mysql.connector as db
from config import DB_CONFIG

def get_db() :
    return db.connect(**DB_CONFIG)