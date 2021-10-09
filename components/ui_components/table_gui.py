import json

from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem
import sys
from PyQt5 import QtGui


class table_gui(QTableWidget):
    def __init__(self):
        super().__init__()

        self.setColumnCount(6)
        self.setRowCount(8)

        self.setHorizontalHeaderLabels(["No.", "Time", "Source", "Destination", "Protocol", "Length"])
        self.verticalHeader().hide()

        self.populate_table()

    def populate_table(self):
        json_file = "C:\\Users\\eyanm\\PracticumGUI\\TestSpace\\test.json"

        with open(json_file) as file:
            data = json.load(file)

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

