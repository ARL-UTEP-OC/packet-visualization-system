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
        # Testing
        # dataset_name = 'd2'
        context_results = self.context.get_packet_data_by_dataset(dataset_name)
        classifier = Classifier(cluster_number=cluster_number, context_results=context_results)
        classified_data = classifier.result_data_frame
        return classified_data

    def create_analysis(self, uuid_list, properties_list, cluster_number, obj):
        dataset_name =  self.extract_dataset_name(obj)
        properties_dict = self.create_properties_dictionary(properties_list)
        mongo_id_list = self.create_mongo_id_list(uuid_list)
        context_results = self.context.get_packet_data(dataset_name, mongo_id_list, properties_dict)
        classifier = Classifier(cluster_number=cluster_number, context_results=context_results)
        classified_data = classifier.result_data_frame
        return classified_data, classifier.feature_list
    
    def create_properties_dictionary(self, properties_list):
        properties_dictionary = {'_id': 0}
        for p in properties_list:
            properties_dictionary[p] = 1
        return properties_dictionary
    
    def create_mongo_id_list(self, uuid_list):
        objIds = []
        for s in uuid_list:
            objIds.append(ObjectId(s))
    
    def extract_dataset_name(self, obj):
        if type(obj) is Pcap:
            return os.path.basename(obj.directory)
        elif type(obj) is Dataset:
            return obj.name
        else:
            raise Exception('Invalid Object Type at extract_dataset')
