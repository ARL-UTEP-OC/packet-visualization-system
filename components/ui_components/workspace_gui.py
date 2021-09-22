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

class Workspace_UI(QtWidgets.QMainWindow):
    def __init__(self, workspace_name: str, workspace_object: Workspace):
        # Workspace Constructor
        super(Workspace_UI, self).__init__()
        self.workspace_object = workspace_object

        self.setFixedSize(917, 548)
        self.setWindowTitle(workspace_name)

        self.project_tree = QtWidgets.QTreeWidget()
        self.project_tree.setGeometry(QtCore.QRect(0, 62, 221, 451))
        self.project_tree.setHeaderLabels(["Project(s) Name", "Size", "DoC"])
        self.project_tree.installEventFilter(self)

        self.add_project_button = QtWidgets.QPushButton("Add a Project", clicked=lambda: self.add_project())
        self.add_project_button.setGeometry(QtCore.QRect(0, 22, 221, 41))

        self.add_pcap_button = QtWidgets.QPushButton("Add Pcap", clicked=lambda: self.add_pcap())
        self.add_pcap_button.setGeometry(QtCore.QRect(370, 22, 111, 31))

        self.add_dataset_button = QtWidgets.QPushButton("Add Dataset", clicked=lambda: self.add_dataset())
        self.add_dataset_button.setGeometry(QtCore.QRect(240, 22, 111, 31))

        self.open_in_wireshark_button = QtWidgets.QPushButton("Export to Wireshark")
        self.open_in_wireshark_button.setGeometry(QtCore.QRect(500, 22, 111, 31))

        save_action = QAction("Save", self)
        save_action.triggered.connect(lambda: self.save())

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

        self.show()

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        remove_project_action = context_menu.addAction("Remove Project")

        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action == remove_project_action:
            self.remove_project()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Workspace Close", "Would you like to save this Workspace?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.workspace_object.save()
            event.accept()
        else:
            self.workspace_object.close()
            event.accept()

    def add_project(self):
        text = QInputDialog.getText(self, "Project Name Entry", "Enter Project name:")[0]
        if not self.project_tree.findItems(text, QtCore.Qt.MatchRecursive, 0):
            project = Project(name=text)
            self.workspace_object.add_project(project)

            item = QtWidgets.QTreeWidgetItem(self.project_tree)
            item.setText(0, text)
        else:
            print("Item named " + text + " already exists")

    def remove_project(self):
        try:
            if self.project_tree.selectedItems() and self.project_tree.selectedItems()[0].parent() == None:
                project = self.project_tree.selectedItems()[0]
                for p in self.workspace_object.project:
                    if p.name == project.text(0):
                        self.workspace_object.del_project(p)
                        QTreeWidget.invisibleRootItem(self.project_tree).removeChild(project)
                        return True
        except:
            print(traceback.print_exc())
            return False

    def add_dataset(self):
        try:
            if self.project_tree.selectedItems() and self.project_tree.selectedItems()[0].parent() == None:
                text = QInputDialog.getText(self, "Dataset Name Entry", "Enter Dataset name:")[0]
                if not self.project_tree.findItems(text, QtCore.Qt.MatchRecursive, 0):
                   # pcap_path, pcap_name = self.collect_path_and_name(self.get_pcap_path())
                    #print(pcap_name)
                    #if pcap_path == "":
                        #return False
                    project = self.project_tree.selectedItems()[0]

                    for p in self.workspace_object.project:
                        if p.name == project.text(0):
                            dataset = Dataset(name=text, path=p.path)
                            p.add_dataset(dataset)
                            child_item = QtWidgets.QTreeWidgetItem()
                            child_item.setText(0, text)
                            project.addChild(child_item)

                            #new_pcap = Pcap(file= pcap_path)
                            #pcap_item = QtWidgets.QTreeWidgetItem()
                            #pcap_item.setText(0, )
                            #child_item.addChild()
                            return True
                else:
                    print("Item named " + text + " already exists")
        except:
            print(traceback.print_exc())

    def add_pcap(self):
        if self.project_tree.selectedItems() and self.project_tree.selectedItems()[0].parent().parent() == None:
            print("Adding Pcap")
            file = QFileDialog.getOpenFileName(caption= "Add a Pcap file to this Dataset")

        return
    def get_pcap_path(self):
        file_filter = "Wireshark capture file (*.pcap)"
        initial_filter = "Wireshark capture file (*.pcap)"
        path = QFileDialog.getOpenFileName(caption="Add a Pcap file to this Dataset", filter= file_filter, initialFilter= initial_filter)[0]
        return path

    def save(self):
        try:
            self.workspace_object.save()
        except:
            traceback.print_exc()
        return

    def open_new_workspace(self):
        file = QFileDialog.getSaveFileName(caption="Choose Workspace location")[0]

        if file != '':
            path, workspace_name = self.collect_path_and_name(file)
            new_workspace_object = Workspace(name=workspace_name, location=path, project=[])
            new_workspace_object.close()
            self.workspace = Workspace_UI(workspace_name, new_workspace_object)
            self.workspace.show()

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
