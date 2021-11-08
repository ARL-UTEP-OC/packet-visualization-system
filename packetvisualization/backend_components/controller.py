import os
import pandas as pd
from bson.objectid import ObjectId

from packetvisualization.backend_components.classifier import Classifier
from packetvisualization.backend_components.entity_operator import EntityOperations
from packetvisualization.models.dataset import Dataset
from packetvisualization.models.pcap import Pcap


class Controller:
    context = EntityOperations()

    # TODO: Fix cluster number to capture whatever the user inputs
    # TODO: Integrate functionality of processing user selected properties
    def classify_dataset(self, dataset_name: str, cluster_number=5) -> pd.DataFrame:
        """
        1. Get dataset packet metadata by dataset_name
        2. Transform Information to match classifier dictionary {attributes: [headers], data: [row]}
        3. Return classified data_frame to ui_component to plot.
        """
        context_results = self.context.get_packet_data_by_dataset(dataset_name)
        classifier = Classifier(cluster_number=cluster_number, context_results=context_results)
        classified_data = classifier.result_data_frame
        return classified_data

    def create_analysis(self, uuid_list, properties_list, cluster_number, obj, db):
        dataset_name = self.extract_dataset_name(obj)
        properties_dict = self.create_properties_dictionary(properties_list)
        mongo_id_list = self.create_mongo_id_list(uuid_list)
        context_results = self.context.get_packet_data(dataset_name, mongo_id_list, properties_dict, db)
        classifier = Classifier(cluster_number=cluster_number, context_results=context_results)
        classified_data = classifier.result_data_frame
        return classified_data, classifier.feature_list

    @staticmethod
    def create_properties_dictionary(properties_list):
        properties_dictionary = {'_id': 0}
        for p in properties_list:
            properties_dictionary[p] = 1
        return properties_dictionary

    @staticmethod
    def create_mongo_id_list(uuid_list):
        mongo_ids = []
        for s in uuid_list:
            mongo_ids.append(ObjectId(s))
        return mongo_ids

    @staticmethod
    def extract_dataset_name(obj):
        if type(obj) is Pcap:
            return os.path.basename(obj.directory)
        elif type(obj) is Dataset:
            return obj.name
        else:
            raise Exception('Invalid Object Type at extract_dataset')
