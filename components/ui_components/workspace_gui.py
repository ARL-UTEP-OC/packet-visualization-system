import os
import sys
import traceback
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QInputDialog, QMenu, QFileDialog, QAction, QMessageBox, QTreeWidget

from components.models.dataset import Dataset
from components.models.pcap import Pcap
from components.models.project import Project
from components.models.workspace import Workspace
from components.backend_components import Wireshark

class Workspace_UI(QtWidgets.QMainWindow):
    def __init__(self, workspace_name: str, workspace_object: Workspace, test_mode:bool = False, existing_flag:bool = False):
        # Workspace Constructor
        super(Workspace_UI, self).__init__()
        try:
            self.workspace_object = workspace_object
            self.test_mode = test_mode

            self.setFixedSize(917, 548)
            self.setWindowTitle(workspace_name)

            self.project_tree = QtWidgets.QTreeWidget()
            self.project_tree.setGeometry(QtCore.QRect(0, 62, 221, 451))
            self.project_tree.setHeaderLabels(["Project(s) Name", "Size", "DoC"])

            self.add_project_button = QtWidgets.QPushButton("Add a Project", clicked=lambda: self.add_project())
            self.add_project_button.setGeometry(QtCore.QRect(0, 22, 221, 41))

            self.add_pcap_button = QtWidgets.QPushButton("Add Pcap", clicked=lambda: self.add_pcap())
            self.add_pcap_button.setGeometry(QtCore.QRect(370, 22, 111, 31))

            self.add_dataset_button = QtWidgets.QPushButton("Add Dataset", clicked=lambda: self.add_dataset())
            self.add_dataset_button.setGeometry(QtCore.QRect(240, 22, 111, 31))

            self.open_in_wireshark_button = QtWidgets.QPushButton("Export to Wireshark", clicked=lambda : self.open_in_wireshark())
            self.open_in_wireshark_button.setGeometry(QtCore.QRect(500, 22, 111, 31))

            save_action = QAction("Save", self)
            save_action.triggered.connect(lambda: workspace_object.save())

            open_new_workspace_action = QAction("Open new Workspace", self)
            open_new_workspace_action.triggered.connect(lambda: self.open_new_workspace())

            open_existing_workspace_action = QAction("Open Existing Workspace", self)
            open_existing_workspace_action.triggered.connect(lambda: print("Open Existing Workspace"))

            menu = self.menuBar()
            menu_file = menu.addMenu("File")
            menu_file.addAction(save_action)
            menu_file.addAction(open_new_workspace_action)
            menu_file.addAction(open_existing_workspace_action)

            self.setLayout(QtWidgets.QVBoxLayout())
            self.layout().addWidget(self.add_project_button)
            self.layout().addWidget(self.project_tree)
            self.layout().addWidget(self.add_dataset_button)
            self.layout().addWidget(self.add_pcap_button)
            self.layout().addWidget(self.open_in_wireshark_button)

            if existing_flag == True:
                self.generate_existing_workspace()
        except:
            traceback.print_exc()

        self.show()

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        remove_project_action = context_menu.addAction("Remove Project")
        remove_dataset_action = context_menu.addAction("Remove Dataset")
        remove_pcap_action = context_menu.addAction("Remove Pcap")

        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action == remove_project_action:
            self.remove_project()
        elif action == remove_dataset_action:
            self.remove_dataset()
        elif action == remove_pcap_action:
            self.remove_pcap()

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

    def add_project(self, text = None):
        if self.test_mode == False:
            text = QInputDialog.getText(self, "Project Name Entry", "Enter Project name:")[0]
        if not self.project_tree.findItems(text, QtCore.Qt.MatchRecursive, 0):
            project = Project(name=text)
            self.workspace_object.add_project(project)

            item = QtWidgets.QTreeWidgetItem(self.project_tree)
            item.setText(0, text)
            return True
        else:
            print("Item named " + text + " already exists")
            return False

    def remove_project(self, project = None):
        if self.project_tree.selectedItems() and self.check_if_item_is(self.project_tree.selectedItems()[0], "Project") or self.test_mode == True:
            if self.test_mode == False:
                project = self.project_tree.selectedItems()[0]
            for p in self.workspace_object.project:
                if p.name == project.text(0):
                    self.workspace_object.del_project(p)
                    QTreeWidget.invisibleRootItem(self.project_tree).removeChild(project)
                    return True
            return False

    def add_dataset(self, text = None, file = None, project = None):
        try:
            pcap_path = ""
            pcap_name = ""
            if self.project_tree.selectedItems() and self.check_if_item_is(self.project_tree.selectedItems()[0], "Project") or self.test_mode == True:
                if self.test_mode == False:
                    text = QInputDialog.getText(self, "Dataset Name Entry", "Enter Dataset name:")[0]
                if not self.project_tree.findItems(text, QtCore.Qt.MatchRecursive, 0) and text != "":
                    if self.test_mode == False:
                        pcap_path, pcap_name, file = self.get_pcap_path()
                    else:
                        pcap_path, pcap_name = os.path.split(file)
                    if pcap_path == None:
                        return False
                    if self.test_mode == False:
                        project = self.project_tree.selectedItems()[0]

                    for p in self.workspace_object.project:
                        if p.name == project.text(0) and p.find_dataset(text) == None:
                            dataset = Dataset(name=text, parentPath=p.path)
                            p.add_dataset(dataset)
                            child_item = QtWidgets.QTreeWidgetItem()
                            child_item.setText(0, text)
                            project.addChild(child_item)

                            #if self.test_mode == False:
                            new_pcap = Pcap(file= file, path= dataset.path, name= pcap_name)
                            if new_pcap.name != None:
                                dataset.add_pcap(new=new_pcap)
                                pcap_item = QtWidgets.QTreeWidgetItem()
                                pcap_item.setText(0, pcap_name)
                                child_item.addChild(pcap_item)
                            else:
                                child_item.parent().removeChild(child_item)
                                p.del_dataset(dataset)
                            return True
                    return False
                else:
                    return False
        except:
            print(traceback.print_exc())
            return False

    def remove_dataset(self, dataset_item = None):
         if self.project_tree.selectedItems() and self.check_if_item_is(self.project_tree.selectedItems()[0], "Dataset") or self.test_mode == True:
            if self.test_mode == False:
                dataset_item = self.project_tree.selectedItems()[0]
            for p in self.workspace_object.project:
                for d in p.dataset:
                    if d.name == dataset_item.text(0):
                        p.del_dataset(old=d)
                        dataset_item.parent().removeChild(dataset_item)
                        return True
            return False

    def add_pcap(self, dataset_item = None, file = None):
        try:
            if self.project_tree.selectedItems()and self.check_if_item_is(self.project_tree.selectedItems()[0], "Dataset") or self.test_mode:
                pcap_path = ""
                pcap_name = ""
                if self.test_mode == False:
                    pcap_path, pcap_name, file = self.get_pcap_path()
                else:
                    pcap_path, pcap_name = os.path.split(file)
                if pcap_path == None:
                    return False
                if self.test_mode == False:
                    dataset_item = self.project_tree.selectedItems()[0]
                for p in self.workspace_object.project:
                    for d in p.dataset:
                        if d.name == dataset_item.text(0):
                            #if self.test_mode == False:
                            new_pcap = Pcap(file=file, path=d.path, name=pcap_name)
                            for cap in d.pcaps:
                                if new_pcap.name == cap.name:
                                    return
                            if new_pcap.name != None and new_pcap not in d.pcaps:
                                d.add_pcap(new_pcap)
                                pcap_item = QtWidgets.QTreeWidgetItem()
                                pcap_item.setText(0, pcap_name)
                                dataset_item.addChild(pcap_item)
                                return True
                return False
        except:
            print("Error loading this pcap")

    def remove_pcap(self, pcap_item = None):
        try:
            if self.project_tree.selectedItems() and self.project_tree.selectedItems()[0].child(0) == None \
                    and self.check_if_item_is(self.project_tree.selectedItems()[0], "Dataset") == False\
                    and self.check_if_item_is(self.project_tree.selectedItems()[0], "Project") == False or self.test_mode == True:

                if self.test_mode == False:
                    pcap_item = self.project_tree.selectedItems()[0]
                for p in self.workspace_object.project:
                    for d in p.dataset:
                        for cap in d.pcaps:
                            if cap.name == pcap_item.text(0):
                                d.del_pcap(cap)
                                pcap_item.parent().removeChild(pcap_item)
                                return True
                return False
        except:
            traceback.print_exc()
            return False

    def open_in_wireshark(self, pcap_item = None, dataset_item = None, merge_flag = False):
        try:
            if self.project_tree.selectedItems() and self.check_if_item_is(self.project_tree.selectedItems()[0], "Dataset") or (self.test_mode == True and merge_flag == True):
                if self.test_mode == False:
                    dataset_item = self.project_tree.selectedItems()[0]
                for p in self.workspace_object.project:
                    for d in p.dataset:
                        if d.name == dataset_item.text(0):
                            Wireshark.openwireshark(d.mergeFilePath)
                            return True
                False

            if self.project_tree.selectedItems() and self.project_tree.selectedItems()[0].child(0) == None \
                    and self.check_if_item_is(self.project_tree.selectedItems()[0], "Dataset") == False \
                    and self.check_if_item_is(self.project_tree.selectedItems()[0], "Project") == False or self.test_mode == True:

                if self.test_mode == False:
                    pcap_item = self.project_tree.selectedItems()[0]
                for p in self.workspace_object.project:
                    for d in p.dataset:
                        for cap in d.pcaps:
                            if pcap_item.text(0) == cap.name:
                                if self.test_mode == True:
                                    return True
                                Wireshark.openwireshark(cap.pcap_file)
        except:
            traceback.print_exc()
            return False

    def get_pcap_path(self, full_path:str = None):
        file_filter = "Wireshark capture file (*.pcap)"
        initial_filter = "Wireshark capture file (*.pcap)"
        if self.test_mode == False:
            full_path = QFileDialog.getOpenFileName(caption="Add a Pcap file to this Dataset", filter= file_filter, initialFilter= initial_filter)[0]

        if full_path != "":
            path, name = self.collect_path_and_name(full_path)
            return path, name, full_path
        else:
            return None, None, full_path

    def check_if_item_is(self, item, key: str):
        try:
            if key == "Project":
                for p in self.workspace_object.project:
                    if item.text(0) == p.name:
                        return True

            if key == "Dataset":
                for p in self.workspace_object.project:
                    for d in p.dataset:
                        if d.name == item.text(0):
                            return True
            return False
        except:
            traceback.print_exc()
            return False

    def open_new_workspace(self, file = None):
        try:
            if self.test_mode == False:
                file = QFileDialog.getSaveFileName(caption="Choose Workspace location")[0]

            if file != '':
                #path, workspace_name = self.collect_path_and_name(file)
                new_workspace_object = Workspace(name=os.path.basename(file), location=os.path.dirname(file))
                self.workspace = Workspace_UI(os.path.basename(file), new_workspace_object)
                self.workspace.show()
                return True
        except:
            traceback.print_exc()
            return False

    def collect_path_and_name(self, full_path: str):
        file_split = ""
        on_windows = True
        path = ""
        name = ""

        if "/" in full_path:
            file_split = full_path.split("/")
            on_windows = True
        elif "\\" in full_path:
            file_split = full_path.split("\\")
            on_windows = False

        if on_windows == True:
            name = file_split[-1]
            file_split.pop()
            empty = "/"
            path = empty.join(file_split)
        elif on_windows == False:
            name = file_split[-1]
            file_split.pop()
            empty = "\\"
            path = empty.join(file_split)

        return path, name

    def generate_existing_workspace(self):
        for p in self.workspace_object.project:
            project_item = QtWidgets.QTreeWidgetItem(self.project_tree)
            project_item.setText(0, p.name)
            for d in p.dataset:
                dataset_item = QtWidgets.QTreeWidgetItem()
                dataset_item.setText(0, d.name)
                project_item.addChild(dataset_item)
                for cap in d.pcaps:
                    pcap_item = QtWidgets.QTreeWidgetItem()
                    pcap_item.setText(0, cap.name)
                    dataset_item.addChild(pcap_item)
        return True