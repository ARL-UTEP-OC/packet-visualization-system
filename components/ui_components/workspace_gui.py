
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QFileDialog

from components.models.project import Project
from components.models.workspace import Workspace

class Workspace_UI(QtWidgets.QMainWindow):
    def __init__(self, workspace_name: str, workspace_object: Workspace):
        # Workspace Constructor
        super().__init__()
        self.setFixedSize(917,548)
        self.setWindowTitle(workspace_name)

        self.project_tree = QtWidgets.QTreeWidget()
        self.project_tree.setGeometry(QtCore.QRect(0, 62, 221, 451))
        self.project_tree.setHeaderLabels(["Project(s) Name", "Size", "DoC"])

        self.add_project_button = QtWidgets.QPushButton("Add a Project",clicked = lambda : self.add_project(workspace_object))
        self.add_project_button.setGeometry(QtCore.QRect(0, 22, 221, 41))

        self.add_pcap_button = QtWidgets.QPushButton("Add Pcap", clicked=lambda: self.add_pcap())
        self.add_pcap_button.setGeometry(QtCore.QRect(370, 22, 111, 31))

        self.add_dataset_button = QtWidgets.QPushButton("Add Dataset", clicked=lambda: self.add_dataset())
        self.add_dataset_button.setGeometry(QtCore.QRect(240, 22, 111, 31))

        self.open_in_wireshark_button = QtWidgets.QPushButton("Export to Wireshark")
        self.open_in_wireshark_button.setGeometry(QtCore.QRect(500, 22, 111, 31))

        menu = self.menuBar()
        menu_file = menu.addMenu("File")
        menu_file.addAction("Save")
        menu_file.addAction("Open new Workspace")

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.add_project_button)
        self.layout().addWidget(self.project_tree)
        self.layout().addWidget(self.add_dataset_button)
        self.layout().addWidget(self.add_pcap_button)
        self.layout().addWidget(self.open_in_wireshark_button)

        self.show()

    def add_project(self, workspace_object: Workspace):
        text = QInputDialog.getText(self, "Project Name Entry", "Enter Project name:")[0]
        if not self.project_tree.findItems(text, QtCore.Qt.MatchRecursive, 0):
            project = Project(name=text)
            workspace_object.add_project(project)

            item = QtWidgets.QTreeWidgetItem(self.project_tree)
            item.setText(0, text)
        else:
            print("Item already exists")


    def add_dataset(self):
        if self.project_tree.selectedItems() and self.project_tree.selectedItems()[0].parent() == None:
            project = self.project_tree.selectedItems()[0]
            text = QInputDialog.getText(self, "Dataset Name Entry", "Enter Dataset name:")[0]

            child_item = QtWidgets.QTreeWidgetItem()
            child_item.setText(0, text)
            project.addChild(child_item)

    def add_pcap(self):
        if self.project_tree.selectedItems() and self.project_tree.selectedItems()[0].parent().parent() == None:
            print()
        return

    def save(self):
        print()
        return

    def open_new_workspace(self):
        file = QFileDialog.getSaveFileName(caption="Choose Workspace location")
        file_split = file[0].split("/")
        workspace_name = file_split[-1]
        if file != ('', ''):
            self.workspace = Workspace_UI(workspace_name)
            self.workspace.show()
