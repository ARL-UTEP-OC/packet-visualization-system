from collections import Counter
from datetime import datetime

import pandas as pd
from PyQt5.QtCore import QObject, pyqtSignal


class PlotWorker(QObject):
    finished = pyqtSignal()
    data = pyqtSignal(list)

    def __init__(self, dataset, db, filter={}):
        super().__init__()
        self.dataset = dataset
        self.db = db
        self.db_data = None
        self.filter = filter

    def run(self):
        if self.dataset:
            if self.dataset.has_changed:
                collection = self.db[self.dataset.name]
                self.dataset.db_data = collection.find(self.filter)
            else:
                self.data.emit(self.dataset.packet_data)
                self.finished.emit()
                return 1
        else:
            self.data.emit([[], []])
            self.finished.emit()
            return 1

        date, protocol_all, time_epoch = [], [], []
        self.dataset.list_data = []

        for d in self.dataset.db_data:
            _id = d["_id"]
            frame_time = d["_source"]["layers"]["frame"]["frame-time"]
            epoch_time = d['_source']['layers']['frame']['frame-time_epoch']

            if d['_source']['layers'].get('ip'):
                ip_src = d["_source"]["layers"]["ip"].get("ip-src")
                ip_dst = d["_source"]["layers"]["ip"].get("ip-dst")
            else:
                ip_src = None
                ip_dst = None

            if d['_source']['layers'].get('udp'):
                port_src = d['_source']['layers']['udp'].get('udp-srcport')
                port_dst = d['_source']['layers']['udp'].get('udp-dstport')
            elif d['_source']['layers'].get('tcp'):
                port_src = d['_source']['layers']['tcp'].get('tcp-srcport')
                port_dst = d['_source']['layers']['tcp'].get('tcp-dstport')
            else:
                port_src = None
                port_dst = None

            protocols = d["_source"]["layers"]["frame"]["frame-protocols"]
            protocols = protocols.split(":")
            if protocols[-1] == "Data":
                protocol = protocols[-2]
                protocol_all.append(protocol)
            else:
                protocol = protocols[-1]
                protocol_all.append(protocol)

            length = d["_source"]["layers"]["frame"]["frame-len"]

            self.dataset.list_data.append([_id, frame_time, ip_src, ip_dst, port_src, port_dst, protocol, length])

            if epoch_time is not None:
                time_epoch = float(epoch_time)
                date.append(datetime.fromtimestamp(time_epoch))
            # protocol.append(d['_source']['layers']['frame']['frame-protocols'])

        self.dataset.db_data.rewind()

        if len(date) > 0:
            date.sort()
            self.dataset.protocols = Counter(protocol_all)
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
        else:
            self.dataset.protocols = []
            self.dataset.s_time = ''
            self.dataset.e_time = ''
            self.dataset.totalPackets = len(date)
            plot_x, plot_y = [], []

        self.dataset.packet_data = [plot_x, plot_y]
        self.dataset.has_changed = False

        self.data.emit([plot_x, plot_y])
        self.finished.emit()
