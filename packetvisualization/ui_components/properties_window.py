from datetime import datetime

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QFormLayout, QTextEdit, QListWidget

from packetvisualization.models.analysis import Analysis
from packetvisualization.models.dataset import Dataset
from packetvisualization.models.project import Project


class PropertiesWindow(QWidget):
    def __init__(self, item):
        super().__init__()
        self.init_window()
        self.item = item

    def init_window(self):
        self.setWindowTitle("Properties")
        self.setWindowIcon(QIcon(":logo.png"))

    def get_properties(self):
        if type(self.item) == Project:
            self.get_project_properties()
            self.show()
        elif type(self.item) == Dataset:
            self.get_dataset_properties()
            self.show()
        elif type(self.item) == Analysis:
            self.get_analysis_properties()
            self.show()

    def get_project_properties(self):
        name = QLabel(self.item.name)
        c_date = QLabel(str(datetime.fromtimestamp(self.item.c_time)))
        size = QLabel(self.item.get_size())

        layout = QFormLayout()
        layout.addRow("Project Name: ", name)
        layout.addRow("Date Created: ", c_date)
        layout.addRow("Size: ", size)

        self.setLayout(layout)

    def get_dataset_properties(self):
        name = QLabel(self.item.name)
        packets = QLabel(str(self.item.totalPackets))
        s_time = QLabel(self.item.s_time.strftime("%m/%d/%Y, %H:%M:%S"))
        e_time = QLabel(self.item.e_time.strftime("%m/%d/%Y, %H:%M:%S"))

        pcaps = QListWidget()
        for i in self.item.pcaps:
            temp = i.name
            QListWidget.addItem(pcaps, temp)
        pcaps.setFixedHeight(75)

        protocols = QListWidget()
        for p in self.item.protocols:
            temp = "%s: %s" % (p[0], p[1])
            QListWidget.addItem(protocols, temp)
        protocols.setFixedHeight(100)

        metadata = QTextEdit(self, plainText=self.item.m_data, lineWrapMode=QTextEdit.FixedColumnWidth,
                             lineWrapColumnOrWidth=50, placeholderText="Custom metadata")
        metadata.textChanged.connect(lambda: text_changed())

        layout = QFormLayout()
        layout.addRow("Dataset Name: ", name)
        layout.addRow("No. Packets: ", packets)
        layout.addRow("Start Time: ", s_time)
        layout.addRow("End Time: ", e_time)
        layout.addRow("PCAP Names: ", pcaps)
        layout.addRow("Protocols: ", protocols)
        layout.addRow("Metadata: ", metadata)
        self.setLayout(layout)

        def text_changed():
            self.item.m_data = metadata.toPlainText()

    def get_analysis_properties(self):
        name = QLabel(self.item.name)
        origin = QLabel(self.item.origin)

        features = QListWidget()
        for f in self.item.features:
            QListWidget.addItem(features, f)
        features.setFixedHeight(100)

        metadata = QTextEdit(self, plainText=self.item.m_data, lineWrapMode=QTextEdit.FixedColumnWidth,
                             lineWrapColumnOrWidth=50, placeholderText="Custom metadata")
        metadata.textChanged.connect(lambda: text_changed())

        layout = QFormLayout()
        layout.addRow("Analysis Name: ", name)
        layout.addRow("Dataset Origin: ", origin)
        layout.addRow("Features: ", features)
        layout.addRow("Metadata: ", metadata)
        self.setLayout(layout)

        def text_changed():
            self.item.m_data = metadata.toPlainText()
