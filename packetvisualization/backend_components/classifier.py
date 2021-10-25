import pandas as pd
import arff
from sklearn.cluster import KMeans


class Classifier:
    feature_list = []
    data_frame = pd.DataFrame()
    categorical_data = pd.DataFrame()
    centroids = []

    def __init__(self, cluster_number, data_dictionary={}, has_arff_file=False, arff_file=None):
        if has_arff_file and arff_file is not None:
            self.cast_arff_to_data(arff_file)
        elif data_dictionary != {}:
            self.set_data_frame(data_dictionary)
        else:
            raise 'Invalid input data'

        self.calculate_categorical_values()
        self.classify_dataset(cluster_number)

    def set_data_frame(self, data_dictionary):
        """
        data_dictionary structure:
        REQUIRED IN DICTIONARY

        A vector of headers that are the attributes present in the data to classify
        data_dictionary['attributes'] = ['col_header_1','col_header_2',...,'col_header_N']

        A matrix with the data that maps by column to each header in attributes
        data_dictionary['data'] = [[row1_data_1,row1_data_2,...,'row1_data_N'],
                                   [row2_data_1,row2_data_2,...,'row2_data_N']]
        """
        if 'attributes' not in data_dictionary and 'data' not in data_dictionary:
            raise 'Required keys are not present in dictionary'
        self.feature_list = [seq[0] for seq in data_dictionary['attributes']]
        self.data_frame = pd.DataFrame(data_dictionary['data'], columns=self.feature_list)
        self.data_frame['instance_number'] = self.data_frame.index + 1

    def calculate_categorical_values(self):
        for feature in self.feature_list:
            self.cast_to_categorical(feature)

    def cast_to_categorical(self, column_name):
        new_column_name = f'_{column_name}'
        self.data_frame[column_name] = pd.Categorical(self.data_frame[column_name])
        self.data_frame[new_column_name] = self.data_frame[column_name].cat.codes

    def classify_dataset(self, cluster_number):
        km = KMeans(n_clusters=cluster_number)
        nominal_idx = -4
        nominal_df = pd.DataFrame(self.data_frame[self.data_frame.columns[nominal_idx:]])
        label = km.fit_predict(nominal_df)
        self.centroids = km.cluster_centers_
        self.data_frame['cluster'] = label

    def cast_arff_to_data(self, input_arff_file):
        try:
            file = open(input_arff_file)
        except:
            raise 'Invalid file'
        decoder = arff.ArffDecoder()
        decoded_arff = decoder.decode(file, encode_nominal=True)
        self.set_data_frame(decoded_arff)
