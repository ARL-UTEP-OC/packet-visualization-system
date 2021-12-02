import os
from PyQt5.QtCore import QObject, pyqtSignal
from packetvisualization.backend_components.entity_operator import EntityOperations


class PcapWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, pcap, file, table, dataset_name):
        super().__init__()
        self.pcap = pcap
        self.file = file
        self.table = table
        self.dataset_name = dataset_name
        self.eo = EntityOperations()

    def run(self):
        count = 0
        for dirpath, _, filenames in os.walk(self.pcap.split_dir):
            for f in filenames:
                json_name = f.replace('.pcap', '.json')
                file = os.path.abspath(os.path.join(dirpath, f))
                json_file = os.path.join(self.pcap.split_json_dir, json_name)
                self.pcap.create_file(json_file)
                os.system('cd "C:\Program Files\Wireshark" & tshark -r ' + file + ' -T json > ' + json_file)

                count += 1
                progress = int((count / len(filenames) * 0.5) * 100)
                self.progress.emit(progress)

        count = 0
        for dirpath, _, filenames in os.walk(self.pcap.split_json_dir):
            parent_pcap = os.path.basename(os.path.normpath(dirpath)).replace('-splitjson', "")
            for f in filenames:
                file = os.path.abspath(os.path.join(dirpath, f))
                self.eo.insert_packets(file, self.table, self.dataset_name, parent_pcap)

                count += 1
                progress = int((count / len(filenames) * 0.5 + 0.5) * 100)
                self.progress.emit(progress)


        self.pcap.cleanup()

        self.finished.emit()



