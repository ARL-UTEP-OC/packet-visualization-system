import os
import traceback

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMenu, QAction

from packetvisualization.models.context.database_context import DbContext
from packetvisualization.models.dataset import Dataset
from packetvisualization.models.pcap import Pcap


def field_dictionary():
    dictionary = {
        "frame-number": 0,
        "frame-time_relative": 0,
        "ip-src": 0,
        "ip-dst": 0,
        "srcport": 0,
        "dstport": 0,
        "frame-protocols": 0,
        "frame-len": 0
    }
    return dictionary


class table_gui(QTableWidget):
    def __init__(self, obj, progressbar, db: DbContext):
        super().__init__()
        self.dict = field_dictionary()
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels(
            ["No.", "Time", "Source IP", "Destination IP", "srcport", "dstport", "Protocol", "Length"])
        self.verticalHeader().hide()
        fnt = QFont()
        fnt.setPointSize(11)
        fnt.setBold(True)
        self.horizontalHeader().setFont(fnt)

        self.populate_table(obj=obj, progressbar=progressbar, db=db)

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        self.mark_action = QAction("Mark/Unmark Packet", self)
        self.mark_action.triggered.connect(self.mark_packet)

        self.viewASCII_action = QAction("View as ASCII", self)
        self.viewASCII_action.triggered.connect(self.view_as_ASCII)

        self.viewRAW_action = QAction("View as RAW", self)
        self.viewRAW_action.triggered.connect(self.view_as_RAW)

        self.viewText_action = QAction("View as text", self)
        self.viewText_action.triggered.connect(self.view_as_text)

        menu.addAction(self.mark_action)

        view_menu = menu.addMenu("View")
        view_menu.addAction(self.viewASCII_action)
        view_menu.addAction(self.viewRAW_action)
        view_menu.addAction(self.viewText_action)

        menu.exec(event.globalPos())

    def view_as_text(self):
        try:
            if self.selectedItems():
                selected = self.selectedItems()
                for item in selected:
                    if item.column() != 0:
                        if item.data(Qt.UserRole) is not None:
                            item.setText(item.data(Qt.UserRole))
                            self.resizeRowToContents(item.row())
        except:
            traceback.print_exc()

    def view_as_RAW(self):
        try:
            if self.selectedItems():
                selected = self.selectedItems()
                for item in selected:
                    if item.column() != 0:
                        if item.data(Qt.UserRole) is None:
                            text = item.text()
                            item.setData(Qt.UserRole, text)
                        else:
                            text = item.data(Qt.UserRole)
                        raw = ':'.join(hex(ord(x))[2:] for x in text)
                        item.setText(raw)
                        self.resizeRowToContents(item.row())
        except:
            traceback.print_exc()

    def view_as_ASCII(self):
        try:
            if self.selectedItems():
                selected = self.selectedItems()
                for item in selected:
                    if item.column() != 0:
                        if item.data(Qt.UserRole) is None:
                            text = item.text()
                            item.setData(Qt.UserRole, text)
                        else:
                            text = item.data(Qt.UserRole)
                        ascii = ""
                        for char in text:
                            ascii += str(ord(char)) + " "
                        item.setText(ascii)
                        self.resizeRowToContents(item.row())
        except:
            traceback.print_exc()

    def mark_packet(self):
        try:
            if self.selectedItems():
                selected = self.selectedItems()
                prev_row = -1
                row_list = []
                for item in selected:
                    if item.row() != prev_row and item.row() not in row_list:
                        if item.background() == QColor(255, 182, 193):
                            for j in range(self.columnCount()):
                                self.item(item.row(), j).setBackground(QColor(255, 255, 255))
                        else:
                            for j in range(self.columnCount()):
                                self.item(item.row(), j).setBackground(QColor(255, 182, 193))
                        prev_row = item.row()
                        row_list.append(prev_row)
        except:
            traceback.print_exc()

    def populate_table(self, obj, progressbar, db):
        if type(obj) is Pcap:
            dataset_name = os.path.basename(obj.directory)
            collection = db[dataset_name]
            query = {'parent_pcap': obj.name}
            data = collection.find(query)
        elif type(obj) is Dataset:
            dataset_name = obj.name
            collection = db[dataset_name]
            query = {'parent_dataset': obj.name}
            data = collection.find(query)

        self.setRowCount(data.count())
        value = (100 / data.count())
        progressbar_value = 0
        progressbar.show()
        i = 0
        for packet in data:
            self.setItem(i, 0, QTableWidgetItem(packet['_source']['layers']['frame'].get('frame-number')))
            self.dict["frame-number"] += 1

            self.setItem(i, 1, QTableWidgetItem(packet['_source']['layers']['frame'].get('frame-time_relative')))
            self.dict["frame-time_relative"] += 1

            if packet['_source']['layers'].get('ip') is not None:
                self.setItem(i, 2, QTableWidgetItem(packet['_source']['layers'].get('ip').get('ip-src')))
                self.dict["ip-src"] += 1
                self.setItem(i, 3, QTableWidgetItem(packet['_source']['layers'].get('ip').get('ip-dst')))
                self.dict["ip-dst"] += 1
            else:
                self.setItem(i, 2, QTableWidgetItem(None))
                self.setItem(i, 3, QTableWidgetItem(None))
                self.horizontalHeaderItem(2).setForeground(QColor(175, 175, 175))
                self.horizontalHeaderItem(3).setForeground(QColor(175, 175, 175))

            if packet['_source']['layers'].get('udp') is not None:
                self.setItem(i, 4, QTableWidgetItem(packet['_source']['layers'].get('udp').get('udp-srcport')))
                self.dict["srcport"] += 1
                self.setItem(i, 5, QTableWidgetItem(packet['_source']['layers'].get('udp').get('udp-dstport')))
                self.dict["dstport"] += 1
            elif packet['_source']['layers'].get('tcp') is not None:
                self.setItem(i, 4, QTableWidgetItem(packet['_source']['layers'].get('tcp').get('tcp-srcport')))
                self.dict["srcport"] += 1
                self.setItem(i, 5, QTableWidgetItem(packet['_source']['layers'].get('tcp').get('tcp-dstport')))
                self.dict["dstport"] += 1
            else:
                self.setItem(i, 4, QTableWidgetItem(None))
                self.setItem(i, 5, QTableWidgetItem(None))
                self.horizontalHeaderItem(4).setForeground(QColor(175, 175, 175))
                self.horizontalHeaderItem(5).setForeground(QColor(175, 175, 175))

            protocols = packet['_source']['layers']['frame'].get('frame-protocols')
            self.setItem(i, 6, QTableWidgetItem(protocols.split(':')[-1].upper()))
            self.dict["frame-protocols"] += 1

            self.setItem(i, 7, QTableWidgetItem(packet['_source']['layers']['frame'].get('frame-len')))
            self.dict["frame-len"] += 1

            i += 1
            progressbar_value = progressbar_value + value
            progressbar.setValue(progressbar_value)

        self.update_lables()
        self.resizeColumnsToContents()
        progressbar.setValue(0)
        progressbar.hide()

    def update_lables(self):
        self.horizontalHeaderItem(0).setText("No. (" + str(self.dict["frame-number"]) + ")")
        self.horizontalHeaderItem(1).setText(
            "Time (" + str(self.dict["frame-time_relative"]) + ")")
        self.horizontalHeaderItem(2).setText("Source IP (" + str(self.dict["ip-src"]) + ")")
        self.horizontalHeaderItem(3).setText("Dest IP (" + str(self.dict["ip-dst"]) + ")")
        self.horizontalHeaderItem(4).setText("Source Port (" + str(self.dict["srcport"]) + ")")
        self.horizontalHeaderItem(5).setText("Dest Port (" + str(self.dict["dstport"]) + ")")
        self.horizontalHeaderItem(6).setText("Protocol (" + str(self.dict["frame-protocols"]) + ")")
        self.horizontalHeaderItem(7).setText("Length (" + str(self.dict["frame-len"]) + ")")
