# import os
# import sys

# import PyQt5
# from PyQt5 import QtCore, QtWidgets

# from packetvisualization.ui_components.startup_gui import Ui_startup_window

# cwd = None

# def setup_module():
#     global app, startup_window, ui, cwd

#     cwd = os.getcwd()
#     QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
#     app = QtWidgets.QApplication(sys.argv)
#     startup_window = QtWidgets.QMainWindow()
#     ui = Ui_startup_window()
#     ui.setupUi(test_mode= True)

# def teardown_module():
#     global cwd
#     os.chdir(cwd)

# def test_setupUI():
#     assert ui.startup_window.size() == PyQt5.QtCore.QSize(248, 121)
#     assert ui.new_workspace_button.geometry() == PyQt5.QtCore.QRect(40, 20, 171, 31)
#     assert ui.existing_workspace_button.geometry() == PyQt5.QtCore.QRect(40, 70, 171, 31)

# def test_collect_path_and_name():
#     full_path = os.getcwd()
#     partial_path = os.path.dirname(full_path)
#     base = os.path.basename(full_path)
#     assert Ui_startup_window.collect_path_and_name(ui, full_path) == (partial_path, base)

# def test_open_new_workspace():
#     assert Ui_startup_window.open_new_workspace(ui, True, "") == None
#     assert Ui_startup_window.open_new_workspace(ui, True, os.getcwd()) == True

# def test_retranslateUI():
#     ui.retranslateUi()
#     assert ui.startup_window.windowTitle() == "Startup"
#     assert ui.new_workspace_button.text() == "Start a new Workspace"
#     assert ui.existing_workspace_button.text() == "Open an existing Workspace"
