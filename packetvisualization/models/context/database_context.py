import pymongo
import subprocess
from pymongo.database import Database
from decouple import config
import certifi

class DbContext:
    db = Database
    # Find our connection string in the .env file in the root directory
    dbString = config('DBSTRING')

    def __init__(self):
        # CLOUD
        # client = pymongo.MongoClient(f'{self.dbString}?retryWrites=true&w=majority', tlsCAFile=certifi.where())
        # LOCAL
        self.client = pymongo.MongoClient(f'{self.dbString}')
        # self.db = client.PracticumDB
        # print(self.db.list_collections())

    def destroy_session(self):
        # TODO: Fix this, until this is fixed we have to manually delete the DB data
        # mongodump -d yourDB -c "your/colName" --out "-" --quiet > col.bson
        subprocess.call([f'mongodump --uri {self.dbString} --out "-" --quiet > col.bson']);

# Implementation example
# context = DbContext()
# packet = {'_id': 3, 'name': 'test-packet', 'meta': ['testing1', 'testing2']}
# To create a new collections table replace the name 'Packets' with yourtable name
# packets_doc = context.db.Packets
# result = packets_doc.insert_one(packet)