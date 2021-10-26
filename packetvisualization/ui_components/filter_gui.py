import os
import sys
import traceback

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QTextEdit, QLineEdit, QFormLayout
from PyQt5.QtWidgets import QTreeWidget

from packetvisualization.backend_components import Wireshark
from packetvisualization.models.workspace import Workspace


class filter_window(QtWidgets.QWidget):

    # QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # app = QtWidgets.QApplication(sys.argv)
    # filter_window = QtWidgets.QMainWindow()

    def __init__(self, path, projectTree: QTreeWidget, workspace: Workspace):

        super().__init__()
        self.setWindowTitle("Filter Wireshark")
        form_layout = QFormLayout()
        self.setLayout(form_layout)

        self.cmd = QtWidgets.QLineEdit(self)
        self.cmd.setObjectName("cmd")

        # self.portFilter = QtWidgets.QLineEdit(self)
        # self.portFilter.setObjectName("tcp.port")

        self.newFileName = QtWidgets.QLineEdit(self)
        self.newFileName.setObjectName("newFileName")

        self.errorMsg = QtWidgets.QLabel()

        form_layout.addRow("Display Filter", self.cmd)
        # form_layout.addRow("TCP Port", self.portFilter)
        form_layout.addRow("File Name*", self.newFileName)
        form_layout.addRow(self.errorMsg)
        form_layout.addRow(QtWidgets.QPushButton("Submit", clicked=lambda: self.submit_filter_options()))

        self.show()

        self.path = path
        self.projectTree = projectTree
        self.workspace = workspace

        #print(self.path)

    def submit_filter_options(self):
        wsFilter = {}
        newFileName = self.findChild(QLineEdit, "newFileName")
        if newFileName.text() != "":
            for w in self.findChildren(QLineEdit):
                if w.objectName() != "newFileName" and w.text() != "":
                    wsFilter[w.objectName()] = w.text()

            error = Wireshark.filter(self.path, wsFilter, newFileName.text(), self.projectTree, self.workspace)
            print(error)
            if not error:
                self.close()
            else:
                # print(error)
                self.errorMsg.setText(f"{error}")

        #print(self.path)



