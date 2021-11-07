import sys
import traceback

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTreeWidget, QWidget, QPushButton

from packetvisualization.backend_components import json_parser
from packetvisualization.backend_components.controller import Controller
from packetvisualization.models.dataset import Dataset
from packetvisualization.models.workspace import Workspace
import plotly.express as px
import plotly.graph_objects as go


class properties_window(QWidget):
    # QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # app = QtWidgets.QApplication(sys.argv)
    # filter_window = QtWidgets.QMainWindow()

    def __init__(self, jsonString, obj):

        self.cursorObj = jsonString
        self.controller = Controller()
        self.obj = obj

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

        self.layout.addWidget(self.listWidget, 0, 2, 1, 2)

        self.listWidget2 = QtWidgets.QListWidget()

        self.listWidget2.setGeometry(QtCore.QRect(10, 10, 211, 291))

        self.pktIdsAsList = []
        for i in range(len(pktIds)):
            string = str(pktIds[i])
            self.pktIdsAsList.append(string)
            item = QtWidgets.QListWidgetItem(string)
            self.listWidget2.addItem(item)

        self.layout.addWidget(self.listWidget2, 0, 0, 1, 2)

        self.button = QtWidgets.QPushButton("Analyze", clicked=lambda: self.analyze())
        self.layout.addWidget(self.button, 1, 2, 1, 2)


        self.cluster = QtWidgets.QLineEdit(self)
        self.cluster.setObjectName("cluster")
        self.layout.addWidget(self.cluster, 1, 1, 1, 1)

        self.setLayout(self.layout)

    def analyze(self):
        if (type(self.obj) != Dataset):
            return 'Not a dataset name'
        items = self.listWidget.selectedItems()
        selProperties = []
        
        for i in range(len(items)):
            selProperties.append(str(self.listWidget.selectedItems()[i].text()))

        if self.cluster.text() != "" and len(selProperties) != 0:
            df, features = self.controller.create_analysis(self.pktIdsAsList, selProperties, self.cluster.text(), self.obj)
            fig = px.scatter(df, x="cluster", y="instance_number", 
                 color='cluster',color_continuous_scale=px.colors.sequential.Bluered_r,
                 hover_data=df.columns.values[:len(features)])
            fig.show()
            self.close()



