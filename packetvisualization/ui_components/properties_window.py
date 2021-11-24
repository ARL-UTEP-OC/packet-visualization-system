from datetime import datetime

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QLineEdit, QFormLayout, QTextEdit

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
        elif type(self.item) == Dataset:
            self.get_dataset_properties()
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
        packets = QLabel("0")
        s_time = QLabel("0")
        e_time = QLabel("0")
        protocols = QLabel("TCP: 0;\nUDP: 0;")
        pcaps = QLabel("0")

        metadata = QTextEdit(self, plainText=self.item.m_data, lineWrapMode=QTextEdit.FixedColumnWidth,
                             lineWrapColumnOrWidth=50, placeholderText="Custom metadata")
        metadata.textChanged.connect(lambda: text_changed())

        layout = QFormLayout()
        layout.addRow("Dataset Name: ", name)
        layout.addRow("No. Packets: ", packets)
        layout.addRow("Start Time: ", s_time)
        layout.addRow("End Time: ", e_time)
        layout.addRow("Protocols: ", protocols)
        layout.addRow("PCAP Names: ", pcaps)
        layout.addRow("Metadata: ", metadata)

        self.setLayout(layout)

        def text_changed():
            self.item.m_data = metadata.toPlainText()
