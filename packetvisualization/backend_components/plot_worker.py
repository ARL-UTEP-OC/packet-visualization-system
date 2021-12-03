from collections import Counter
from datetime import datetime

import pandas as pd
from PyQt5.QtCore import QObject, pyqtSignal


class PlotWorker(QObject):
    finished = pyqtSignal()
    data = pyqtSignal(list)

    def __init__(self, dataset, db):
        super().__init__()
        self.dataset = dataset
        self.db = db
        self.db_data = None

    def run(self):
        if self.dataset:
            # collection = self.db[self.dataset.name]
            # query = {'parent_dataset': self.dataset.name}
            # self.db_data = list(collection.find({}))
            if self.dataset.has_changed:
                # backend = TableBackend()
                # self.db_data = backend.query_pcap(self.dataset, self.db)
                collection = self.db[self.dataset.name]
                self.db_data = collection.find()
            else:
                self.data.emit(self.dataset.packet_data)
                self.finished.emit()
                return 1
        else:
            self.db_data = None

        if self.db_data:
            date, protocol, time_epoch = [], [], []

            for packet_data in self.db_data:
                epoch_time = packet_data['_source']['layers']['frame']['frame-time_epoch']
                if epoch_time is not None:
                    time_epoch = float(epoch_time)
                    date.append(datetime.fromtimestamp(time_epoch))
                protocol.append(packet_data['_source']['layers']['frame']['frame-protocols'])

            date.sort()

            r_protocols = []
            for p in protocol:
                s = p.split(":")
                if s[-1] != 'data':
                    r_protocols.append(s[-1])
                else:
                    r_protocols.append(s[-2])

            self.dataset.protocols = Counter(r_protocols)
            self.dataset.protocols = sorted(self.dataset.protocols.items(), key=lambda x: (x[1], x[0]), reverse=True)

            d = {"datetime": date}
            df = pd.DataFrame(data=d)

            self.dataset.s_time = date[0]
            self.dataset.e_time = date[-1]
            self.dataset.totalPackets = len(date)

            plot_x = pd.date_range(date[0].replace(microsecond=0, second=0),
                                   date[-1].replace(microsecond=0, second=0, minute=date[-1].minute + 1),
                                   periods=100)
            plot_y = [0 for i in range(len(plot_x))]

            result_df = []

            for d in range(len(plot_x) - 1):
                mask = (df["datetime"] >= plot_x[d]) & (df["datetime"] < plot_x[d + 1])
                result_df.append(df[mask])

            for i in range(len(result_df)):
                plot_y[i] = len(result_df[i])

            self.dataset.packet_data = [plot_x, plot_y]
            self.dataset.has_changed = False
        else:
            plot_x, plot_y = [], []

        self.data.emit([plot_x, plot_y])
        self.finished.emit()
