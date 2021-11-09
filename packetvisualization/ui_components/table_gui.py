import os
import traceback

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMenu, QAction, QInputDialog, QTreeWidgetItem

from packetvisualization.backend_components import Wireshark
from packetvisualization.backend_components.table_backend import TableBackend
from packetvisualization.models.context.database_context import DbContext
from packetvisualization.models.dataset import Dataset
from packetvisualization.models.pcap import Pcap
from packetvisualization.ui_components import properties_gui


def gen_dictionary():
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
    def __init__(self, obj, progressbar, db: DbContext, workspace):
        super().__init__()
        self.icons = os.path.join(os.path.dirname(__file__), "images", "svg")
        self.backend = TableBackend()
        self.workspace = workspace
        self.obj = obj
        self.dict = gen_dictionary()
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
        try:
            menu = QMenu(self)

            self.tag_action = QAction("Add Tag", self)
            self.tag_action.triggered.connect(self.add_tag)

            self.remove_tag_action = QAction("Remove Tag", self)
            self.remove_tag_action.triggered.connect(self.remove_tag)

            # Analysis actions
            self.analyze_action = QAction("Selected Packets", self)
            self.analyze_action.triggered.connect(self.analyze)

            self.analyze_all_action = QAction("All Packets", self)
            self.analyze_all_action.triggered.connect(lambda: self.analyze(all_packets=True))

            self.analyze_tagged_action = QAction("Tagged Packets", self)
            self.analyze_tagged_action.triggered.connect(lambda: self.analyze(tagged=True))

            # Dataset Actions
            self.create_dataset_action = QAction("Selected Packets", self)
            self.create_dataset_action.triggered.connect(self.create_dataset)

            self.tagged_create_dataset_action = QAction("Tagged Packets", self)
            self.tagged_create_dataset_action.triggered.connect(lambda: self.create_dataset(tagged=True))

            self.all_dataset_action = QAction("All Packets", self)
            self.all_dataset_action.triggered.connect(self.create_dataset_from_all)

            # Text Transformation Actions
            self.viewASCII_action = QAction("ASCII", self)
            self.viewASCII_action.triggered.connect(self.view_as_ASCII)

            self.viewRAW_action = QAction("RAW", self)
            self.viewRAW_action.triggered.connect(self.view_as_RAW)

            self.viewText_action = QAction("Text", self)
            self.viewText_action.triggered.connect(self.view_as_text)

            # Wireshark Actions
            self.view_in_wireshark_action = QAction("Selected Packets", self)
            self.view_in_wireshark_action.triggered.connect(self.view_in_wireshark)

            self.view_tagged_in_wireshark_action = QAction("Tagged Packets", self)
            self.view_tagged_in_wireshark_action.triggered.connect(lambda: self.view_in_wireshark(tagged=True))

            self.view_all_in_wireshark_action = QAction("All Packets", self)
            self.view_all_in_wireshark_action.triggered.connect(lambda: self.view_in_wireshark(all_packets=True))

            menu.addAction(self.tag_action)
            menu.addAction(self.remove_tag_action)

            analysis_menu = menu.addMenu("Analyze...")
            analysis_menu.addAction(self.analyze_action)
            analysis_menu.addAction(self.analyze_tagged_action)
            analysis_menu.addAction(self.analyze_all_action)

            wireshark_menu = menu.addMenu("View in Wireshark from...")
            wireshark_menu.addAction(self.view_in_wireshark_action)
            wireshark_menu.addAction(self.view_tagged_in_wireshark_action)
            wireshark_menu.addAction(self.view_all_in_wireshark_action)

            dataset_menu = menu.addMenu("Create Dataset from...")
            dataset_menu.addAction(self.create_dataset_action)
            dataset_menu.addAction(self.tagged_create_dataset_action)
            dataset_menu.addAction(self.all_dataset_action)

            view_menu = menu.addMenu("Read as...")
            view_menu.addAction(self.viewASCII_action)
            view_menu.addAction(self.viewRAW_action)
            view_menu.addAction(self.viewText_action)

            menu.exec(event.globalPos())
        except:
            traceback.print_exc()

    def view_in_wireshark(self, tagged: bool = None, all_packets: bool = None):
        """Allows user to select packets from packet table for viewing in Wireshark
        """
        if all_packets:
            if type(self.obj) is Pcap:
                Wireshark.openwireshark(self.obj.path)
            else:
                Wireshark.openwireshark(self.obj.mergeFilePath)
            return True

        if not tagged:
            list = []
            if self.selectedItems():
                selected = self.selectedItems()
                row_list = []
                for item in selected:
                    if item.row() not in row_list:
                        frame_number = self.item(item.row(), 0).text()
                        list.append(frame_number)
                        row_list.append(item.row())

        if tagged:
            list = []
            tag = QInputDialog.getText(self, "Tag Name Entry", "Enter Tag name:")[0]
            for i in range(self.rowCount()):
                if tag in self.item(i, 0).data(Qt.UserRole)[1]:
                    list.append(self.item(i, 0).text())

        if len(list) > 0:
            if type(self.obj) == Pcap:
                infile = self.obj.path
            else:
                infile = self.obj.mergeFilePath

            frame_string_list = self.backend.gen_frame_string(list)
            temp_mergecap = self.backend.gen_pcap_from_frames(frame_string_list, infile, self.workspace.progressbar)
            Wireshark.openwireshark(temp_mergecap)

    def add_tag(self):
        """Allows user to add "tags" to packet items on the table gui. A user can add multiple tags to
            any packet item. Scroll over the tag icon to view a list of tags applied to that packet.
            """
        if self.selectedItems():
            selected = self.selectedItems()
            row_list = []
            tag = QInputDialog.getText(self, "Tag Name Entry", "Enter Tag name:")[0]
            for item in selected:
                if item.row() not in row_list and tag != "":
                    tag_list = self.item(item.row(), 0).data(Qt.UserRole)[1]
                    tag_list.append(tag)
                    packet_id = self.item(item.row(), 0).data(Qt.UserRole)[0]
                    self.item(item.row(), 0).setData(Qt.UserRole, [packet_id, tag_list])
                    self.item(item.row(), 0).setIcon(QIcon(os.path.join(self.icons, "pricetag.svg")))
                    tooltip = ""
                    for t in tag_list:
                        tooltip += t + " "
                    self.item(item.row(), 0).setToolTip(tooltip)
                    self.item(item.row(), 0).setStatusTip(tooltip)

                    row_list.append(item.row())

    def remove_tag(self):
        """User can remove all tags associated with selected packets.
        """
        if self.selectedItems():
            selected = self.selectedItems()
            row_list = []
            for item in selected:
                if item.row() not in row_list:
                    packet_id = self.item(item.row(), 0).data(Qt.UserRole)[0]
                    self.item(item.row(), 0).setData(Qt.UserRole, [packet_id, []])
                    self.item(item.row(), 0).setIcon(QIcon())
                    self.item(item.row(), 0).setStatusTip(None)
                    self.item(item.row(), 0).setToolTip(None)
                    row_list.append(item.row())

    def view_as_text(self):
        """User can view this packets field data in standard text. Cannot be applied
        to the "frame number" field.
        """
        if self.selectedItems():
            selected = self.selectedItems()
            for item in selected:
                if item.column() != 0:
                    if item.data(Qt.UserRole) is not None:
                        item.setText(item.data(Qt.UserRole))
                        self.resizeRowToContents(item.row())

    def view_as_RAW(self):
        """User can view this packets field data in raw hex. Cannot be applied
        to the "frame number" field.
        """
        if self.selectedItems():
            selected = self.selectedItems()
            for item in selected:
                if item.column() != 0:
                    if item.data(Qt.UserRole) is None:
                        text = item.text()
                        item.setData(Qt.UserRole, text)
                    else:
                        text = item.data(Qt.UserRole)
                    raw = self.backend.convert_to_raw(text)
                    item.setText(raw)
                    self.resizeRowToContents(item.row())

    def view_as_ASCII(self):
        """User can view this packets field data in ASCII. Cannot be applied
        to the "frame number" field.
        """
        if self.selectedItems():
            selected = self.selectedItems()
            for item in selected:
                if item.column() != 0:
                    if item.data(Qt.UserRole) is None:
                        text = item.text()
                        item.setData(Qt.UserRole, text)
                    else:
                        text = item.data(Qt.UserRole)
                    ascii_data = self.backend.convert_to_ascii(text)
                    item.setText(ascii_data)
                    self.resizeRowToContents(item.row())

    def create_dataset(self, tagged: bool = None):
        """Allows user to create a new dataset from selected or tagged packets.
            """
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
                if tag in self.item(i, 0).data(Qt.UserRole)[1]:
                    list.append(self.item(i, 0).text())

        if len(list) > 0:
            if type(self.obj) == Pcap:
                infile = self.obj.path
            else:
                infile = self.obj.mergeFilePath

            frame_string_list = self.backend.gen_frame_string(list)
            temp_mergecap = self.backend.gen_pcap_from_frames(frame_string_list, infile)

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
                    new_pcap = Pcap(file=temp_mergecap, path=dataset_object.path, name="sub_" + base + ".pcap")
                    dataset_object.add_pcap(new_pcap)
                    pcap_item = QTreeWidgetItem()
                    pcap_item.setText(0, new_pcap.name)
                    pcap_item.setData(0, Qt.UserRole, new_pcap)
                    child_item.addChild(pcap_item)

                    # Insert into Database
                    mytable = self.workspace.db[dataset_object.name]
                    self.workspace.eo.insert_packets(new_pcap.json_file, mytable, dataset_object.name,
                                                     new_pcap.name)

    def create_dataset_from_all(self):
        """Allows user to create a Dataset from all packets in a packet table
        """
        items = []
        for p in self.workspace.workspace_object.project:
            items.append(p.name)
        item, ok = QInputDialog.getItem(self, "Select Project",
                                        "List of Projects", items, 0, False)

        if type(self.obj) == Pcap:
            infile = self.obj.path
        else:
            infile = self.obj.mergeFilePath

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
                new_pcap = Pcap(file=infile, path=dataset_object.path, name=base + ".pcap")
                dataset_object.add_pcap(new_pcap)
                pcap_item = QTreeWidgetItem()
                pcap_item.setText(0, new_pcap.name)
                pcap_item.setData(0, Qt.UserRole, new_pcap)
                child_item.addChild(pcap_item)

                # Insert into Database
                mytable = self.workspace.db[dataset_object.name]
                self.workspace.eo.insert_packets(new_pcap.json_file, mytable, dataset_object.name,
                                                 new_pcap.name)

    def analyze(self, tagged: bool = None, all_packets: bool = None):
        """Initiates the analysis process from selected packets, all packets, or tagged packets
        """
        list = []
        data = ""
        row_list = []

        if all_packets:
            data = self.backend.query_pcap(self.obj, self.workspace.db)

        elif tagged:
            tag = QInputDialog.getText(self, "Tag Name Entry", "Enter Tag name:")[0]
            for i in range(self.rowCount()):
                if tag in self.item(i, 0).data(Qt.UserRole)[1]:
                    list.append(self.item(i, 0).data(Qt.UserRole)[0])
            data = self.backend.query_id(self.obj, self.workspace.db, list)

        else:
            if self.selectedItems():
                selected = self.selectedItems()
                for item in selected:
                    if item.row() not in row_list:
                        packet_id = self.item(item.row(), 0).data(Qt.UserRole)[0]
                        list.append(packet_id)
                        row_list.append(item.row())
                data = self.backend.query_id(self.obj, self.workspace.db, list)

        # for packet in data:
        #     print(packet)

        # self.ui = properties_gui.properties_window(data, self.obj, self.workspace.db, self.workspace)
        self.ui = properties_gui.properties_window(data, self.obj, self.workspace.db, self.workspace)
        self.ui.show()

    def populate_table(self, obj, progressbar, db):
        """Generates and populates a table of packets from the specified pcap or dataset
        """
        data = self.backend.query_pcap(obj, db)

        self.setRowCount(data.count())
        value = (100 / data.count())
        progressbar_value = 0
        progressbar.show()
        i = 0
        for packet in data:
            frame_number_item = QTableWidgetItem(str(i + 1))
            self.setItem(i, 0, frame_number_item)
            frame_number_item.setData(Qt.UserRole, [packet['_id'], []])
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
        """Updates the table column header labels to reflect the color (grey/black) and the
        count of the fields within each packet.
        """
        self.horizontalHeaderItem(0).setText("No. (" + str(self.dict["frame-number"]) + ")")
        self.horizontalHeaderItem(1).setText(
            "Time (" + str(self.dict["frame-time_relative"]) + ")")
        self.horizontalHeaderItem(2).setText("Source IP (" + str(self.dict["ip-src"]) + ")")
        self.horizontalHeaderItem(3).setText("Dest IP (" + str(self.dict["ip-dst"]) + ")")
        self.horizontalHeaderItem(4).setText("Source Port (" + str(self.dict["srcport"]) + ")")
        self.horizontalHeaderItem(5).setText("Dest Port (" + str(self.dict["dstport"]) + ")")
        self.horizontalHeaderItem(6).setText("Protocol (" + str(self.dict["frame-protocols"]) + ")")
        self.horizontalHeaderItem(7).setText("Length (" + str(self.dict["frame-len"]) + ")")
