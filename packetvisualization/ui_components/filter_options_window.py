from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QFormLayout, QScrollArea, QGroupBox, QVBoxLayout, QLineEdit, QComboBox
import traceback
import sys
from packetvisualization.models import filter


class filter_options_window(QtWidgets.QWidget):
    # QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # app = QtWidgets.QApplication(sys.argv)
    # filter_window = QtWidgets.QMainWindow()

    def __init__(self, filter_options):

        try:
            super().__init__()
            self.setWindowTitle("Set Filters")
            self.setGeometry(200, 500, 400, 300)
            form_layout = QFormLayout()
            groupBox = QGroupBox()

            self.setLayout(form_layout)

            dropdown = QComboBox(self)
            dropdown.addItem("K-Means")
            form_layout.addRow("Algorithm", dropdown)
            for i in filter_options:
                self.cmd = QtWidgets.QLineEdit(self)
                self.cmd.setObjectName(f"{i}")
                form_layout.addRow(f"{i}", self.cmd)

            # form_layout.addRow(QtWidgets.QPushButton("Submit", clicked=lambda: self.submit()))

            groupBox.setLayout(form_layout)
            scroll = QScrollArea()
            scroll.setWidget(groupBox)
            scroll.setWidgetResizable(True)
            scroll.setFixedHeight(400)
            layout = QVBoxLayout(self)
            layout.addWidget(scroll)
            layout.addWidget(QtWidgets.QPushButton("Submit", clicked=lambda: self.submit()))

            self.show()
        except Exception:
            print(traceback.format_exc())
            print(sys.exc_info()[2])

    def submit(self):
        filters = {}
        for w in self.findChildren(QLineEdit):
            if w.objectName() != "newFileName" and w.text() != "":
                filters[w.objectName()] = w.text()

        filter.filters = filters
        self.close()






