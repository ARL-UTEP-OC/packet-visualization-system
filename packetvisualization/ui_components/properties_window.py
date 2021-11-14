from datetime import datetime

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout

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
        self.setFixedSize(700, 175)

    def get_properties(self):
        if type(self.item) == Project:
            self.get_project_properties()
        elif type(self.item) == Dataset:
            self.get_dataset_properties()
        self.show()

    def get_project_properties(self):
        name = QLabel("Project Name: " + self.item.name)
        c_date = QLabel("Project Creation Time: " + str(datetime.fromtimestamp(self.item.c_time)))
        size = QLabel("Size: " + self.item.get_size())

        layout = QVBoxLayout()
        layout.addWidget(name)
        layout.addWidget(c_date)
        layout.addWidget(size)

        self.setLayout(layout)

    def get_dataset_properteis(self):
        pass
