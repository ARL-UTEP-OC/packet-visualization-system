import os
import shutil
import sys
import traceback
import zipfile

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QInputDialog, QMenu, QFileDialog, QAction, QMessageBox, QTreeWidget, QProgressBar, \
    QTableWidget

from packetvisualization.backend_components.entity_operator import EntityOperator
from packetvisualization.backend_components.load import Load
from packetvisualization.models import dataset
# from packetvisualization.backend.context.entities import EntityOperations
from packetvisualization.models.dataset import Dataset
from packetvisualization.models.pcap import Pcap
from packetvisualization.models.project import Project
from packetvisualization.models.workspace import Workspace
from packetvisualization.backend_components import Wireshark
from packetvisualization.ui_components.table_gui import table_gui



class Workspace_UI(QtWidgets.QMainWindow):
    def __init__(self, workspace_name: str, workspace_object: Workspace, test_mode: bool = False,
                 existing_flag: bool = False):
        # Workspace Constructor
        super(Workspace_UI, self).__init__()
        try:
            self.workspace_object = workspace_object
            self.test_mode = test_mode

            self.setFixedSize(917, 548)
            self.setWindowTitle(workspace_name)

            self.project_tree = QtWidgets.QTreeWidget()
            self.project_tree.setGeometry(QtCore.QRect(0, 60, 221, 261))
            self.project_tree.setHeaderLabels(["Item Name", "Size", "DoC"])

            self.analysis_tree = QtWidgets.QTreeWidget()
            self.analysis_tree.setGeometry(QtCore.QRect(0, 320, 221, 191))
            self.analysis_tree.setHeaderLabels(["Analysis", "Origin Dataset"])

            self.add_project_button = QtWidgets.QPushButton("Add a Project", clicked=lambda: self.add_project())
            self.add_project_button.setGeometry(QtCore.QRect(0, 22, 221, 41))

            self.add_pcap_button = QtWidgets.QPushButton("Add Pcap", clicked=lambda: self.add_pcap())
            self.add_pcap_button.setGeometry(QtCore.QRect(370, 22, 111, 31))

            self.add_dataset_button = QtWidgets.QPushButton("Add Dataset", clicked=lambda: self.add_dataset())
            self.add_dataset_button.setGeometry(QtCore.QRect(240, 22, 111, 31))

            self.open_in_wireshark_button = QtWidgets.QPushButton("Export to Wireshark",
                                                                  clicked=lambda: self.open_in_wireshark())
            self.open_in_wireshark_button.setGeometry(QtCore.QRect(500, 22, 111, 31))

            self.analyze_button = QtWidgets.QPushButton("Analyze", clicked=lambda: self.analyze())
            self.analyze_button.setGeometry(QtCore.QRect(630, 22, 111, 31))

            self.stack = QtWidgets.QStackedWidget()
            self.stack.setGeometry(QtCore.QRect(230, 55, 681, 490))

            self.tableWidget = table_gui()
            self.stack.addWidget(self.tableWidget)

            save_action = QAction("Save", self)
            save_action.triggered.connect(lambda: workspace_object.save())

            open_new_workspace_action = QAction("Open new Workspace", self)
            open_new_workspace_action.triggered.connect(lambda: self.open_new_workspace())

            open_existing_workspace_action = QAction("Open Existing Workspace", self)
            open_existing_workspace_action.triggered.connect(lambda: self.open_existing_workspace(self.test_mode))

            menu = self.menuBar()
            menu_file = menu.addMenu("File")
            menu_file.addAction(save_action)
            menu_file.addAction(open_new_workspace_action)
            menu_file.addAction(open_existing_workspace_action)

            self.setLayout(QtWidgets.QVBoxLayout())
            self.layout().addWidget(self.add_project_button)
            self.layout().addWidget(self.project_tree)
            self.layout().addWidget(self.analysis_tree)
            self.layout().addWidget(self.add_dataset_button)
            self.layout().addWidget(self.add_pcap_button)
            self.layout().addWidget(self.analyze_button)
            self.layout().addWidget(self.open_in_wireshark_button)
            self.layout().addWidget(self.stack)

            self.progress_bar = QProgressBar(self)
            self.progress_bar.setGeometry(15, 518, 221, 23)

            self.ent_operator = EntityOperator()

            if existing_flag:
                self.generate_existing_workspace()
        except:
            traceback.print_exc()

        self.show()

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        remove_project_action = context_menu.addAction("Remove Project")
        remove_dataset_action = context_menu.addAction("Remove Dataset")
        remove_pcap_action = context_menu.addAction("Remove PCAP")
        context_menu.addSeparator()
        convert_to_csv_action = context_menu.addAction("Convert Dataset to CSV")
        convert_to_json_action = context_menu.addAction("Convert Dataset to JSON")
        context_menu.addSeparator()
        add_pcap_folder_action = context_menu.addAction("Add Folder of PCAP's")
        add_pcap_zip_action = context_menu.addAction("Add zip Folder of PCAP's")

        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action == remove_project_action:
            self.remove_project()
        elif action == remove_dataset_action:
            self.remove_dataset()
        elif action == remove_pcap_action:
            self.remove_pcap()
        elif action == convert_to_csv_action:
            self.convert_dataset_to_csv()
        elif action == convert_to_json_action:
            self.convert_dataset_to_json()
        elif action == add_pcap_folder_action:
            self.add_pcap_folder()
        elif action == add_pcap_zip_action:
            self.add_pcap_zip()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Workspace Close", "Would you like to save this Workspace?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.workspace_object.save()
            self.workspace_object.__del__()
            event.accept()
        else:
            self.workspace_object.__del__()
            event.accept()

    def add_project(self, text=None):
        if self.test_mode == False:
            text = QInputDialog.getText(self, "Project Name Entry", "Enter Project name:")[0]
        if not self.project_tree.findItems(text, QtCore.Qt.MatchRecursive, 0):
            project = Project(name=text, parent_path=self.workspace_object.path)
            self.workspace_object.add_project(project)
            item = QtWidgets.QTreeWidgetItem(self.project_tree)
            item.setData(0, QtCore.Qt.UserRole, project)
            item.setText(0, text)
            return True
        else:
            print("Item named " + text + " already exists")
            return False

    def remove_project(self, project=None):
        if self.project_tree.selectedItems() and type(
                self.project_tree.selectedItems()[0].data(0, QtCore.Qt.UserRole)) is Project or self.test_mode == True:
            if not self.test_mode:
                project = self.project_tree.selectedItems()[0]
            p = project.data(0, QtCore.Qt.UserRole)
            self.workspace_object.del_project(p)
            QTreeWidget.invisibleRootItem(self.project_tree).removeChild(project)
            return True
        else:
            return False

    def add_dataset(self, text=None, file=None, project=None):
        try:
            pcap_path = ""
            pcap_name = ""
            if self.project_tree.selectedItems() and type(self.project_tree.selectedItems()[0].data(0,
                                                                                                    QtCore.Qt.UserRole)) is Project or self.test_mode == True:
                if not self.test_mode:
                    text = QInputDialog.getText(self, "Dataset Name Entry", "Enter Dataset name:")[0]
                if not self.project_tree.findItems(text, QtCore.Qt.MatchRecursive, 0) and text != "":
                    if not self.test_mode:
                        pcap_path, pcap_name, file, extension = self.get_pcap_path()
                    else:
                        pcap_path, pcap_name = os.path.split(file)
                    if pcap_path is None:
                        return False
                    if not self.test_mode:
                        project = self.project_tree.selectedItems()[0]

                    p = project.data(0, QtCore.Qt.UserRole)
                    # dataset = Dataset(name=text, parentPath=p.path)

                    # ent_operator = EntityOperations()

                    db_dataset = datasetEnt(name=text, path=p.path)
                    self.ent_operator.insert_dataset(db_dataset)
                    # db_dataset.create_folder()
                    # db_dataset.create_merge_file()

                    p.add_dataset(db_dataset)
                    child_item = QtWidgets.QTreeWidgetItem()
                    child_item.setText(0, text)
                    child_item.setData(0, QtCore.Qt.UserRole, db_dataset)

                    project.addChild(child_item)

                    # new_pcap = Pcap(file=file, path=dataset.path, name=pcap_name)
                    db_pcap = pcapEnt(name=pcap_name, path=db_dataset.path, pcap_file=file, parentKey=db_dataset.id)
                    # ent_operator.insert_pcap(db_pcap)
                    if db_pcap.name is not None:
                        self.ent_operator.insert_pcap(db_pcap)
                        # dataset.add_pcap(new=db_pcap)
                        pcap_item = QtWidgets.QTreeWidgetItem()
                        pcap_item.setText(0, pcap_name)
                        pcap_item.setData(0, QtCore.Qt.UserRole, db_pcap)
                        child_item.addChild(pcap_item)
                    else:
                        child_item.parent().removeChild(child_item)
                        p.del_dataset(db_dataset)
                    return True
                else:
                    return False
        except:
            print(traceback.print_exc())
            return False

    def remove_dataset(self, dataset_item=None):
        if self.project_tree.selectedItems() and type(
                self.project_tree.selectedItems()[0].data(0,
                                                          QtCore.Qt.UserRole)) is datasetEnt or self.test_mode == True:
            if not self.test_mode:
                dataset_item = self.project_tree.selectedItems()[0]
            d = dataset_item.data(0, QtCore.Qt.UserRole)
            for p in self.workspace_object.project:
                for d in p.dataset:
                    if d.name == dataset_item.text(0):
                        self.ent_operator.remove_dataset(d)
                        p.del_dataset(old=d)
                        dataset_item.parent().removeChild(dataset_item)
                        return True
            return False

    def add_pcap(self, dataset_item=None, file=None):
        try:
            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0, QtCore.Qt.UserRole)) is datasetEnt or self.test_mode:

                if not self.test_mode:
                    pcap_path, pcap_name, file, extension = self.get_pcap_path()
                else:
                    pcap_path, pcap_name = os.path.split(file)
                if pcap_path is None:
                    return False
                if not self.test_mode:
                    dataset_item = self.project_tree.selectedItems()[0]

                d = dataset_item.data(0, QtCore.Qt.UserRole)
                # new_pcap = Pcap(file=file, path=d.path, name=pcap_name)
                new_pcap = pcapEnt(name=pcap_name, path=d.path, pcap_file=file, parentKey=d.id)

                if new_pcap.name is not None and new_pcap not in d.pcaps:
                    # d.add_pcap(new_pcap)
                    self.ent_operator.insert_pcap(new_pcap)
                    pcap_item = QtWidgets.QTreeWidgetItem()
                    pcap_item.setText(0, pcap_name)
                    pcap_item.setData(0, QtCore.Qt.UserRole, new_pcap)
                    dataset_item.addChild(pcap_item)

                    return True
                return False
        except:
            traceback.print_exc()
            print("Error loading this pcap")

    def add_pcap_zip(self):
        try:
            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0, QtCore.Qt.UserRole)) is datasetEnt or self.test_mode:

                location = QFileDialog.getOpenFileName(caption="Select zip Folder of PCAP's", filter="zip (*.zip)")[0]
                dataset_item = self.project_tree.selectedItems()[0]
                dataset_obj = self.project_tree.selectedItems()[0].data(0, QtCore.Qt.UserRole)
                extracted_folder = os.path.join(os.path.dirname(location), "ExtractedPV")
                with zipfile.ZipFile(location, 'r') as my_zip:
                    my_zip.extractall(extracted_folder)

                for file in os.listdir(extracted_folder):
                    # new_pcap = Pcap(file, dataset_obj.path, os.path.join(extracted_folder, file))
                    new_pcap = pcapEnt(name=file, path=dataset_obj.path, pcap_file=os.path.join(extracted_folder, file),
                                       parentKey=dataset_obj.id)
                    # dataset_obj.add_pcap(new_pcap)
                    pcap_item = QtWidgets.QTreeWidgetItem()
                    pcap_item.setText(0, os.path.basename(file))
                    pcap_item.setData(0, QtCore.Qt.UserRole, new_pcap)
                    dataset_item.addChild(pcap_item)

                shutil.rmtree(extracted_folder)
                return True
        except:
            traceback.print_exc()

    def add_pcap_folder(self):
        try:
            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0, QtCore.Qt.UserRole)) is datasetEnt or self.test_mode:

                location = QFileDialog.getExistingDirectory(caption="Select Folder of PCAP's")
                dataset_item = self.project_tree.selectedItems()[0]
                dataset = self.project_tree.selectedItems()[0].data(0, QtCore.Qt.UserRole)
                for file in os.listdir(location):
                    # new_pcap = Pcap(file, dataset.path, os.path.join(location, file))
                    new_pcap = pcapEnt(name=file, path=dataset.path, pcap_file=os.path.join(location, file),
                                       parentKey=dataset.id)
                    # dataset.add_pcap(new_pcap)
                    pcap_item = QtWidgets.QTreeWidgetItem()
                    pcap_item.setText(0, os.path.basename(file))
                    pcap_item.setData(0, QtCore.Qt.UserRole, new_pcap)
                    dataset_item.addChild(pcap_item)
                return True
        except:
            traceback.print_exc()

    def remove_pcap(self, pcap_item=None):
        try:
            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0,
                                                              QtCore.Qt.UserRole)) is pcapEnt or self.test_mode == True:
                if not self.test_mode:
                    pcap_item = self.project_tree.selectedItems()[0]

                for p in self.workspace_object.project:
                    for d in p.dataset:
                        for cap in d.pcaps:
                            if cap.name == pcap_item.text(0):
                                self.ent_operator.remove_pcap(cap)
                                d.del_pcap(cap)
                                pcap_item.parent().removeChild(pcap_item)
                                return True
                return False
        except:
            traceback.print_exc()
            return False

    def analyze(self):
        if self.project_tree.selectedItems() and type(
                self.project_tree.selectedItems()[0].data(0,
                                                          QtCore.Qt.UserRole)) is datasetEnt or self.test_mode == True:
            if not self.test_mode:
                text = QInputDialog.getText(self, "Analysis Name Entry", "Enter Analysis name:")[0]
            analysis_item = QtWidgets.QTreeWidgetItem(self.analysis_tree)
            analysis_item.setText(0, text)
            return True

    def remove_analysis(self):
        return

    def open_in_wireshark(self, pcap_item=None, dataset_item=None, merge_flag=False):
        try:
            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0, QtCore.Qt.UserRole)) is datasetEnt or (
                    self.test_mode == True and merge_flag == True):
                if not self.test_mode:
                    dataset_item = self.project_tree.selectedItems()[0]
                d = dataset_item.data(0, QtCore.Qt.UserRole)
                Wireshark.openwireshark(d.mergeFilePath)
                return True

            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0,
                                                              QtCore.Qt.UserRole)) is pcapEnt or self.test_mode == True:
                if not self.test_mode:
                    pcap_item = self.project_tree.selectedItems()[0]
                cap = pcap_item.data(0, QtCore.Qt.UserRole)
                if self.test_mode:
                    return True
                Wireshark.openwireshark(cap.pcap_file)
            else:
                return False
        except:
            traceback.print_exc()
            return False

    def convert_dataset_to_csv(self):
        try:
            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0,
                                                              QtCore.Qt.UserRole)) is datasetEnt or self.test_mode == True:
                dataset_item = self.project_tree.selectedItems()[0]
                dataset = dataset_item.data(0, QtCore.Qt.UserRole)
                dataset_file = dataset.mergeFilePath

                output_file = QFileDialog.getSaveFileName(caption="Choose Output location", filter=".csv (*.csv)")[0]

                os.system(
                    'cd "C:\Program Files\Wireshark" & tshark -r ' + dataset_file + ' -T fields -e frame.number -e '
                                                                                    'ip.src -e ip.dst '
                                                                                    '-e frame.len -e frame.time -e '
                                                                                    'frame.time_relative -e _ws.col.Info '
                                                                                    '-E header=y -E '
                                                                                    'separator=, -E quote=d -E '
                                                                                    'occurrence=f > ' + output_file)
                return True
        except:
            traceback.print_exc()

    def convert_dataset_to_json(self):
        try:
            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0,
                                                              QtCore.Qt.UserRole)) is datasetEnt or self.test_mode == True:
                dataset_item = self.project_tree.selectedItems()[0]
                dataset = dataset_item.data(0, QtCore.Qt.UserRole)
                dataset_file = dataset.mergeFilePath

                output_file = QFileDialog.getSaveFileName(caption="Choose Output location", filter=".json (*.json)")[0]

                os.system('cd "C:\Program Files\Wireshark" & tshark -r ' + dataset_file + ' -T json > ' + output_file)
                return True
        except:
            traceback.print_exc()

    def get_pcap_path(self, full_path: str = None):
        file_filter = "Wireshark capture file (*.pcap)"
        initial_filter = "Wireshark capture file (*.pcap)"
        if not self.test_mode:
            full_path = QFileDialog.getOpenFileName(caption="Add a Pcap file to this Dataset", filter=file_filter,
                                                    initialFilter=initial_filter)[0]

        if full_path != "":
            name = os.path.basename(full_path)
            path = os.path.dirname(full_path)
            extension = os.path.splitext(full_path)[1]
            return path, name, full_path, extension
        else:
            return None, None, full_path

    def open_new_workspace(self, file=None):
        try:
            if not self.test_mode:
                file = QFileDialog.getSaveFileName(caption="Choose Workspace location")[0]

            if file != '':
                new_workspace_object = Workspace(name=os.path.basename(file), location=os.path.dirname(file))
                self.workspace = Workspace_UI(os.path.basename(file), new_workspace_object)
                self.workspace.show()
                return True
        except:
            traceback.print_exc()
            return False

    def open_existing_workspace(self, test_mode: bool, file=None):
        try:
            if not test_mode:
                file_filter = "zip(*.zip)"
                file = QFileDialog.getOpenFileName(caption="Open existing Workspace", filter=file_filter)[0]

                if file != "":
                    if not test_mode:
                        workspace_object = Load().open_zip(file)

                        workspaceUI = Workspace_UI(workspace_object.name, workspace_object, existing_flag=True)
                        workspaceUI.show()
                        return True
        except:
            traceback.print_exc()
            return False

    def generate_existing_workspace(self):
        for p in self.workspace_object.project:
            project_item = QtWidgets.QTreeWidgetItem(self.project_tree)
            project_item.setText(0, p.name)
            project_item.setData(0, QtCore.Qt.UserRole, p)
            for d in p.dataset:
                dataset_item = QtWidgets.QTreeWidgetItem()
                dataset_item.setText(0, d.name)
                dataset_item.setData(0, QtCore.Qt.UserRole, d)
                project_item.addChild(dataset_item)
                for cap in d.pcaps:
                    pcap_item = QtWidgets.QTreeWidgetItem()  # Need to link to list of pcaps
                    pcap_item.setText(0, cap.name)
                    dataset_item.addChild(pcap_item)
        return True
