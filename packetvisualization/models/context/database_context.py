import pymongo
import subprocess
from pymongo.database import Database
from decouple import config


class DbContext:
    db = Database
    dbString = config('DBSTRING')

    def __init__(self):
        client = pymongo.MongoClient(f'{self.dbString}?retryWrites=true&w=majority')
        self.db = client.PracticumDB
        print(self.db.list_collections())

    def destroy_session(self):
        # TODO: Fix this, until this is fixed we have to manually delete the DB data
        # mongodump -d yourDB -c "your/colName" --out "-" --quiet > col.bson
        subprocess.call([f'mongodump --uri {self.dbString} --out "-" --quiet > col.bson']);

# Implementation example
context = DbContext()
packet = {'_id': 3, 'name': 'test-packet', 'meta': ['testing1', 'testing2']}

packets_doc = context.db.Packets
result = packets_doc.insert_one(packet)
