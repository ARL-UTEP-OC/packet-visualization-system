from datetime import datetime

import pandas as pd
from PyQt5.QtCore import QObject, pyqtSignal


class PlotWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    data = pyqtSignal(list)

    def __init__(self, data):
        super().__init__()
        self.db_data = data

    def run(self):
        if self.db_data:
            date, time_epoch = [], []

            for packet_data in self.db_data:
                time_epoch = float(packet_data['_source']['layers']['frame'].get('frame-time_epoch'))
                if time_epoch is not None:
                    date.append(datetime.fromtimestamp(time_epoch))

            d = {"datetime": date}
            df = pd.DataFrame(data=d)

            plot_x = pd.date_range(date[0].replace(microsecond=0, second=0),
                                   date[-1].replace(microsecond=0, second=0, minute=date[-1].minute + 1),
                                   periods=100)
            plot_y = [0 for i in range(len(plot_x))]

            result_df = []

            for d in range(len(plot_x)-1):
                mask = (df["datetime"] >= plot_x[d]) & (df["datetime"] < plot_x[d+1])
                result_df.append(df[mask])
                progress = int(d / len(date) * 100)
                self.progress.emit(progress)

            for i in range(len(result_df)):
                plot_y[i] = len(result_df[i])
        else:
            self.progress.emit(50)
            plot_x, plot_y = [], []
            self.progress.emit(100)

        self.data.emit([plot_x, plot_y])
        self.finished.emit()
