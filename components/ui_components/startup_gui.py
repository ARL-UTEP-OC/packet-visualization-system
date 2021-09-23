import re
import shutil
import sys
import traceback

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog

from components.models.workspace import Workspace
from workspace_gui import Workspace_UI


class Ui_startup_window(object):
    def setupUi(self, startup_window):
        startup_window.setObjectName("startup_window")
        startup_window.setFixedSize(248, 121)
        self.centralwidget = QtWidgets.QWidget(startup_window)
        self.centralwidget.setObjectName("centralwidget")

        self.new_workspace_button = QtWidgets.QPushButton(self.centralwidget, clicked = lambda: self.open_new_workspace())
        self.new_workspace_button.setGeometry(QtCore.QRect(40, 20, 171, 31))
        self.new_workspace_button.setObjectName("new_workspace_button")


        self.existing_workspace_button = QtWidgets.QPushButton(self.centralwidget, clicked = lambda: self.open_existing_workspace())
        self.existing_workspace_button.setGeometry(QtCore.QRect(40, 70, 171, 31))
        self.existing_workspace_button.setObjectName("existing_workspace_button")

        startup_window.setCentralWidget(self.centralwidget)
        self.retranslateUi(startup_window)
        QtCore.QMetaObject.connectSlotsByName(startup_window)

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
                startup_window.close()
                path, workspace_name = self.collect_path_and_name(file)
                workspace_object = Workspace(name=workspace_name, location=path)

                self.workspace = Workspace_UI(workspace_name, workspace_object)
                self.workspace.show()
        except:
            traceback.print_exc()
    def open_existing_workspace(self):
        file = QFileDialog.getOpenFileName(caption="Open existing Workspace")
        #Open existing workspace from path "file"

    def retranslateUi(self, startup_window):
        _translate = QtCore.QCoreApplication.translate
        startup_window.setWindowTitle(_translate("startup_window", "Startup"))
        self.new_workspace_button.setText(_translate("startup_window", "Start a new Workspace"))
        self.existing_workspace_button.setText(_translate("startup_window", "Open an existing Workspace"))


if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    startup_window = QtWidgets.QMainWindow()
    ui = Ui_startup_window()
    ui.setupUi(startup_window)
    startup_window.show()
    sys.exit(app.exec_())