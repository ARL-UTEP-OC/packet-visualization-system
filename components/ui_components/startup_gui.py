
import sys
import traceback

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog

from components.models.dataset import Dataset
from components.models.pcap import Pcap
from components.models.project import Project
from components.models.workspace import Workspace
from components.ui_components.workspace_gui import Workspace_UI


class Ui_startup_window(object):
    def setupUi(self, startup_window, test_mode:bool = False):

        startup_window.setObjectName("startup_window")
        startup_window.setFixedSize(248, 121)
        self.centralwidget = QtWidgets.QWidget(startup_window)
        self.centralwidget.setObjectName("centralwidget")

        self.new_workspace_button = QtWidgets.QPushButton(self.centralwidget, clicked = lambda: self.open_new_workspace(test_mode= test_mode))
        self.new_workspace_button.setGeometry(QtCore.QRect(40, 20, 171, 31))
        self.new_workspace_button.setObjectName("new_workspace_button")


        self.existing_workspace_button = QtWidgets.QPushButton(self.centralwidget, clicked = lambda: self.open_existing_workspace(test_mode=test_mode))
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

    def open_new_workspace(self, test_mode: bool, file = None):
        try:
            if test_mode == False:
                file = QFileDialog.getSaveFileName(caption="Choose Workspace location")[0]

            if file != '':
                if test_mode == False:
                    startup_window.close()
                path, workspace_name = self.collect_path_and_name(file)
                workspace_object = Workspace(name=workspace_name, location=path)

                self.workspace = Workspace_UI(workspace_name, workspace_object)
                self.workspace.show()
                return True
        except:
            print("Error loading new workspace")
            return False

    def open_existing_workspace(self, test_mode: bool, file = None):
        try:
            #if test_mode == False:
                #file = QFileDialog.getOpenFileName(caption="Open existing Workspace")[0]

                #if file != "":
                    #if test_mode == False:
                        #startup_window.close()
            worspace1 = Workspace("W1", "C:\\Users\\eyanm\\PracticumGUI\\TestSpace")
            project1 = Project("P1")
            project2 = Project("P2")
            worspace1.add_project(project1)
            worspace1.add_project(project2)
            dataset1 = Dataset("D1","C:\\Users\\eyanm\\PracticumGUI\\TestSpace\\.W1\\P1")
            dataset2 = Dataset("D2", "C:\\Users\\eyanm\\PracticumGUI\\TestSpace\\.W1\\P1")
            dataset3 = Dataset("D3", "C:\\Users\\eyanm\\PracticumGUI\\TestSpace\\.W1\\P2")
            project1.add_dataset(dataset1)
            project1.add_dataset(dataset2)
            project2.add_dataset(dataset3)
            pcap1 = Pcap("sample2.pcap", "C:\\Users\\eyanm\\PracticumGUI\\TestSpace\\.W1\\P1\\D1", "C:\\Users\\eyanm\\PracticumGUI\\sample2.pcap")
            pcap2 = Pcap("sample3.pcap", "C:\\Users\\eyanm\\PracticumGUI\\TestSpace\\.W1\\P1\\D1", "C:\\Users\\eyanm\\PracticumGUI\\sample3.pcap")
            pcap3 = Pcap("sample4.pcap", "C:\\Users\\eyanm\\PracticumGUI\\TestSpace\\.W1\\P1\\D1", "C:\\Users\\eyanm\\PracticumGUI\\sample4.pcap")
            pcap4 = Pcap("sample2.pcap", "C:\\Users\\eyanm\\PracticumGUI\\TestSpace\\.W1\\P1\\D2", "C:\\Users\\eyanm\\PracticumGUI\\sample2.pcap")
            dataset1.add_pcap(pcap1)
            dataset1.add_pcap(pcap2)
            dataset1.add_pcap(pcap3)
            dataset2.add_pcap(pcap2)

            workspaceUI = Workspace_UI("W1", worspace1,existing_flag=True)
            workspaceUI.show()
            return True

        except:
            traceback.print_exc()
            return False

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