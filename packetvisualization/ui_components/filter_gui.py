import os
import sys
import traceback

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog, QTextEdit, QLineEdit, QFormLayout
from PyQt5.QtWidgets import QTreeWidget


#from components.backend_components.load import Load
#from components.models.dataset import Dataset
#from components.models.pcap import Pcap
#from components.models.project import Project
#from components.models.workspace import Workspace
#from components.ui_components.workspace_gui import Workspace_UI
from components.backend_components import Wireshark
from components.models.project import Project
from components.models.workspace import Workspace


class filter_window(QtWidgets.QWidget):

    # QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # app = QtWidgets.QApplication(sys.argv)
    # filter_window = QtWidgets.QMainWindow()

    def __init__(self, path, projectTree: QTreeWidget, workspace: Workspace):

        super().__init__()
        self.setWindowTitle("Filter Wireshark")
        form_layout = QFormLayout()
        self.setLayout(form_layout)

        self.ipFilter = QtWidgets.QLineEdit(self)
        self.ipFilter.setObjectName("ip.addr")

        self.portFilter = QtWidgets.QLineEdit(self)
        self.portFilter.setObjectName("tcp.port")

        self.newFileName = QtWidgets.QLineEdit(self)
        self.newFileName.setObjectName("newFileName")

        form_layout.addRow("IP Address", self.ipFilter)
        form_layout.addRow("TCP Port", self.portFilter)
        form_layout.addRow("File Name", self.newFileName)
        form_layout.addRow(QtWidgets.QPushButton("Submit", clicked=lambda: self.submit_filter_options()))

        self.show()

        self.path = path

        self.projectTree = projectTree

        self.workspace = workspace

        print(self.path)

        #self.filter_window.setObjectName("Filter Wireshark")
        #self.filter_window.setFixedSize(400, 800)
        #self.filter_window.setWindowTitle("Filter Wireshark")
        #self.centralwidget = QtWidgets.QWidget(self.filter_window)
        #self.centralwidget.setObjectName("centralwidget")

        #self.ip_filter_label = QtWidgets.QLabel(self.filter_window)
        #self.ip_filter_label.setText("IP Addr")
        #self.ip_filter_label.setGeometry(QtCore.QRect(10, 20, 50, 20))
        #self.ip_filter_input = QtWidgets.QTextEdit(self.filter_window)
        #self.ip_filter_input.setGeometry(QtCore.QRect(190, 15, 200, 25))
        #self.ip_filter_input.setObjectName("ip.addr")

        #self.ip_filter_label = QtWidgets.QLabel(self.filter_window)
        #self.ip_filter_label.setText("TCP Port")
        #self.ip_filter_label.setGeometry(QtCore.QRect(10, 50, 50, 20))
        #self.ip_filter_input = QtWidgets.QTextEdit(self.filter_window)
        #self.ip_filter_input.setGeometry(QtCore.QRect(190, 50, 200, 25))
        #self.ip_filter_input.setObjectName("tcp.port")

        # self.submit_button = QtWidgets.QPushButton(self.filter_window, clicked=lambda : self.submit_filter_options())
        # self.submit_button.setGeometry(QtCore.QRect(300, 750, 90, 30))
        # self.submit_button.setText("Submit")



    def submit_filter_options(self):
        wsFilter = {}
        newFileName = self.findChild(QLineEdit, "newFileName")
        if newFileName.text() != "":
            for w in self.findChildren(QLineEdit):
                if w.objectName() != "newFileName":
                    wsFilter[w.objectName()] = w.text()

            Wireshark.filter(self.path, wsFilter, newFileName.text(), self.projectTree, self.workspace)

        #print(self.path)



