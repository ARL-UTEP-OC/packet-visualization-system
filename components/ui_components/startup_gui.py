import re
import shutil
import sys
import traceback

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog

from components.models.workspace import Workspace
from workspace_gui import Workspace_UI


class Ui_startup_window(object):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    startup_window = QtWidgets.QMainWindow()
    def setupUi(self):
        self.startup_window.setObjectName("startup_window")
        self.startup_window.setFixedSize(248, 121)
        self.centralwidget = QtWidgets.QWidget(self.startup_window)
        self.centralwidget.setObjectName("centralwidget")

        self.new_workspace_button = QtWidgets.QPushButton(self.centralwidget, clicked = lambda: self.open_new_workspace())
        self.new_workspace_button.setGeometry(QtCore.QRect(40, 20, 171, 31))
        self.new_workspace_button.setObjectName("new_workspace_button")


        self.existing_workspace_button = QtWidgets.QPushButton(self.centralwidget, clicked = lambda: self.open_existing_workspace())
        self.existing_workspace_button.setGeometry(QtCore.QRect(40, 70, 171, 31))
        self.existing_workspace_button.setObjectName("existing_workspace_button")

        self.startup_window.setCentralWidget(self.centralwidget)
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self.startup_window)

    def collect_path_and_name(self, full_path:str):
        file_split = ""
        on_windows = True
        path = ""
        name = ""

        if "/" in full_path:
            file_split = full_path.split("/")
            on_windows = True
        elif "\\" in full_path:
            file_split = full_path.split("\\")
            on_windows = False

        if on_windows == True:
            name = file_split[-1]
            file_split.pop()
            empty = "/"
            path = empty.join(file_split)
        elif on_windows == False:
            name = file_split[-1]
            file_split.pop()
            empty = "\\"
            path = empty.join(file_split)

        return path, name

    def open_new_workspace(self):
        try:
            file = QFileDialog.getSaveFileName(caption="Choose Workspace location")[0]

            if file != '':
                self.startup_window.close()
                path, workspace_name = self.collect_path_and_name(file)
                workspace_object = Workspace(name=workspace_name, location=path)

                self.workspace = Workspace_UI(workspace_name, workspace_object)
                self.workspace.show()
        except:
            traceback.print_exc()
    def open_existing_workspace(self):
        file = QFileDialog.getOpenFileName(caption="Open existing Workspace")
        #Open existing workspace from path "file"

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.startup_window.setWindowTitle(_translate("startup_window", "Startup"))
        self.new_workspace_button.setText(_translate("startup_window", "Start a new Workspace"))
        self.existing_workspace_button.setText(_translate("startup_window", "Open an existing Workspace"))

    def run_program(self):
        # QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        # application = QtWidgets.QApplication(sys.argv)
        self.setupUi()
        self.startup_window.show()
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    # QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # app = QtWidgets.QApplication(sys.argv)
    # startup_window = QtWidgets.QMainWindow()
    # ui = Ui_startup_window()
    # ui.setupUi(startup_window)
    # startup_window.show()
    # sys.exit(app.exec_())
    ui = Ui_startup_window()
    ui.run_program()