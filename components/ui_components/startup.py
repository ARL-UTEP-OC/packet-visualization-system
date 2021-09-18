import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from workspace import Workspace


class Ui_startup_window(object):
    def setupUi(self, startup_window):
        startup_window.setObjectName("startup_window")
        startup_window.setFixedSize(248, 121)
        self.centralwidget = QtWidgets.QWidget(startup_window)
        self.centralwidget.setObjectName("centralwidget")

        self.new_workspace_button = QtWidgets.QPushButton(self.centralwidget, clicked = lambda: self.open_new_workspace_placeholder())
        self.new_workspace_button.clicked.connect(lambda : startup_window.close())
        self.new_workspace_button.setGeometry(QtCore.QRect(40, 20, 171, 31))
        self.new_workspace_button.setObjectName("new_workspace_button")


        self.existing_workspace_button = QtWidgets.QPushButton(self.centralwidget, clicked = lambda: self.open_existing_workspace())
        self.existing_workspace_button.setGeometry(QtCore.QRect(40, 70, 171, 31))
        self.existing_workspace_button.setObjectName("existing_workspace_button")

        startup_window.setCentralWidget(self.centralwidget)
        self.retranslateUi(startup_window)
        QtCore.QMetaObject.connectSlotsByName(startup_window)

    def open_new_workspace(self):
        file = QFileDialog.getSaveFileName(caption="Save Workspace")
        file_split = file[0].split("/")
        workspace_name = file_split[-1]
        if file != ('', ''):
            #Save the new workspace

            self.workspace = Workspace()
            self.workspace.show()

    def open_new_workspace_placeholder(self):
        self.workspace = Workspace()
        self.workspace.show()

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