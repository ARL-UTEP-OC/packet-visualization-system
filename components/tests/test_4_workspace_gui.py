import sys
import traceback

import PyQt5
import pytest
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QInputDialog, QMenu, QFileDialog, QAction, QMessageBox, QTreeWidget

from components.models.dataset import Dataset
from components.models.pcap import Pcap
from components.models.project import Project
from components.models.workspace import Workspace
from components.backend_components import Wireshark
from components.ui_components.workspace_gui import Workspace_UI

@pytest.fixture()
def workspace_object():
    workspace_object = Workspace(name="Test Workspace", location="C:\\Users\\eyanm\\PracticumGUI\\TestSpace")
    project1 = Project("P1")
    workspace_object.add_project(project1)
    dataset1 = Dataset("D1", "C:\\Users\\eyanm\\PracticumGUI\\TestSpace\\.Test Workspace\\P1")
    project1.add_dataset(dataset1)
    pcap1 = Pcap("sample2.pcap", "C:\\Users\\eyanm\\PracticumGUI\\TestSpace\\.Test Workspace\\P1\\D1",
                 "C:\\Users\\eyanm\\PracticumGUI\\sample2.pcap")
    dataset1.add_pcap(pcap1)
    return workspace_object

def test_workspace_setup():
    global workspace_object, test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    workspace_object = Workspace(name="Test Workspace", location="C:\\Users\\eyanm\\PracticumGUI\\TestSpace")
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object)

    assert test_workspace.size() == PyQt5.QtCore.QSize(917, 548)
    assert test_workspace.project_tree.geometry() == QtCore.QRect(0, 62, 221, 451)
    assert test_workspace.add_project_button.geometry() == QtCore.QRect(0, 22, 221, 41)
    assert test_workspace.add_project_button.text() == "Add a Project"
    assert test_workspace.add_pcap_button.geometry() == QtCore.QRect(370, 22, 111, 31)
    assert test_workspace.add_pcap_button.text() == "Add Pcap"
    assert test_workspace.add_dataset_button.geometry() == QtCore.QRect(240, 22, 111, 31)
    assert test_workspace.add_dataset_button.text() == "Add Dataset"
    assert test_workspace.open_in_wireshark_button.geometry() == QtCore.QRect(500, 22, 111, 31)
    assert test_workspace.open_in_wireshark_button.text() == "Export to Wireshark"

def test_collect_path_and_name():
    global workspace_object, test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    workspace_object = Workspace(name="Test Workspace", location="C:\\Users\\eyanm\\PracticumGUI\\TestSpace")
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object)

    full_path = "C:\\Users\\eyanm\\PracticumGUI\\TestSpace"
    assert test_workspace.collect_path_and_name(full_path) == ("C:\\Users\\eyanm\\PracticumGUI", "TestSpace")

    full_path = "C:/Users/eyanm/PracticumGUI/TestSpace"
    assert test_workspace.collect_path_and_name(full_path) == ("C:/Users/eyanm/PracticumGUI", "TestSpace")

    full_path = "C:\\Users\\eyanm\\PycharmProjects\\packet-visualize\\components\\tests\\examples\\myWorkspace\\myProject1\\myDataset1\\sample1.pcap"
    assert test_workspace.collect_path_and_name(full_path) == ("C:\\Users\\eyanm\\PycharmProjects\\packet-visualize\\components\\tests\\examples\\myWorkspace\\myProject1\\myDataset1", "sample1.pcap")

def test_get_pcap_path():
    global workspace_object, test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    workspace_object = Workspace(name="Test Workspace", location="C:\\Users\\eyanm\\PracticumGUI\\TestSpace")
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object, test_mode= True)

    assert test_workspace.get_pcap_path("") == (None, None, "")

def test_check_if_item_is(workspace_object):
    global test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object, test_mode=True, existing_flag=True)

    item = QtWidgets.QTreeWidgetItem()
    item.setText(0, "P1")
    assert test_workspace.check_if_item_is(item, "Project") == True

    item.setText(0, "D1")
    assert  test_workspace.check_if_item_is(item, "Dataset") == True

    item.setText(0, "sample2.pcap")
    assert test_workspace.check_if_item_is(item, "Dataset") == False

def test_open_new_workspace():
    global workspace_object, test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    workspace_object = Workspace(name="Test Workspace", location="C:\\Users\\eyanm\\PracticumGUI\\TestSpace")
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object, test_mode=True)

    assert test_workspace.open_new_workspace(file= "C:\\Users\\eyanm\\PracticumGUI\\TestSpace") == True
    assert test_workspace.open_new_workspace(file="") == None

def test_generate_existing_workspace(workspace_object):
    global test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object, test_mode=True)

    assert test_workspace.generate_existing_workspace() == True

def test_open_in_wireshark(workspace_object):
    global test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object, test_mode=True, existing_flag=True)

    pcap_item = QtWidgets.QTreeWidgetItem()
    pcap_item.setText(0, "sample2.pcap")
    assert test_workspace.open_in_wireshark(pcap_item=pcap_item) == True

    pcap_item.setText(0, "")
    assert test_workspace.open_in_wireshark(pcap_item=pcap_item) == None

def test_add_project(workspace_object):
    global test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object, test_mode=True, existing_flag=True)

    assert test_workspace.add_project("P1") == False
    assert test_workspace.add_project("P3") == True

def test_remove_project(workspace_object):
    global test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object, test_mode=True, existing_flag=True)

    item = QtWidgets.QTreeWidgetItem()
    item.setText(0, "P1")
    assert test_workspace.remove_project(item) == True

    item.setText(0, "P2")
    assert test_workspace.remove_project(item) == False

def test_add_dataset(workspace_object):
    global test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object, test_mode=True, existing_flag=True)

    pcap1 = Pcap("sample2.pcap", "C:\\Users\\eyanm\\PracticumGUI\\TestSpace\\.Test Workspace\\P1\\D1",
                 "C:\\Users\\eyanm\\PracticumGUI\\sample2.pcap")
    text = "D2"

    item = QtWidgets.QTreeWidgetItem()
    item.setText(0, "P1")

    assert test_workspace.add_dataset(text, pcap1, item) == True
    assert test_workspace.add_dataset("D1", pcap1, item) == False

def test_remove_dataset(workspace_object):
    global test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object, test_mode=True, existing_flag=True)

    item = QtWidgets.QTreeWidgetItem()
    item.setText(0, "D1")

    parent = QtWidgets.QTreeWidgetItem()
    parent.setText(0, "Parent")
    parent.addChild(item)

    assert test_workspace.remove_dataset(item) == True

    item.setText(0, "")
    assert test_workspace.remove_dataset(item) == False

def test_add_pcap(workspace_object):
    global test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object, test_mode=True, existing_flag=True)

    pcap1 = Pcap("sample2.pcap", "C:\\Users\\eyanm\\PracticumGUI\\TestSpace\\.Test Workspace\\P1\\D1",
                 "C:\\Users\\eyanm\\PracticumGUI\\sample2.pcap")

    item = QtWidgets.QTreeWidgetItem()
    item.setText(0, "D1")

    assert test_workspace.add_pcap(item, pcap1) == True

    item.setText(0, "")
    assert test_workspace.add_pcap(item, pcap1) == False








