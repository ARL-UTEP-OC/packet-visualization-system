from packetvisualization.models.context.database_context import DbContext
from pymongo import MongoClient,InsertOne, DeleteMany
import json


class EntityOperator:

    def fix_dictionary(self,d):  # Function to replace any key with '.' in name
        new = {}
        for k, v in d.items():
            if isinstance(v, dict):
                v = self.fix_dictionary(v)
            new[k.replace('.', '-')] = v
        return new

    def insert_packets(self, json_file, collection, dataset_name, pcap_name):  # take json with packet information and bulk insert into DB
        requesting = []
        with open(json_file, encoding="ISO-8859-1") as f:
            packet_data = json.load(f)  # list of packets w/data as json object
            for jsonObj in packet_data:
                jsonObj["parent_dataset"] = dataset_name
                jsonObj["parent_pcap"] = pcap_name
                jsonObj = self.fix_dictionary(jsonObj)  # replace all key instances of "." with "-"

                requesting.append(InsertOne(jsonObj))

        collection.bulk_write(requesting)

    def delete_packets(self, collection, parent, name):
        query = {parent: name}
        collection.delete_many(query)

    def delete_collection(self, collection):
        collection.drop()
