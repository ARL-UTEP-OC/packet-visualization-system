from packetvisualization.models.context.database_context import DbContext
from pymongo import MongoClient, InsertOne, DeleteMany
import json
import os


class EntityOperations:
    context = DbContext()
    client = context.client

    def create_db(self,workspace_name):  # create new DB when we have a new workspace
        mydb = self.client[workspace_name]
        return mydb

    def remove_db(self, workspace_name):  # Use when we don't save workspace
        self.client.drop_database(workspace_name)

    def dump_db(self, workspace_name, save_dir):
        os.system("mongodump --db " + workspace_name + " --out " + save_dir)

    def restore_db(self, workspace_name, save_location):
        os.system("mongorestore --db " + workspace_name + " --drop " + save_location)

    def set_db(self, workspace_name):
        db = self.client[workspace_name]
        return db

    def fix_dictionary(self, d):  # Function to replace any key with '.' in name
        new = {}
        for k, v in d.items():
            if isinstance(v, dict):
                v = self.fix_dictionary(v)
            new[k.replace('.', '-')] = v
        return new

    def insert_packets(self, json_file, collection, dataset_name, pcap_name):  # take json with packet information and bulk insert into DB
        requesting = []
        with open(json_file, encoding="ISO-8859-1") as f:  #
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

    def get_packet_data_by_dataset(self, dataset_name: str):
        collection = self.context.db[dataset_name]
        query = {'parent_dataset': dataset_name}
        context_results = list(collection.find(query, {
            '_id': 0,
            '_source.layers.ip.ip-dst': 1,
            '_source.layers.ip.ip-src': 1,
            '_source.layers.udp.udp-srcport': 1,
            '_source.layers.udp.udp-dstport': 1, }))
        return context_results

    def get_packet_data(self, dataset_name, object_id_list, properties_dictionary, db):
        """Gets selected packets data, for kmeans analysis"""
        collection = db[dataset_name]
        context_results = list(collection.find({"_id": {"$in": object_id_list}}, properties_dictionary))
        return context_results
