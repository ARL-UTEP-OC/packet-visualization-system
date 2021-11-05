import sys
import traceback

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTreeWidget, QWidget, QPushButton

from packetvisualization.backend_components import json_parser
from packetvisualization.models.workspace import Workspace


class properties_window(QWidget):
    # QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # app = QtWidgets.QApplication(sys.argv)
    # filter_window = QtWidgets.QMainWindow()

    def __init__(self, jsonString):

        super().__init__()
        self.setWindowTitle("Select Properties")
        # form_layout = QFormLayout()
        # self.setLayout(form_layout)
        self.layout = QtWidgets.QGridLayout()

        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )

        self.listWidget.setGeometry(QtCore.QRect(10, 10, 211, 291))
        items = json_parser.parser(jsonString)
        properties = items[0]
        pktIds = items[1]

        for i in properties:
            item = QtWidgets.QListWidgetItem(i)
            self.listWidget.addItem(item)

        self.listWidget.itemClicked.connect(self.printItemText)
        self.layout.addWidget(self.listWidget, 0, 2, 1, 2)

        self.listWidget2 = QtWidgets.QListWidget()
        # self.listWidget2.setSelectionMode(
        #     QtWidgets.QAbstractItemView.ExtendedSelection
        # )

        self.listWidget2.setGeometry(QtCore.QRect(10, 10, 211, 291))

        self.pktIdsAsList = []
        for i in range(len(pktIds)):
            string = str(pktIds[i])
            self.pktIdsAsList.append(string)
            print(string)
            item = QtWidgets.QListWidgetItem(string)
            self.listWidget2.addItem(item)

        self.layout.addWidget(self.listWidget2, 0, 0, 1, 2)

        self.button = QtWidgets.QPushButton("Analyze", clicked=lambda: self.analyze())
        self.layout.addWidget(self.button, 1, 2, 1, 2)


        self.cluster = QtWidgets.QLineEdit(self)
        self.cluster.setObjectName("cluster")
        self.layout.addWidget(self.cluster, 1, 1, 1, 1)

        self.setLayout(self.layout)

            # self.show()

        # self.path = path
        # self.projectTree = projectTree
        # self.workspace = workspace

        #print(self.path)

    def analyze(self):
        items = self.listWidget.selectedItems()
        selProperties = []
        for i in range(len(items)):
            selProperties.append(str(self.listWidget.selectedItems()[i].text()))

        print(selProperties)
        print(self.pktIdsAsList)
        print(self.cluster.text())

        ### Abraham, enter you method call here ###
        ### yourMethod(selProperties,self.pktIdsAsList,self.cluster.text()) ###
        ### selProperties is selected properties (its in method so don't need self) ###
        ### pktIdAsList is the object ids from select packet(s) ###
        ### cluster is the value user enters ###




    # def submit_filter_options(self):
    #     wsFilter = {}
    #     newFileName = self.findChild(QLineEdit, "newFileName")
    #     if newFileName.text() != "":
    #         for w in self.findChildren(QLineEdit):
    #             if w.objectName() != "newFileName" and w.text() != "":
    #                 wsFilter[w.objectName()] = w.text()
    #
    #         error = Wireshark.filter(self.path, wsFilter, newFileName.text(), self.projectTree, self.workspace)
    #         print(error)
    #         if not error:
    #             self.close()
    #         else:
    #             # print(error)
    #             self.errorMsg.setText(f"{error}")

        #print(self.path)



