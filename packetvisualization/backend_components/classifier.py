import pandas as pd
import arff
from sklearn.cluster import KMeans


class Classifier:
    feature_list = []
    result_data_frame = pd.DataFrame()
    categorical_data = pd.DataFrame()
    centroids = []

    def __init__(self, cluster_number, context_results) -> None:
        if (context_results is None or cluster_number < 1):
            raise ('Invalid param values')
        """
        Data preprocessing
        """
        self.try_parse_context_to_dataframe(context_results)
        self.calculate_categorical_values()
        """
        Running the Classifying algorithm
        """
        self.classify_dataset(cluster_number)

    def try_parse_context_to_dataframe(self, context_results):
        try:
            self.result_data_frame = pd.json_normalize(context_results).fillna(0)
            self.feature_list = list(self.result_data_frame.columns)
        except:
            raise 'Could not cast the results'

    def calculate_categorical_values(self):
        if self.feature_list is []:
            raise 'Feature list is empty'
        for feature in self.feature_list:
            self.cast_features_to_categorical(feature)

    def cast_features_to_categorical(self, column_name):
        new_column_name = f'derived{column_name}'
        self.result_data_frame[column_name] = pd.Categorical(self.result_data_frame[column_name])
        self.result_data_frame[new_column_name] = self.result_data_frame[column_name].cat.codes

    def classify_dataset(self, cluster_number):
        km = KMeans(n_clusters=cluster_number)
        nominal_idx = -4
        nominal_df = pd.DataFrame(self.result_data_frame[self.result_data_frame.columns[nominal_idx:]])
        label = km.fit_predict(nominal_df)
        self.centroids = km.cluster_centers_
        self.result_data_frame['cluster'] = label
        self.result_data_frame['instance_number'] = self.result_data_frame.index + 1

    # ARFF IMPLEMENTATION
    def cast_arff_to_data(self, input_arff_file):
        try:
            file = open(input_arff_file)
        except:
            raise 'Invalid file'
        decoder = arff.ArffDecoder()
        decoded_arff = decoder.decode(file, encode_nominal=True)
        self.set_data_frame(decoded_arff)

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
        self.result_data_frame = pd.DataFrame(data_dictionary['data'], columns=self.feature_list)
