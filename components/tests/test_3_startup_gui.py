import sys

import PyQt5
from PyQt5 import QtCore, QtWidgets

from components.ui_components.startup_gui import Ui_startup_window

def setup_module(module):
    global app, startup_window, ui

    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    startup_window = QtWidgets.QMainWindow()
    ui = Ui_startup_window()
    ui.setupUi(test_mode= True)

def test_setupUI():
    assert ui.startup_window.size() == PyQt5.QtCore.QSize(248, 121)
    assert ui.new_workspace_button.geometry() == PyQt5.QtCore.QRect(40, 20, 171, 31)
    assert ui.existing_workspace_button.geometry() == PyQt5.QtCore.QRect(40, 70, 171, 31)

def test_collect_path_and_name():
    full_path = "C:\\Users\\eyanm\\PracticumGUI\\TestSpace"
    assert Ui_startup_window.collect_path_and_name(ui, full_path) == ("C:\\Users\\eyanm\\PracticumGUI", "TestSpace")

    full_path = "C:/Users/eyanm/PracticumGUI/TestSpace"
    assert Ui_startup_window.collect_path_and_name(ui, full_path) == ("C:/Users/eyanm/PracticumGUI", "TestSpace")

def test_open_new_workspace():
    assert Ui_startup_window.open_new_workspace(ui, True, "") == None
    assert Ui_startup_window.open_new_workspace(ui, True,"C:\\Users\\eyanm\\PracticumGUI") == True

def test_retranslateUI():
    ui.retranslateUi()
    assert ui.startup_window.windowTitle() == "Startup"
    assert ui.new_workspace_button.text() == "Start a new Workspace"
    assert ui.existing_workspace_button.text() == "Open an existing Workspace"
