import json
import os
import platform
import shutil

from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem
import sys
from PyQt5 import QtGui

from packetvisualization.models.pcap import Pcap


class table_gui(QTableWidget):
    def __init__(self, pcap: Pcap, progressbar):
        super().__init__()

        self.setColumnCount(6)

        self.setHorizontalHeaderLabels(["No.", "Time", "Source", "Destination", "Protocol", "Length"])
        self.verticalHeader().hide()

        pcap_json = self.pcap_to_json(pcap)
        self.populate_table(pcap_json=pcap_json, progressbar=progressbar)

    def pcap_to_json(self, pcap):
        name = pcap.name
        name = name.strip('.pcap')
        name = name + ".json"

        path = os.path.dirname(pcap.path)
        json_file = os.path.join(path, name)
        self.temp_file = json_file

        if platform.system() == "Windows":
            os.system('cd "C:\Program Files\Wireshark" & tshark -r ' + pcap.pcap_file + ' -T json > ' + json_file)
        elif platform.system()=="Linux":
            os.system('tshark -r ' + pcap.pcap_file + ' -T json > ' + json_file)

        return json_file

    def populate_table(self, pcap_json, progressbar):
        with open(pcap_json) as file:
            data = json.load(file)
            file.close()

        self.setRowCount(len(data))

        value = (100/len(data))
        progressbar_value = 0
        progressbar.show()
        i = 0
        for packet in data:
            self.setItem(i, 0, QTableWidgetItem(packet['_source']['layers']['frame'].get('frame.number')))
            self.setItem(i, 1, QTableWidgetItem(packet['_source']['layers']['frame'].get('frame.time_relative')))

            if packet['_source']['layers'].get('ip') is not None:
                self.setItem(i, 2, QTableWidgetItem(packet['_source']['layers'].get('ip').get('ip.src')))
                self.setItem(i, 3, QTableWidgetItem(packet['_source']['layers'].get('ip').get('ip.dst')))

            protocols = packet['_source']['layers']['frame'].get('frame.protocols')
            self.setItem(i, 4, QTableWidgetItem(protocols.split(':')[-1].upper()))
            self.setItem(i, 5, QTableWidgetItem(packet['_source']['layers']['frame'].get('frame.len')))

            i += 1
            progressbar_value = progressbar_value + value
            progressbar.setValue(progressbar_value)

        progressbar.setValue(0)
        progressbar.hide()
        os.remove(self.temp_file)
