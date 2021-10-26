import pandas as pd

from packetvisualization.backend_components.classifier import Classifier
from packetvisualization.backend_components.entity_operator import EntityOperations


class Controller:
    context = EntityOperations()

    def classify_dataset(self, dataset_name: str) -> pd.DataFrame:
        """
        1. Get dataset packets by dataset_name
        2. Transform Information to match classifier dictionary {attributes: [headers], data: [row]}
        3. Return classified data_frame to ui_component to plot.
        """
        # Testing
        # dataset_name = 'd2'
        context_results = self.context.get_packet_data_by_dataset(dataset_name)
        classifier = Classifier(cluster_number=5, context_results=context_results)
        classified_data = classifier.result_data_frame
        return classified_data
