import sys
import traceback

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTreeWidget, QWidget, QPushButton

from packetvisualization.backend_components import json_parser
from packetvisualization.backend_components.controller import Controller
from packetvisualization.models.dataset import Dataset
from packetvisualization.models.workspace import Workspace
from packetvisualization.models.context.database_context import DbContext
import plotly.express as px
import plotly.offline as po



class properties_window(QWidget):
    # QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # app = QtWidgets.QApplication(sys.argv)
    # filter_window = QtWidgets.QMainWindow()

    def __init__(self, jsonString, obj, db, workspace):

        self.cursorObj = jsonString
        self.controller = Controller()
        self.obj = obj
        self.db = db
        self.workspace = workspace

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
        selected_properties = []

        for i in range(len(items)):
            selected_properties.append(str(self.listWidget.selectedItems()[i].text()))

        if self.cluster.text() == "" and len(selected_properties) == 0:
            raise Exception('Please select properties and enter a correct cluster number')
        df, features = self.controller.create_analysis(self.pktIdsAsList,
                                                       selected_properties,
                                                       int(self.cluster.text()),
                                                       self.obj,
                                                       self.db)

        fig = px.scatter(df, x="cluster", y="instance_number",
                         color='cluster', color_continuous_scale=px.colors.sequential.Bluered_r,
                         hover_data=df.columns.values[:len(features)])

        raw_html = '<html><head><meta charset="utf-8" />'
        raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        raw_html += '<body>'
        raw_html += po.plot(fig, include_plotlyjs=False, output_type='div')
        raw_html += '</body></html>'

        self.workspace.classifier_plot_view.setHtml(raw_html)
        self.workspace.classifier_window.show()
        self.close()
