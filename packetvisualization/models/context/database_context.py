import pymongo
from pymongo.database import Database
from decouple import config

class DbContext:
    db = Database
    # Find our connection string in the .env file in the root directory
    dbString = config('DBSTRING')

    def __init__(self):
        self.client = pymongo.MongoClient(f'{self.dbString}')