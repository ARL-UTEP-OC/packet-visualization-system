import os
import shutil
import traceback

from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMenu, QAction, QInputDialog, QTreeWidgetItem, QFileDialog

from packetvisualization.backend_components import Wireshark
from packetvisualization.backend_components.table_backend import TableBackend
from packetvisualization.models.context.database_context import DbContext
from packetvisualization.models.dataset import Dataset
from packetvisualization.models.pcap import Pcap
from packetvisualization.ui_components import properties_gui


def gen_dictionary():
    """Creates a dictionary that stores the count of how many times a field appears in a packet
    """
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
        self.backend = TableBackend()
        self.workspace = workspace
        self.progressbar = progressbar
        self.obj = obj
        self.thread_is_free = True
        self.dict = gen_dictionary()
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels(
            ["No.", "Time", "Source IP", "Destination IP", "srcport", "dstport", "Protocol", "Length"])
        self.verticalHeader().hide()
        fnt = QFont()
        fnt.setPointSize(11)
        fnt.setBold(True)
        self.horizontalHeader().setFont(fnt)

        self.populate_table()

    def contextMenuEvent(self, event):
        """Creates the right-click menu for accessing table functionality
        """
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

            # Export Actions
            self.to_csv_selected_action = QAction("Selected Packets", self)
            self.to_csv_selected_action.triggered.connect(self.export_to_csv)

            self.to_csv_tagged_action = QAction("Tagged Packets", self)
            self.to_csv_tagged_action.triggered.connect(lambda: self.export_to_csv(tagged=True))

            self.to_csv_all_action = QAction("All Packets", self)
            self.to_csv_all_action.triggered.connect(lambda: self.export_to_csv(all_packets=True))

            self.to_json_selected_action = QAction("Selected Packets", self)
            self.to_json_selected_action.triggered.connect(self.export_to_json)

            self.to_json_tagged_action = QAction("Tagged Packets", self)
            self.to_json_tagged_action.triggered.connect(lambda: self.export_to_json(tagged=True))

            self.to_json_all_action = QAction("All Packets", self)
            self.to_json_all_action.triggered.connect(lambda: self.export_to_json(all_packets=True))

            self.to_pcap_selected_action = QAction("Selected Packets", self)
            self.to_pcap_selected_action.triggered.connect(self.export_to_pcap)

            self.to_pcap_tagged_action = QAction("Tagged Packets", self)
            self.to_pcap_tagged_action.triggered.connect(lambda: self.export_to_pcap(tagged=True))

            self.to_pcap_all_action = QAction("All Packets", self)
            self.to_pcap_all_action.triggered.connect(lambda: self.export_to_pcap(all_packets=True))

            menu.addAction(self.tag_action)
            menu.addAction(self.remove_tag_action)

            if type(self.obj) is Dataset:
                analysis_menu = menu.addMenu("Analyze")
                analysis_menu.addAction(self.analyze_action)
                analysis_menu.addAction(self.analyze_tagged_action)
                analysis_menu.addAction(self.analyze_all_action)

            export_menu = menu.addMenu("Export")
            csv_menu = export_menu.addMenu("To CSV from...")
            csv_menu.addAction(self.to_csv_selected_action)
            csv_menu.addAction(self.to_csv_tagged_action)
            csv_menu.addAction(self.to_csv_all_action)
            json_menu = export_menu.addMenu("To JSON from...")
            json_menu.addAction(self.to_json_selected_action)
            json_menu.addAction(self.to_json_tagged_action)
            json_menu.addAction(self.to_json_all_action)
            pcap_menu = export_menu.addMenu("To PCAP from...")
            pcap_menu.addAction(self.to_pcap_selected_action)
            pcap_menu.addAction(self.to_pcap_tagged_action)
            pcap_menu.addAction(self.to_pcap_all_action)

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
        """Starts a thread that allows user to select packets from packet table for viewing in Wireshark
        """
        if self.selectedItems() and self.thread_is_free:
            self.thread_is_free = False

            self.thread = QThread()

            if tagged:
                tag = QInputDialog.getText(self, "Tag Name Entry", "Enter Tag name:")[0]
                self.worker = table_worker(table=self, selected=self.selectedItems(), tagged=tagged, tag=tag)
            else:
                self.worker = table_worker(table=self, selected=self.selectedItems(), all_packets=all_packets)

            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.create_pcap_for_wireshark)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.progress.connect(self.update_progressbar)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

            self.thread.finished.connect(self.free_thread)

    def export_to_pcap(self, tagged: bool = None, all_packets: bool = None):
        """Starts a thread that allows user to export packets to a PCAP file
        """
        if self.selectedItems() and self.thread_is_free:
            self.thread_is_free = False

            output_file = QFileDialog.getSaveFileName(caption="Choose Output location", filter="Wireshark capture "
                                                                                               "file (*.pcap)")[0]

            if tagged:
                tag = QInputDialog.getText(self, "Tag Name Entry", "Enter Tag name:")[0]
                self.worker = table_worker(table=self, selected=self.selectedItems(), tagged=tagged, tag=tag,
                                           all_packets=all_packets, output_file=output_file)
            else:
                self.worker = table_worker(table=self, selected=self.selectedItems(), tagged=tagged,
                                           all_packets=all_packets, output_file=output_file)

            self.thread = QThread()

            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.create_pcap)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.progress.connect(self.update_progressbar)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

            self.thread.finished.connect(self.free_thread)

    def free_thread(self):
        """Signals to other threads that the table thread is free to use
        """
        self.thread_is_free = True

    def export_to_json(self, tagged: bool = None, all_packets: bool = None):
        """Starts a thread that allows user to export packets to JSON format
        """
        if self.selectedItems() and self.thread_is_free:
            self.thread_is_free = False

            output_file = QFileDialog.getSaveFileName(caption="Choose Output location", filter=".json (*.json)")[0]

            if tagged:
                tag = QInputDialog.getText(self, "Tag Name Entry", "Enter Tag name:")[0]
                self.worker = table_worker(table=self, selected=self.selectedItems(), tagged=tagged, tag=tag,
                                           all_packets=all_packets, output_file=output_file)
            else:
                self.worker = table_worker(table=self, selected=self.selectedItems(), tagged=tagged,
                                           all_packets=all_packets, output_file=output_file)

            self.thread = QThread()

            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.create_pcap_for_json)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.progress.connect(self.update_progressbar)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

            self.thread.finished.connect(self.free_thread)

    def export_to_csv(self, tagged: bool = None, all_packets: bool = None):
        """Starts a thread that allows user to export packets to CSV format
        """
        if self.selectedItems() and self.thread_is_free:
            self.thread_is_free = False

            output_file = QFileDialog.getSaveFileName(caption="Choose Output location", filter=".csv (*.csv)")[
                0]

            if tagged:
                tag = QInputDialog.getText(self, "Tag Name Entry", "Enter Tag name:")[0]
                self.worker = table_worker(table=self, selected=self.selectedItems(), tagged=tagged, tag=tag,
                                           all_packets=all_packets, output_file=output_file)
            else:
                self.worker = table_worker(table=self, selected=self.selectedItems(), tagged=tagged,
                                           all_packets=all_packets, output_file=output_file)

            self.thread = QThread()

            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.create_pcap_for_csv)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.progress.connect(self.update_progressbar)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

            self.thread.finished.connect(self.free_thread)

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
                    self.item(item.row(), 0).setIcon(QIcon(":pricetag.svg"))
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

    def update_progressbar(self, n: int):
        """Receives signal to update the progress bar from threaded tasks
        """
        self.progressbar.setValue(n)

    def update_merge_cap(self, mergecap):
        """Receives signal to update the temp mergecap for the use of adding a dataset
        """
        self.mergecap = mergecap[0]

    def create_dataset(self, tagged: bool = None):
        """Starts a thread that allows user to create a new dataset from selected or tagged packets.
        """
        if self.selectedItems() and self.thread_is_free:
            self.thread_is_free = False
            try:
                self.thread = QThread()

                if tagged:
                    tag = QInputDialog.getText(self, "Tag Name Entry", "Enter Tag name:")[0]
                    self.worker = table_worker(table=self, selected=self.selectedItems(), tagged=tagged, tag=tag)
                else:
                    self.worker = table_worker(table=self, selected=self.selectedItems())

                self.worker.moveToThread(self.thread)

                self.thread.started.connect(self.worker.create_pcap_for_dataset)
                self.worker.finished.connect(self.thread.quit)
                self.worker.finished.connect(self.worker.deleteLater)
                self.worker.progress.connect(self.update_progressbar)
                self.worker.merge_cap.connect(self.update_merge_cap)
                self.thread.finished.connect(self.thread.deleteLater)

                self.thread.start()

                self.thread.finished.connect(self.add_dataset_to_project_tree)
                self.thread.finished.connect(self.free_thread)
            except:
                traceback.print_exc()

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
                dataset_object = Dataset(name=text, parent_path=project_object.path)
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

        self.ui = properties_gui.properties_window(data, self.obj, self.workspace.db, self.workspace)
        self.ui.show()

    def populate_table(self):
        """Starts a thread that generates and populates a table of packets from the specified pcap or dataset
        """
        if self.thread_is_free:
            self.thread_is_free = False

            self.thread = QThread()
            self.worker = table_worker(table=self)

            self.thread.started.connect(self.worker.create_table)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.progress.connect(self.update_progressbar)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

            self.thread.finished.connect(self.free_thread)

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

    def add_dataset_to_project_tree(self):
        """Adds temp mergecap to the designated dataset in the designated project in the
        project tree of the workspace
        """
        temp_mergecap = self.mergecap
        items = []
        for p in self.workspace.workspace_object.project:
            items.append(p.name)

        item, ok = QInputDialog.getItem(self, "Select Project",
                                        "List of Projects", items, 0, False)

        if ok and item:
            text = QInputDialog.getText(self, "Dataset Name Entry", "Enter Dataset name:")[0]
            project_item = self.workspace.project_tree.findItems(item, Qt.MatchRecursive, 0)[0]
            project_object = project_item.data(0, Qt.UserRole)

            if text and not self.workspace.project_tree.findItems(text, Qt.MatchRecursive, 0):
                # Add Project and Dataset object && project tree item
                dataset_object = Dataset(name=text, parent_path=project_object.path)
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
                self.workspace.eo.insert_packets(new_pcap.json_file, mytable, dataset_object.name, new_pcap.name)


class table_worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    merge_cap = pyqtSignal(list)

    def __init__(self, table: table_gui, selected=None, tagged: bool = False, all_packets: bool = None, tag: str = None,
                 output_file=None):
        super().__init__()
        self.table = table
        self.selected = selected
        self.tagged = tagged
        self.all_packets = all_packets
        self.tag = tag
        self.output_file = output_file

    def create_pcap(self):
        """Creates a pcap from selected packets in the table
        """
        all_packets = self.all_packets
        tagged = self.tagged
        tag = self.tag
        output_file = self.output_file
        selected = self.selected
        name = os.path.basename(output_file)

        if all_packets:
            if type(self.table.obj) is Pcap:
                shutil.copy(self.table.obj.path, output_file)
            elif type(self.table.obj) is Dataset:
                shutil.copy(self.table.obj.mergeFilePath, output_file)
            return True

        if not tagged:
            list = []
            row_list = []
            for item in selected:
                if item.row() not in row_list:
                    frame_number = self.table.item(item.row(), 0).text()
                    list.append(frame_number)
                    row_list.append(item.row())

        if tagged:
            list = []
            for i in range(self.table.rowCount()):
                if tag in self.table.item(i, 0).data(Qt.UserRole)[1]:
                    list.append(self.table.item(i, 0).text())

        if len(list) > 0:
            if type(self.table.obj) == Pcap:
                infile = self.table.obj.path
            else:
                infile = self.table.obj.mergeFilePath

            frame_string_list = self.table.backend.gen_frame_string(list)
            temp_mergecap = self.table.backend.gen_pcap_from_frames(frame_string_list, infile,
                                                                    self.table.workspace.progressbar, self.progress)

            if output_file != "":
                shutil.copy(temp_mergecap, output_file)

        self.finished.emit()

    def create_pcap_for_json(self):
        """Creates a pcap from selected packets and then exports it to a JSON file
        """
        all_packets = self.all_packets
        tagged = self.tagged
        tag = self.tag
        output_file = self.output_file
        selected = self.selected

        if all_packets:
            if type(self.table.obj) is Pcap:
                self.table.backend.to_json(output_file, self.obj.path)
            elif type(self.table.obj) is Dataset:
                self.table.backend.to_json(output_file, self.table.obj.mergeFilePath)
            return True

        if not tagged:
            list = []
            row_list = []
            for item in selected:
                if item.row() not in row_list:
                    frame_number = self.table.item(item.row(), 0).text()
                    list.append(frame_number)
                    row_list.append(item.row())

        if tagged:
            list = []
            for i in range(self.table.rowCount()):
                if tag in self.table.item(i, 0).data(Qt.UserRole)[1]:
                    list.append(self.table.item(i, 0).text())

        if len(list) > 0:
            if type(self.table.obj) == Pcap:
                infile = self.table.obj.path
            else:
                infile = self.table.obj.mergeFilePath

            frame_string_list = self.table.backend.gen_frame_string(list)
            temp_mergecap = self.table.backend.gen_pcap_from_frames(frame_string_list, infile,
                                                                    self.table.workspace.progressbar, self.progress)

            if output_file != "":
                self.table.backend.to_json(output_file, temp_mergecap)

        self.finished.emit()

    def create_pcap_for_csv(self):
        """Creates a pcap from selected packets and then exports it to a CSV file
        """
        all_packets = self.all_packets
        tagged = self.tagged
        tag = self.tag
        output_file = self.output_file
        selected = self.selected

        if all_packets:
            if type(self.table.obj) is Pcap:
                self.table.backend.to_csv(output_file, self.obj.path)
            elif type(self.table.obj) is Dataset:
                self.table.backend.to_csv(output_file, self.table.obj.mergeFilePath)
            return True

        if not tagged:
            list = []
            row_list = []
            for item in selected:
                if item.row() not in row_list:
                    frame_number = self.table.item(item.row(), 0).text()
                    list.append(frame_number)
                    row_list.append(item.row())

        if tagged:
            list = []
            for i in range(self.table.rowCount()):
                if tag in self.table.item(i, 0).data(Qt.UserRole)[1]:
                    list.append(self.table.item(i, 0).text())

        if len(list) > 0:
            if type(self.table.obj) == Pcap:
                infile = self.table.obj.path
            else:
                infile = self.table.obj.mergeFilePath

            frame_string_list = self.table.backend.gen_frame_string(list)
            temp_mergecap = self.table.backend.gen_pcap_from_frames(frame_string_list, infile,
                                                                    self.table.workspace.progressbar, self.progress)

            if output_file != "":
                self.table.backend.to_csv(output_file, temp_mergecap)

        self.finished.emit()

    def create_pcap_for_wireshark(self):
        """Creates a pcap from selected packets and then opens the pcap in Wireshark
        """
        table = self.table
        selected = self.selected
        tagged = self.tagged
        all_packets = self.all_packets
        tag = self.tag

        try:
            if all_packets:
                if type(table.obj) is Pcap:
                    Wireshark.openwireshark(table.obj.path)
                else:
                    Wireshark.openwireshark(table.obj.mergeFilePath)
                return True

            if not tagged:
                list = []
                if selected:
                    row_list = []
                    for item in selected:
                        if item.row() not in row_list:
                            frame_number = table.item(item.row(), 0).text()
                            list.append(frame_number)
                            row_list.append(item.row())

            if tagged:
                list = []
                for i in range(table.rowCount()):
                    if tag in table.item(i, 0).data(Qt.UserRole)[1]:
                        list.append(table.item(i, 0).text())

            if len(list) > 0:
                if type(table.obj) == Pcap:
                    infile = table.obj.path
                else:
                    infile = table.obj.mergeFilePath

                frame_string_list = table.backend.gen_frame_string(list)
                temp_mergecap = table.backend.gen_pcap_from_frames(frame_string_list, infile, table.progressbar,
                                                                   self.progress)
                Wireshark.openwireshark(temp_mergecap)

            self.finished.emit()
        except:
            traceback.print_exc()

    def create_pcap_for_dataset(self):
        """Creates a pcap from selected packets and then allows for adding that pcap to a dataset
        """
        table = self.table
        selected = self.selected
        tagged = self.tagged
        tag = self.tag

        try:
            list = []
            if not tagged:
                row_list = []
                for item in selected:
                    if item.row() not in row_list:
                        frame_number = table.item(item.row(), 0).text()
                        list.append(frame_number)
                        row_list.append(item.row())

            if tagged:
                for i in range(table.rowCount()):
                    if tag in table.item(i, 0).data(Qt.UserRole)[1]:
                        list.append(table.item(i, 0).text())

            if len(list) > 0:
                if type(table.obj) == Pcap:
                    infile = table.obj.path
                else:
                    infile = table.obj.mergeFilePath

                frame_string_list = table.backend.gen_frame_string(list)
                temp_mergecap = table.backend.gen_pcap_from_frames(frame_string_list, infile, table.progressbar,
                                                                   self.progress)

            self.merge_cap.emit([temp_mergecap])
            self.finished.emit()
        except:
            traceback.print_exc()

    def create_table(self):
        """Populates the table from a database query of the individual packets contained in a pcap
        """
        obj = self.table.obj
        progressbar = self.table.progressbar
        db = self.table.workspace.db

        data = self.table.backend.query_pcap(obj, db)
        self.table.setRowCount(data.count())
        value = (100 / data.count())
        progressbar_value = 0
        progressbar.show()

        i = 0
        for packet in data:
            frame_number_item = QTableWidgetItem(str(i + 1))
            self.table.setItem(i, 0, frame_number_item)
            frame_number_item.setData(Qt.UserRole, [packet['_id'], []])
            self.table.dict["frame-number"] += 1
            self.table.setItem(i, 1, QTableWidgetItem(packet['_source']['layers']['frame'].get('frame-time_relative')))
            self.table.dict["frame-time_relative"] += 1

            if packet['_source']['layers'].get('ip') is not None:
                self.table.setItem(i, 2, QTableWidgetItem(packet['_source']['layers'].get('ip').get('ip-src')))
                self.table.dict["ip-src"] += 1
                self.table.setItem(i, 3, QTableWidgetItem(packet['_source']['layers'].get('ip').get('ip-dst')))
                self.table.dict["ip-dst"] += 1
            else:
                self.table.setItem(i, 2, QTableWidgetItem(None))
                self.table.setItem(i, 3, QTableWidgetItem(None))
                self.table.horizontalHeaderItem(2).setForeground(QColor(175, 175, 175))
                self.table.horizontalHeaderItem(3).setForeground(QColor(175, 175, 175))

            if packet['_source']['layers'].get('udp') is not None:
                self.table.setItem(i, 4, QTableWidgetItem(packet['_source']['layers'].get('udp').get('udp-srcport')))
                self.table.dict["srcport"] += 1
                self.table.setItem(i, 5, QTableWidgetItem(packet['_source']['layers'].get('udp').get('udp-dstport')))
                self.table.dict["dstport"] += 1
            elif packet['_source']['layers'].get('tcp') is not None:
                self.table.setItem(i, 4, QTableWidgetItem(packet['_source']['layers'].get('tcp').get('tcp-srcport')))
                self.table.dict["srcport"] += 1
                self.table.setItem(i, 5, QTableWidgetItem(packet['_source']['layers'].get('tcp').get('tcp-dstport')))
                self.table.dict["dstport"] += 1
            else:
                self.table.setItem(i, 4, QTableWidgetItem(None))
                self.table.setItem(i, 5, QTableWidgetItem(None))
                self.table.horizontalHeaderItem(4).setForeground(QColor(175, 175, 175))
                self.table.horizontalHeaderItem(5).setForeground(QColor(175, 175, 175))

            protocols = packet['_source']['layers']['frame'].get('frame-protocols')
            self.table.setItem(i, 6, QTableWidgetItem(protocols.split(':')[-1].upper()))
            self.table.dict["frame-protocols"] += 1

            self.table.setItem(i, 7, QTableWidgetItem(packet['_source']['layers']['frame'].get('frame-len')))
            self.table.dict["frame-len"] += 1

            i += 1
            progressbar_value = progressbar_value + value
            self.progress.emit(progressbar_value)

        self.table.update_lables()
        self.table.resizeColumnsToContents()
        self.progress.emit(0)
        progressbar.hide()
        self.finished.emit()
