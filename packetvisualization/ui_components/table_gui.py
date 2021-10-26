import os
import platform
import shutil
import subprocess
import traceback

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMenu, QAction, QInputDialog, QFileDialog, QTreeWidgetItem

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


def gen_frame_string(list_in):
    frame_string = ""
    for i in range(len(list_in)):
        if i == 0:
            frame_string += "frame.number==" + str(list_in[i])
        else:
            frame_string += " || frame.number==" + str(list_in[i])
    return frame_string


class table_gui(QTableWidget):
    def __init__(self, obj, progressbar, db: DbContext, workspace):
        super().__init__()
        self.icons = os.path.join(os.path.dirname(__file__), "images", "svg")
        self.workspace = workspace
        self.obj = obj
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

        self.tag_action = QAction("Add Tag", self)
        self.tag_action.triggered.connect(self.add_tag)

        self.remove_tag_action = QAction("Remove Tag", self)
        self.remove_tag_action.triggered.connect(self.remove_tag)

        self.create_dataset_action = QAction("Create Dataset", self)
        self.create_dataset_action.triggered.connect(self.create_dataset)

        self.tagged_create_dataset_action = QAction("Create Dataset", self)
        self.tagged_create_dataset_action.triggered.connect(lambda : self.create_dataset(tagged= True))

        self.viewASCII_action = QAction("View as ASCII", self)
        self.viewASCII_action.triggered.connect(self.view_as_ASCII)

        self.viewRAW_action = QAction("View as RAW", self)
        self.viewRAW_action.triggered.connect(self.view_as_RAW)

        self.viewText_action = QAction("View as text", self)
        self.viewText_action.triggered.connect(self.view_as_text)

        self.view_in_wireshark_action = QAction("View in Wireshark", self)
        self.view_in_wireshark_action.triggered.connect(self.view_in_wireshark)

        self.view_tagged_in_wireshark_action = QAction("View in Wireshark", self)
        self.view_tagged_in_wireshark_action.triggered.connect(self.view_tagged_in_wireshark)

        menu.addAction(self.mark_action)
        menu.addAction(self.tag_action)
        menu.addAction(self.remove_tag_action)
        menu.addAction(self.create_dataset_action)
        menu.addAction(self.view_in_wireshark_action)

        tagged_menu = menu.addMenu("Tagged")
        tagged_menu.addAction(self.view_tagged_in_wireshark_action)
        tagged_menu.addAction(self.tagged_create_dataset_action)

        view_menu = menu.addMenu("View")
        view_menu.addAction(self.viewASCII_action)
        view_menu.addAction(self.viewRAW_action)
        view_menu.addAction(self.viewText_action)

        menu.exec(event.globalPos())

    def view_in_wireshark(self):
        try:
            list = []
            if self.selectedItems():
                selected = self.selectedItems()
                row_list = []
                for item in selected:
                    if item.row() not in row_list:
                        frame_number = self.item(item.row(), 0).text()
                        list.append(frame_number)
                        row_list.append(item.row())

            frame_string = gen_frame_string(list)

            output_file = os.path.join(os.getcwd(), "tEmPpCaP.pcap")

            if type(self.obj) == Pcap:
                infile = self.obj.path
            else:
                infile = self.obj.mergeFilePath

            if (platform.system()=="Windows"):
                os.system(
                    'cd "C:\Program Files\Wireshark" & tshark -r ' + infile + ' -Y \"' + frame_string + '\" -w ' + output_file)
                subprocess.Popen("C:\Program Files\Wireshark\wireshark -r " + output_file)
            elif (platform.system()=="Linux"):
                os.system('tshark -r ' + infile + ' -Y \"' + frame_string + '\" -w ' + output_file)
                subprocess.Popen("wireshark -r " + output_file)
        except:
            traceback.print_exc()

    def view_tagged_in_wireshark(self):
        try:
            list = []
            tag = QInputDialog.getText(self, "Tag Name Entry", "Enter Tag name:")[0]
            for i in range(self.rowCount()):
                if self.item(i, 0).data(Qt.UserRole) == tag:
                    list.append(self.item(i, 0).text())

            if len(list) > 0:
                frame_string = gen_frame_string(list)

                output_file = os.path.join(os.getcwd(), "tEmPpCaP.pcap")

                if type(self.obj) == Pcap:
                    infile = self.obj.path
                else:
                    infile = self.obj.mergeFilePath

                if (platform.system() == "Windows"):
                    os.system(
                        'cd "C:\Program Files\Wireshark" & tshark -r ' + infile + ' -Y \"' + frame_string + '\" -w ' + output_file)
                    subprocess.Popen("C:\Program Files\Wireshark\wireshark -r " + output_file)
                elif (platform.system() == "Linux"):
                    os.system('tshark -r ' + infile + ' -Y \"' + frame_string + '\" -w ' + output_file)
                    subprocess.Popen("wireshark -r " + output_file)
        except:
            traceback.print_exc()

    def add_tag(self):
        if self.selectedItems():
            selected = self.selectedItems()
            row_list = []
            tag = QInputDialog.getText(self, "Tag Name Entry", "Enter Tag name:")[0]
            for item in selected:
                if item.row() not in row_list and tag != "":
                    self.item(item.row(), 0).setData(Qt.UserRole, tag)
                    self.item(item.row(), 0).setIcon(QIcon(os.path.join(self.icons, "pricetag.svg")))
                    self.item(item.row(), 0).setToolTip(tag)
                    self.item(item.row(), 0).setStatusTip(tag)

                    row_list.append(item.row())
        return

    def remove_tag(self):
        try:
            if self.selectedItems():
                selected = self.selectedItems()
                row_list = []
                for item in selected:
                    if item.row() not in row_list:
                        self.item(item.row(), 0).setData(Qt.UserRole, None)
                        self.item(item.row(), 0).setIcon(QIcon())
                        self.item(item.row(), 0).setStatusTip(None)
                        self.item(item.row(), 0).setToolTip(None)
                        row_list.append(item.row())
        except:
            traceback.print_exc()

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

    def create_dataset(self, tagged: bool = None):
        try:
            list = []
            if not tagged:
                if self.selectedItems():
                    selected = self.selectedItems()
                    row_list = []
                    for item in selected:
                        if item.row() not in row_list:
                            frame_number = self.item(item.row(), 0).text()
                            list.append(frame_number)
                            row_list.append(item.row())
            if tagged:
                tag = QInputDialog.getText(self, "Tag Name Entry", "Enter Tag name:")[0]
                for i in range(self.rowCount()):
                    if self.item(i, 0).data(Qt.UserRole) == tag:
                        list.append(self.item(i, 0).text())

            frame_string = gen_frame_string(list)
            output_file = os.path.join(os.getcwd(), "tEmPpCaP.pcap")

            if type(self.obj) == Pcap:
                infile = self.obj.path
            else:
                infile = self.obj.mergeFilePath

            if (platform.system() == "Windows"):
                os.system(
                    'cd "C:\Program Files\Wireshark" & tshark -r ' + infile + ' -Y \"' + frame_string + '\" -w ' + output_file)
            elif (platform.system() == "Linux"):
                os.system('tshark -r ' + infile + ' -Y \"' + frame_string + '\" -w ' + output_file)

            items = []
            for p in self.workspace.workspace_object.project:
                items.append(p.name)

            item, ok = QInputDialog.getItem(self, "Select Project",
                                            "List of Projects", items, 0, False)

            if ok and item:
                text = QInputDialog.getText(self, "Dataset Name Entry", "Enter Dataset name:")[0]
                project_item = self.workspace.project_tree.findItems(item, Qt.MatchRecursive, 0)[0]
                project_object = project_item.data(0, Qt.UserRole)

                if text:
                    # Add Project and Dataset object && project tree item
                    dataset_object = Dataset(name=text, parentPath=project_object.path)
                    project_object.add_dataset(dataset_object)
                    child_item = QTreeWidgetItem()
                    child_item.setText(0, text)
                    child_item.setData(0, Qt.UserRole, dataset_object)
                    project_item.addChild(child_item)

                    # Add PCAP object && project tree item
                    base = os.path.splitext(self.obj.name)[0]
                    new_pcap = Pcap(file=output_file, path=dataset_object.path, name="sub_"+base+".pcap")
                    dataset_object.add_pcap(new_pcap)
                    pcap_item = QTreeWidgetItem()
                    pcap_item.setText(0, new_pcap.name)
                    pcap_item.setData(0, Qt.UserRole, new_pcap)
                    child_item.addChild(pcap_item)

                    # Insert into Database
                    mytable = self.workspace.db[dataset_object.name]
                    self.workspace.eo.insert_packets(new_pcap.json_file, mytable, dataset_object.name, new_pcap.name)

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
            frame_number_item = QTableWidgetItem(str(i + 1))
            self.setItem(i, 0, frame_number_item)
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
