import os
import shutil
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
from components.backend_components.load import Load

@pytest.fixture(scope="session")
def workspace_object():
    cwd = os.getcwd()
    original_cwd = os.getcwd()
    file = os.path.join(cwd, "components", "tests", "examples", "myWorkspace", "myProject1", "myDataset1",
                        "sample2.pcap")
    workspace_object = Workspace(name="Test Workspace", location=cwd)
    project1 = Project("P1")
    workspace_object.add_project(project1)
    cwd = os.path.join(cwd, ".Test Workspace", "P1")
    dataset1 = Dataset("D1", project1.path)
    project1.add_dataset(dataset1)
    cwd = os.path.join(cwd, "D1")
    pcap_path = os.getcwd()
    pcap1 = Pcap("sample2.pcap", dataset1.path,
                 file)
    dataset1.add_pcap(pcap1)
    yield workspace_object
    print("++++Teardown++++")
    cwd = os.getcwd()
    os.chdir("..")
    base = os.path.basename(cwd)
    try:
        if os.path.isdir(cwd) and base == ".Test Workspace":
            shutil.rmtree(cwd)
    except:
        print(".Test Workspace was not removed properly")

def test_workspace_setup():
    global workspace_object, test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    workspace_object = Workspace(name="Test Workspace", location=os.getcwd())
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
    workspace_object.__del__()

def test_collect_path_and_name():
    global workspace_object, test_workspace
    full_path = os.getcwd()
    partial_path = os.path.dirname(full_path)
    base = os.path.basename(full_path)

    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    workspace_object = Workspace(name="Test Workspace", location=full_path)
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object)

    assert test_workspace.collect_path_and_name(full_path) == (partial_path, base)
    workspace_object.__del__()

def test_get_pcap_path():
    global workspace_object, test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    workspace_object = Workspace(name="Test Workspace", location=os.getcwd())
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object, test_mode= True)
    test_workspace.test_mode = True

    assert test_workspace.get_pcap_path("") == (None, None, "")
    workspace_object.__del__()

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

'''
def test_open_new_workspace():
    global workspace_object, test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    cwd = os.getcwd()
    workspace_object = Workspace(name="Test Workspace", location=os.getcwd())
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object, test_mode=True)

    assert test_workspace.open_new_workspace(file=os.path.join(cwd, "TestSpace")) == True
    assert test_workspace.open_new_workspace(file="") == None

'''

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

    dataset_item = QtWidgets.QTreeWidgetItem()
    dataset_item.setText(0, "D1")
    assert test_workspace.open_in_wireshark(None, dataset_item, True) == True

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

    cwd = os.getcwd()
    file = os.path.join(cwd, "..", "components", "tests", "examples", "myWorkspace", "myProject1", "myDataset1",
                        "sample2.pcap")
    file = os.path.normpath(file)
    print(file)
    #cwd = os.path.join(cwd, "P1", "D1")
    #pcap1 = Pcap("sample2.pcap", cwd,
    #             file)
    text = "D2"

    item = QtWidgets.QTreeWidgetItem()
    item.setText(0, "P1")
    print(test_workspace.check_if_item_is(item, "Project"))
    assert test_workspace.add_dataset(text, file, item) == True
    assert test_workspace.add_dataset("D1", file, item) == False
'''
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

    os.chdir("..")
    cwd = os.getcwd()
    file = os.path.join(cwd, "examples", "myWorkspace", "myProject1", "myDataset1",
                        "sample3.pcap")

    cwd = os.path.join(cwd, ".Test Workspace", "P1", "D1")
    pcap1 = Pcap("sample3.pcap", cwd, file)

    item = QtWidgets.QTreeWidgetItem()
    item.setText(0, "D1")

    assert test_workspace.add_pcap(item, pcap1) == True

    item.setText(0, "")
    assert test_workspace.add_pcap(item, pcap1) == False

def test_remove_pcap(workspace_object):
    global test_workspace
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    test_workspace = Workspace_UI(workspace_name="Test Worskpace", workspace_object=workspace_object, test_mode=True, existing_flag=True)

    item = QtWidgets.QTreeWidgetItem()
    item.setText(0, "sample2.pcap")

    parent = QtWidgets.QTreeWidgetItem()
    parent.addChild(item)

    assert test_workspace.remove_pcap(item) == True

    item.setText(0, "")
    assert test_workspace.remove_pcap(item) == False
'''






