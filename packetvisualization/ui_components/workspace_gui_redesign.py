import os
import platform as pf
import shutil
import sys
import traceback
import webbrowser
import zipfile

import plotly.offline as po
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from PyQt5.QtWebEngineWidgets import QWebEngineView
from scapy.all import *
from datetime import datetime

from PyQt5.QtCore import Qt, QRect, QObject, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QIcon, QKeySequence
from PyQt5.QtWidgets import QMainWindow, QTreeWidget, QPushButton, QVBoxLayout, QProgressBar, QMenu, QWidget, QLabel, \
    QAction, QMessageBox, QDockWidget, QTextEdit, QInputDialog, QTreeWidgetItem, QFileDialog, QApplication, QToolBar, \
    QTableWidgetItem

from packetvisualization.backend_components.bandwidth_plot import create_plot
from packetvisualization.backend_components.controller import Controller
from packetvisualization.backend_components.entity_operator import EntityOperations
from packetvisualization.backend_components.load import Load
from packetvisualization.models.context.database_context import DbContext
from packetvisualization.models.dataset import Dataset
from packetvisualization.models.pcap import Pcap
from packetvisualization.models.project import Project
from packetvisualization.models.workspace import Workspace
from packetvisualization.backend_components import Wireshark
from packetvisualization.ui_components import filter_gui
from packetvisualization.ui_components.plot_worker import PlotWorker
from packetvisualization.ui_components.table_gui import table_gui


class WorkspaceWindow(QMainWindow):
    """Main GUI windows for the PacketVisualization software. A user can create/delete a project and add/delete a
    dataset to a project. A user can then add/delete a PCAP to a dataset where analysis can be performed on the whole
    dataset or selected packets.
    """
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    # logo = os.path.join(os.path.dirname(__file__), "images", "logo.png")
    app.setWindowIcon(QIcon(":logo.png"))

    def __init__(self, workspace_path: str, existing_flag: bool = False) -> None:
        """Initialization function for a new workspace window.

        :param workspace_path: directory where workspace is saved
        :type workspace_path: str
        :param existing_flag: flag set if opening an existing workspace
        :type existing_flag: bool
        """
        super().__init__()
        self.eo = EntityOperations()
        self.db = None
        # self.icons = os.path.join(os.path.dirname(__file__), "images", "svg")
        # self.logo = os.path.join(os.path.dirname(__file__), "images", "logo.png")
        self.test_mode = False
        if existing_flag:
            self.workspace_object = Load().open_zip(workspace_path)
            restore_path = os.path.join(self.workspace_object.dump_path, self.workspace_object.name)
            print(restore_path)
            self.eo.restore_db(self.workspace_object.name, restore_path)
            self.db = self.eo.set_db(self.workspace_object.name)
        else:
            self.workspace_object = Workspace(name=os.path.basename(workspace_path),
                                              location=os.path.dirname(workspace_path))
            self.workspace_object.create_dump_dir(self.workspace_object.dump_path)
            self.db = self.eo.create_db(self.workspace_object.name)  # create DB with workspace name
        self.setWindowTitle("PacketVisualizer - " + self.workspace_object.name)
        self.resize(1000, 600)

        # Docked widget for Project Tree
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabels(["Item Name", "Size", "DoC"])
        self.project_tree.setColumnWidth(0, 200)
        self.dock_project_tree = QDockWidget("Project Tree Window", self)
        self.dock_project_tree.setWidget(self.project_tree)
        self.dock_project_tree.setFloating(False)

        self.traced_dataset = None
        self.traced_data = None
        # Docked widget for Bandwidth vs. Time Graph
        self.plot_x = []
        self.plot_y = []
        self.fig_view = QWebEngineView()
        self.fig_view.setHtml(create_plot(self.plot_x, self.plot_y))
        self.dock_plot = QDockWidget("Bandwidth vs. Time Window", self)
        self.dock_plot.setWidget(self.fig_view)
        self.dock_plot.setFloating(False)

        # Docked widget for Classifier
        self.classifier_plot_view = QWebEngineView()
        # TODO: X and Y data is going to be provided by Classifier class, once that happens we can fix this.
        data_frame = pd.DataFrame()
        data_frame['instance_number'] = [3, 2, 1]
        data_frame['cluster'] = [1, 2, 3]
        self.create_classifier_plot(data_frame)
        self.classifier_window = QDockWidget("Cluster per instance", self)
        self.classifier_window.setWidget(self.classifier_plot_view)
        self.classifier_window.setFloating(False)
        self.classifier_window.close()

        self.setCentralWidget(self.dock_project_tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_project_tree)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_plot)
        self.addDockWidget(Qt.RightDockWidgetArea, self.classifier_window)

        self._create_actions()
        self._create_menu_bar()
        self._create_tool_bar()
        self._connect_actions()
        self._create_status_bar()

        self.context = DbContext()
        # self.db = self.context.db  # here
        self.controller = Controller()

        if existing_flag:
            self.generate_existing_workspace()

    def run(self):
        self.show()
        sys.exit(self.app.exec_())

    def _create_actions(self) -> None:
        """Creates all actions that will be used in the application
        """
        # File Menu Actions
        self.newProjectAction = QAction(QIcon(":add-circle.svg"), "New &Project", self)
        self.newProjectAction.setShortcut("Ctrl+N")
        self.newProjectAction.setStatusTip("Create a new project")
        self.newProjectAction.setToolTip("Create a new project")

        self.newDatasetAction = QAction("New &Dataset", self)
        self.newDatasetAction.setStatusTip("Create a new dataset")
        self.newDatasetAction.setToolTip("Create a new dataset")

        self.newPCAPAction = QAction("New P&CAP", self)
        self.newPCAPAction.setStatusTip("Create a new pcap")
        self.newPCAPAction.setToolTip("Create a new pcap")

        self.filterWiresharkAction = QAction("Filter Wireshark", self)

        self.openNewAction = QAction("&New Workspace", self)
        self.openNewAction.setStatusTip("Open a new workspace")
        self.openNewAction.setToolTip("Open a new workspace")

        self.openExistingAction = QAction("&Existing Workspace", self)
        self.openExistingAction.setStatusTip("Open existing workspace")
        self.openExistingAction.setToolTip("Open existing workspace")

        self.saveAction = QAction(QIcon(":save.svg"), "&Save", self)
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.setStatusTip("Save workspace")
        self.saveAction.setToolTip("Save workspace")

        self.traceAction = QAction(QIcon(":pulse.svg"), "&Trace", self)
        self.traceAction.setShortcut("Ctrl+T")
        self.traceAction.setStatusTip("Trace dataset on Bandwidth vs Time graph")
        self.traceAction.setToolTip("race dataset on Bandwidth vs Time graph")

        self.exportCsvAction = QAction("Export Dataset/PCAP to &CSV", self)
        self.exportCsvAction.setStatusTip("Export Dataset/PCAP to CSV")
        self.exportCsvAction.setToolTip("Export Dataset/PCAP to CSV")

        self.exportJsonAction = QAction("Export Dataset/PCAP to &JSON", self)
        self.exportJsonAction.setStatusTip("Export Dataset/PCAP to JSON")
        self.exportJsonAction.setToolTip("Export Dataset/PCAP to JSON")

        self.exitAction = QAction("E&xit", self)
        self.exitAction.setShortcut("Alt+F4")
        self.exitAction.setStatusTip("Exit workspace")
        self.exitAction.setToolTip("Exit workspace")

        # Edit Menu Actions
        self.cutAction = QAction(QIcon(":cut.svg"), "Cu&t", self)
        self.cutAction.setShortcut(QKeySequence.Cut)
        self.cutAction.setEnabled(False)

        self.copyAction = QAction(QIcon(":copy.svg"), "&Copy", self)
        self.copyAction.setShortcut(QKeySequence.Copy)
        self.copyAction.setEnabled(False)

        self.pasteAction = QAction(QIcon(":clipboard.svg"), "&Paste", self)
        self.pasteAction.setShortcut(QKeySequence.Paste)
        self.pasteAction.setEnabled(False)

        self.deleteAction = QAction(QIcon(":trash.svg"), "&Delete", self)
        self.deleteAction.setShortcut("Del")
        self.deleteAction.setStatusTip("Remove selected item")
        self.deleteAction.setToolTip("Remove item")

        # View Menu Actions
        self.gen_table_action = QAction(QIcon(":list.svg"), "&Packet Table", self)
        self.gen_table_action.setStatusTip("View Packets in a PCAP")
        self.gen_table_action.setToolTip("View Packets in a PCAP")

        # self.gen_table_action = QAction(QIcon(os.path.join(self.icons, "list.svg")), "&Packet Table", self)
        self.classifier_action = QAction("&Classify Packets", self)
        self.classifier_action.setStatusTip("Classify selected pcap data")
        self.classifier_action.setToolTip("Classify selected pcap data")

        # Wireshark Menu Actions
        self.openWiresharkAction = QAction(QIcon(":wireshark-icon.png"), "Open &Wireshark", self)
        self.openWiresharkAction.setShortcut("Ctrl+W")
        self.openWiresharkAction.setStatusTip("Open dataset or pcap in Wireshark")
        self.openWiresharkAction.setToolTip("Open dataset or pcap in Wireshark")

        # Window Menu Actions
        self.openProjectTreeAction = QAction(QIcon(":git-branch.svg"), "&Project Tree Window", self)
        self.openProjectTreeAction.setStatusTip("Open project tree window")
        self.openProjectTreeAction.setToolTip("Open project tree window")

        self.openPlotAction = QAction(QIcon(":time-outline.svg"), "&Bandwidth vs. Time Window", self)
        self.openPlotAction.setStatusTip("Open Bandwidth vs. Time window")
        self.openPlotAction.setToolTip("Open Bandwidth vs. Time window")

        # Help Menu Actions
        self.helpContentAction = QAction(QIcon(":help.svg"), "&Help Content", self)
        self.aboutAction = QAction("&About", self)
        self.aboutAction.setEnabled(False)

    def _connect_actions(self) -> None:
        """Connects all actions to a method to be executed
        """
        # Connect File actions
        self.openNewAction.triggered.connect(self.open_new_workspace)
        self.newProjectAction.triggered.connect(self.new_project)
        self.newDatasetAction.triggered.connect(self.new_dataset)
        self.newPCAPAction.triggered.connect(self.new_pcap)
        self.openExistingAction.triggered.connect(self.open_existing_workspace)
        self.saveAction.triggered.connect(self.save)
        self.exitAction.triggered.connect(self.exit)
        self.traceAction.triggered.connect(self.trace_dataset)
        self.exportCsvAction.triggered.connect(self.export_csv)
        self.exportJsonAction.triggered.connect(self.export_json)

        # Connect Edit actions
        self.cutAction.triggered.connect(self.cut_content)
        self.copyAction.triggered.connect(self.copy_content)
        self.pasteAction.triggered.connect(self.paste_content)
        self.deleteAction.triggered.connect(self.delete)

        # Connect View actions
        self.gen_table_action.triggered.connect(self.gen_table)
        self.classifier_action.triggered.connect(self.display_classifier_options)

        # Connect Wireshark actions
        self.openWiresharkAction.triggered.connect(self.open_wireshark)
        self.filterWiresharkAction.triggered.connect(self.filter_wireshark)

        # Connect Windows actions
        self.openProjectTreeAction.triggered.connect(self.open_window_project_tree)
        self.openPlotAction.triggered.connect(self.open_window_plot)

        # Connect Help actions
        self.helpContentAction.triggered.connect(self.help_content)
        self.aboutAction.triggered.connect(self.about)

    def _create_menu_bar(self) -> None:
        """Creates the top menu bar where all actions can be accessed
        """
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")
        new_menu = file_menu.addMenu("&New...")
        new_menu.addAction(self.newProjectAction)
        new_menu.addAction(self.newDatasetAction)
        new_menu.addAction(self.newPCAPAction)
        open_menu = file_menu.addMenu(QIcon(":folder.svg"), "&Open...")
        open_menu.addAction(self.openNewAction)
        open_menu.addAction(self.openExistingAction)
        file_menu.addAction(self.saveAction)
        file_menu.addSeparator()
        file_menu.addAction(self.traceAction)
        file_menu.addSeparator()
        export_menu = file_menu.addMenu("&Export")
        export_menu.addAction(self.exportCsvAction)
        export_menu.addAction(self.exportJsonAction)
        file_menu.addSeparator()
        file_menu.addAction(self.exitAction)

        # Edit Menu
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.cutAction)
        edit_menu.addAction(self.copyAction)
        edit_menu.addAction(self.pasteAction)
        edit_menu.addSeparator()
        edit_menu.addAction(self.deleteAction)

        # View Menu
        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(self.gen_table_action)
        view_menu.addAction(self.classifier_action)

        # Wireshark Menu
        wireshark_menu = menu_bar.addMenu('Wire&shark')
        wireshark_menu.addAction(self.openWiresharkAction)

        # Window Menu
        windows_menu = menu_bar.addMenu('&Window')
        windows_menu.addAction(self.openPlotAction)
        windows_menu.addAction(self.openProjectTreeAction)

        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction(self.helpContentAction)
        help_menu.addAction(self.aboutAction)

    def _create_tool_bar(self) -> None:
        """Creates a tool bar for quick access to come actions
        """
        file_tool_bar = QToolBar("File")
        self.addToolBar(Qt.LeftToolBarArea, file_tool_bar)
        file_tool_bar.addAction(self.newProjectAction)
        file_tool_bar.addAction(self.saveAction)
        file_tool_bar.addAction(self.deleteAction)

    def _create_status_bar(self) -> None:
        """Creates a status bar to keep track of task progress
        """
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready", 3000)

        self.progressbar = QProgressBar()
        self.progressbar.setFixedSize(250, 12)
        self.progressbar.setTextVisible(False)
        self.progressbar.setStyleSheet("QProgressBar::chunk {background-color: grey;}")
        self.status_bar.addPermanentWidget(self.progressbar)
        self.progressbar.hide()

    def contextMenuEvent(self, event) -> None:
        # Right Click Menu
        menu = QMenu(self.project_tree)

        if self.project_tree.selectedItems():
            # Right-click a project
            if type(self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Project:
                menu.addAction(self.newDatasetAction)
            # Right-click a dataset
            if type(self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Dataset:
                menu.addAction(self.newPCAPAction)
                menu.addAction(self.traceAction)
                menu.addAction(self.openWiresharkAction)
                menu.addAction(self.filterWiresharkAction)
                menu.addAction(self.classifier_action)
                view_menu = menu.addMenu("View")
                view_menu.addAction(self.gen_table_action)
                export_menu = menu.addMenu("Export")
                export_menu.addAction(self.exportCsvAction)
                export_menu.addAction(self.exportJsonAction)
            # Right-click a pcap
            if type(self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Pcap:
                menu.addAction(self.openWiresharkAction)
                export_menu = menu.addMenu("View")
                export_menu.addAction(self.gen_table_action)
                export_menu = menu.addMenu("Export")
                export_menu.addAction(self.exportCsvAction)
                export_menu.addAction(self.exportJsonAction)

        separator1 = QAction(self)
        separator1.setSeparator(True)
        menu.addAction(separator1)
        menu.addAction(self.cutAction)
        menu.addAction(self.copyAction)
        menu.addAction(self.pasteAction)
        menu.addAction(self.deleteAction)

        separator2 = QAction(self)
        separator2.setSeparator(True)
        menu.addAction(separator2)
        menu.addAction(self.newProjectAction)

        menu.exec(event.globalPos())

    def new_project(self, text=None):
        # Logic for creating a new project
        if not self.test_mode:
            text = QInputDialog.getText(self, "Project Name Entry", "Enter Project name:")[0]
        if not self.project_tree.findItems(text, Qt.MatchRecursive, 0) or self.test_mode == True:
            project = Project(name=text, parent_path=self.workspace_object.path)
            self.workspace_object.add_project(project)
            item = QTreeWidgetItem(self.project_tree)
            item.setData(0, Qt.UserRole, project)
            item.setText(0, text)
        else:
            print("Item named " + text + " already exists")
            traceback.print_exc()

    def new_dataset(self, text=None, file=None, project=None):
        # Logic for creating a new dataset
        try:
            pcap_path = ""
            pcap_name = ""
            if type(self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Project or self.test_mode == True:
                if not self.test_mode:
                    text = QInputDialog.getText(self, "Dataset Name Entry", "Enter Dataset name:")[0]
                if not self.project_tree.findItems(text, Qt.MatchRecursive, 0) and text != "":
                    if not self.test_mode:
                        pcap_path, pcap_name, file, extension = self.get_pcap_path()
                    else:
                        pcap_path, pcap_name = os.path.split(file)
                    if pcap_path is None:
                        return
                    if not self.test_mode:
                        project = self.project_tree.selectedItems()[0]

                    p = project.data(0, Qt.UserRole)
                    dataset = Dataset(name=text, parentPath=p.path)

                    p.add_dataset(dataset)
                    child_item = QTreeWidgetItem()
                    child_item.setText(0, text)
                    child_item.setData(0, Qt.UserRole, dataset)

                    project.addChild(child_item)

                    new_pcap = Pcap(file=file, path=dataset.path, name=pcap_name)
                    if new_pcap.name is not None:
                        dataset.add_pcap(new=new_pcap)
                        pcap_item = QTreeWidgetItem()
                        pcap_item.setText(0, pcap_name)
                        pcap_item.setData(0, Qt.UserRole, new_pcap)
                        child_item.addChild(pcap_item)

                        mytable = self.db[dataset.name]
                        self.eo.insert_packets(new_pcap.json_file, mytable, dataset.name, new_pcap.name)
                    else:
                        child_item.parent().removeChild(child_item)
                        p.del_dataset(dataset)
        except Exception:
            traceback.print_exc()

    def new_pcap(self, dataset_item=None, file=None):
        # Logic for creating a new pcap
        try:
            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Dataset or self.test_mode:

                if not self.test_mode:
                    pcap_path, pcap_name, file, extension = self.get_pcap_path()
                else:
                    pcap_path, pcap_name = os.path.split(file)
                if pcap_path is None:
                    return
                if not self.test_mode:
                    dataset_item = self.project_tree.selectedItems()[0]

                d = dataset_item.data(0, Qt.UserRole)
                new_pcap = Pcap(file=file, path=d.path, name=pcap_name)

                for cap in d.pcaps:
                    if new_pcap.name == cap.name:
                        return

                if new_pcap.name is not None and new_pcap not in d.pcaps:
                    d.add_pcap(new_pcap)
                    pcap_item = QTreeWidgetItem()
                    pcap_item.setText(0, pcap_name)
                    pcap_item.setData(0, Qt.UserRole, new_pcap)
                    dataset_item.addChild(pcap_item)

                    mytable = self.db[d.name]
                    self.eo.insert_packets(new_pcap.json_file, mytable, d.name, new_pcap.name)
                if self.traced_dataset:
                    self.update_traced_data()
        except Exception:
            print("Error loading this pcap")
            traceback.print_exc()

    def open_new_workspace(self) -> None:
        """Prompts user to select save location and opens up a new workspace window
        """
        directory = QFileDialog.getSaveFileName(caption="Choose Workspace location")[0]

        if directory != '':
            self.new_window = WorkspaceWindow(workspace_path=directory)
            self.new_window.show()

    def open_existing_workspace(self) -> None:
        """Prompts user to select saved zip file and opens an existing workspace window
        """
        file_filter = "zip(*.zip)"
        file_path = QFileDialog.getOpenFileName(caption="Open existing Workspace", filter=file_filter)[0]

        if file_path != "":
            if not self.test_mode:
                self.new_window = WorkspaceWindow(workspace_path=file_path, existing_flag=True)
                self.new_window.show()

    def trace_dataset(self):
        if self.project_tree.selectedItems() and type(
                self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Dataset:
            dataset_item = self.project_tree.selectedItems()[0]
            d = dataset_item.data(0, Qt.UserRole)
            self.traced_dataset = d
            self.update_traced_data()

    def export_csv(self):
        # Logic to export dataset or pcap to CSV
        try:
            if self.project_tree.selectedItems():
                input_file = ''
                if type(self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Dataset:
                    dataset_item = self.project_tree.selectedItems()[0]
                    dataset = dataset_item.data(0, Qt.UserRole)
                    input_file = dataset.mergeFilePath
                if type(self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Pcap:
                    pcap_item = self.project_tree.selectedItems()[0]
                    pcap = pcap_item.data(0, Qt.UserRole)
                    input_file = pcap.path

                if input_file != '':
                    output_file = QFileDialog.getSaveFileName(caption="Choose Output location", filter=".csv (*.csv)")[
                        0]

                    if pf.system() == "Windows":
                        os.system(
                            'cd "C:\Program Files\Wireshark" & tshark -r ' + input_file + ' -T fields -e frame.number -e '
                                                                                          'ip.src -e ip.dst '
                                                                                          '-e frame.len -e frame.time -e '
                                                                                          'frame.time_relative -e _ws.col.Info '
                                                                                          '-E header=y -E '
                                                                                          'separator=, -E quote=d -E '
                                                                                          'occurrence=f > ' + output_file)
                    elif pf.system() == "Linux":
                        os.system('tshark -r ' + input_file + ' -T fields -e frame.number -e '
                                                              'ip.src -e ip.dst '
                                                              '-e frame.len -e frame.time -e '
                                                              'frame.time_relative -e _ws.col.Info '
                                                              '-E header=y -E '
                                                              'separator=, -E quote=d -E '
                                                              'occurrence=f > ' + output_file)
                    self.status_bar.showMessage("Export CSV Successful", 3000)
                else:
                    self.status_bar.showMessage("No Dataset/PCAP selected to Export", 3000)
                return True
        except Exception:
            traceback.print_exc()

    def export_json(self):
        # Logic to export dataset or pcap to JSON
        try:
            if self.project_tree.selectedItems():
                input_file = ''
                if type(self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Dataset:
                    dataset_item = self.project_tree.selectedItems()[0]
                    dataset = dataset_item.data(0, Qt.UserRole)
                    input_file = dataset.mergeFilePath
                if type(self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Pcap:
                    pcap_item = self.project_tree.selectedItems()[0]
                    pcap = pcap_item.data(0, Qt.UserRole)
                    input_file = pcap.path

                if input_file != '':
                    output_file = \
                        QFileDialog.getSaveFileName(caption="Choose Output location", filter=".json (*.json)")[0]

                    if pf.system() == "Windows":
                        os.system(
                            'cd "C:\Program Files\Wireshark" & tshark -r ' + input_file + ' -T json > ' + output_file)
                    if pf.system() == "Linux":
                        os.system('tshark -r ' + input_file + ' -T json > ' + output_file)
                    self.status_bar.showMessage("Export JSON Successful", 3000)
                else:
                    self.status_bar.showMessage("No Dataset/PCAP selected to Export", 3000)
                return True
        except Exception:
            traceback.print_exc()

    def save(self) -> None:
        """ Function to save a workspace and all associated data
        """
        self.status_bar.showMessage("Saving...")

        self.eo.dump_db(self.workspace_object.name, self.workspace_object.dump_path)
        self.workspace_object.save()
        self.status_bar.showMessage("Saved", 3000)

    def delete(self, project_item=None, dataset_item=None, pcap_item=None):
        # Logic for deleting an item
        if self.project_tree.selectedItems():
            # Deleting a project
            if type(self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Project:
                if not self.test_mode:
                    project_item = self.project_tree.selectedItems()[0]
                p = project_item.data(0, Qt.UserRole)
                self.workspace_object.del_project(p)
                QTreeWidget.invisibleRootItem(self.project_tree).removeChild(project_item)
            # Deleting a dataset
            elif type(self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Dataset:
                if not self.test_mode:
                    dataset_item = self.project_tree.selectedItems()[0]
                d = dataset_item.data(0, Qt.UserRole)
                for p in self.workspace_object.project:
                    for d in p.dataset:
                        if d.name == dataset_item.text(0):
                            if self.traced_dataset and d.name == self.traced_dataset.name:
                                self.traced_dataset = None
                                self.eo.delete_collection(self.db[d.name])
                                self.update_traced_data()
                            p.del_dataset(old=d)
                            dataset_item.parent().removeChild(dataset_item)
            # Deleting a pcap
            elif type(self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Pcap:
                if not self.test_mode:
                    pcap_item = self.project_tree.selectedItems()[0]
                for p in self.workspace_object.project:
                    for d in p.dataset:
                        for cap in d.pcaps:
                            if cap.name == pcap_item.text(0):
                                d.del_pcap(cap)
                                pcap_item.parent().removeChild(pcap_item)
                                self.eo.delete_packets(self.db[d.name], "parent_pcap", cap.name)
                if self.traced_dataset:
                    self.update_traced_data()
        else:
            return False

    def exit(self) -> None:
        """Exit function that calls the close() function to stop the application
        """
        self.close()

    def cut_content(self):
        # Logic for cutting content
        print("<b>Edit > Cut<\b> clicked")

    def copy_content(self):
        # Logic for copying content
        print("<b>Edit > Copy<\b> clicked")

    def paste_content(self):
        # Logic for pasting content
        print("<b>Edit > Paste<\b> clicked")

    def open_window_project_tree(self):
        # Logic to open the project_tree window
        self.dock_project_tree.show()

    def open_window_plot(self):
        # Logic to open the plot window
        self.dock_plot.show()

    def open_wireshark(self, dataset_item=None, pcap_item=None, merge_flag=False):
        # Logic to open wireshark
        try:
            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Dataset or (
                    self.test_mode == True and merge_flag == True):
                if not self.test_mode:
                    dataset_item = self.project_tree.selectedItems()[0]
                d = dataset_item.data(0, Qt.UserRole)
                Wireshark.openwireshark(d.mergeFilePath)
                return True

            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Pcap or self.test_mode == True:
                if not self.test_mode:
                    pcap_item = self.project_tree.selectedItems()[0]
                cap = pcap_item.data(0, Qt.UserRole)
                if self.test_mode:
                    return True
                Wireshark.openwireshark(cap.pcap_file)
            else:
                return False
        except Exception:
            traceback.print_exc()
            return False

    def help_content(self):
        # Logic for help content
        webbrowser.open(os.path.join(os.path.dirname(__file__), "documents", "Packet_Visualization.pdf"))

    def about(self):
        # Logic for about
        print("<b>Help > About<\b> clicked")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Workspace Close", "Would you like to save this Workspace?",
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            self.save()
            self.eo.remove_db(self.workspace_object.name)
            self.workspace_object.__del__()
            if os.path.exists("tEmPpCaP.pcap"):
                os.remove("tEmPpCaP.pcap")
            if os.path.exists("tEmPmErGeCaP.pcap"):
                os.remove("tEmPmErGeCaP.pcap")
            event.accept()
        elif reply == QMessageBox.No:
            self.eo.remove_db(self.workspace_object.name)
            self.workspace_object.__del__()
            if os.path.exists("tEmPpCaP.pcap"):
                os.remove("tEmPpCaP.pcap")
            if os.path.exists("tEmPmErGeCaP.pcap"):
                os.remove("tEmPmErGeCaP.pcap")
            event.accept()
        else:
            event.ignore()

    def add_pcap_zip(self):
        try:
            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Dataset or self.test_mode:

                location = QFileDialog.getOpenFileName(caption="Select zip Folder of PCAP's", filter="zip (*.zip)")[0]
                dataset_item = self.project_tree.selectedItems()[0]
                dataset_obj = self.project_tree.selectedItems()[0].data(0, Qt.UserRole)
                extracted_folder = os.path.join(os.path.dirname(location), "ExtractedPV")
                with zipfile.ZipFile(location, 'r') as my_zip:
                    my_zip.extractall(extracted_folder)

                namelist = []
                for cap in dataset_obj.pcaps:
                    namelist.append(cap.name)

                for file in os.listdir(extracted_folder):
                    new_pcap = Pcap(file, dataset_obj.path, os.path.join(extracted_folder, file))
                    if new_pcap.name not in namelist:
                        dataset_obj.add_pcap(new_pcap)
                        pcap_item = QTreeWidgetItem()
                        pcap_item.setText(0, os.path.basename(file))
                        pcap_item.setData(0, Qt.UserRole, new_pcap)
                        dataset_item.addChild(pcap_item)

                shutil.rmtree(extracted_folder)
                return True
        except Exception:
            traceback.print_exc()

    def add_pcap_folder(self):
        try:
            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Dataset or self.test_mode:

                location = QFileDialog.getExistingDirectory(caption="Select Folder of PCAP's")
                dataset_item = self.project_tree.selectedItems()[0]
                dataset = self.project_tree.selectedItems()[0].data(0, Qt.UserRole)

                namelist = []
                for cap in dataset.pcaps:
                    namelist.append(cap.name)

                for file in os.listdir(location):
                    if new_pcap.name not in namelist:
                        new_pcap = Pcap(file, dataset.path, os.path.join(location, file))
                        dataset.add_pcap(new_pcap)
                        pcap_item = QTreeWidgetItem()
                        pcap_item.setText(0, os.path.basename(file))
                        pcap_item.setData(0, Qt.UserRole, new_pcap)
                        dataset_item.addChild(pcap_item)
                return True
        except Exception:
            traceback.print_exc()

    def analyze(self):
        if self.project_tree.selectedItems() and type(
                self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Dataset or self.test_mode == True:
            if not self.test_mode:
                text = QInputDialog.getText(self, "Analysis Name Entry", "Enter Analysis name:")[0]
            analysis_item = QTreeWidgetItem(self.analysis_tree)
            analysis_item.setText(0, text)
            return True

    def remove_analysis(self):
        return

    def gen_table(self):
        try:
            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Pcap:
                pcap_item = self.project_tree.selectedItems()[0]
                pcap_obj = pcap_item.data(0, Qt.UserRole)

                table = table_gui(pcap_obj, self.progressbar, self.db, self)
                self.dock_table = QDockWidget("Packet Table", self)
                self.dock_table.setWidget(table)
                self.dock_table.setFloating(False)
                self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_table)

            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Dataset:
                dataset_item = self.project_tree.selectedItems()[0]
                dataset_obj = dataset_item.data(0, Qt.UserRole)

                table = table_gui(dataset_obj, self.progressbar, self.db, self)
                self.dock_table = QDockWidget("Packet Table", self)
                self.dock_table.setWidget(table)
                self.dock_table.setFloating(False)
                self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_table)

            return
        except:
            traceback.print_exc()

    def get_pcap_path(self, full_path: str = None):
        file_filter = "Wireshark capture file (*.pcap)"
        initial_filter = "Wireshark capture file (*.pcap)"
        if not self.test_mode:
            full_path = QFileDialog.getOpenFileName(caption="Add a Pcap file to this Dataset", filter=file_filter,
                                                    initialFilter=initial_filter)[0]

        if full_path != "":
            name = os.path.basename(full_path)
            path = os.path.dirname(full_path)
            extension = os.path.splitext(full_path)[1]
            return path, name, full_path, extension
        else:
            return None, None, full_path

    def generate_existing_workspace(self):
        # here -----------------------------------Load Dump---------------------------------------------------
        for p in self.workspace_object.project:
            project_item = QTreeWidgetItem(self.project_tree)
            project_item.setText(0, p.name)
            project_item.setData(0, Qt.UserRole, p)
            for d in p.dataset:
                dataset_item = QTreeWidgetItem()
                dataset_item.setText(0, d.name)
                dataset_item.setData(0, Qt.UserRole, d)
                project_item.addChild(dataset_item)
                for cap in d.pcaps:
                    pcap_item = QTreeWidgetItem()
                    pcap_item.setText(0, cap.name)
                    pcap_item.setData(0, Qt.UserRole, cap)
                    dataset_item.addChild(pcap_item)

        return True

    def show_classifier_qt(self, fig):
        raw_html = '<html><head><meta charset="utf-8" />'
        raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        raw_html += '<body>'
        raw_html += po.plot(fig, include_plotlyjs=False, output_type='div')
        raw_html += '</body></html>'

        if self.classifier_plot_view is None:
            self.classifier_plot_view = QWebEngineView()
        # setHtml has a 2MB size limit, need to switch to setUrl on tmp file
        # for large figures.
        self.classifier_plot_view.setHtml(raw_html)

    def create_classifier_plot(self, df):
        fig = px.scatter(df, x='cluster', y='instance_number',
                         color='cluster', color_continuous_scale=px.colors.sequential.Bluered_r)
        # fig.show()
        self.show_classifier_qt(fig)

    def update_traced_data(self):
        """Updates the traced data when a packet is added or deleted
        """
        if self.traced_dataset:
            collection = self.db[self.traced_dataset.name]
            query = {'parent_dataset': self.traced_dataset.name}
            self.traced_data = list(collection.find(query))
        else:
            self.traced_data = None
        self.update_plot()

    def report_progress(self, n: int) -> None:
        """Updates the progress bar from worker signal

        :param n: an integer between 0-100 representing the percentage completed
        :type n: int
        """
        self.progressbar.setValue(n)

    def report_plot_data(self, n: list) -> None:
        """Updates bandwidth plot x & y values from worker signal

        :param n: a list of lists, (list of x values and list of y values)
        :type n: list
        """
        self.plot_x = n[0]
        self.plot_y = n[1]

    def update_plot(self):
        """ Creates a new thread to update bandwidth vs. time graph
        """
        # Step 1: Begin showing progress bar
        self.progressbar.show()
        # Step 2: Create a QThread object
        self.thread_1 = QThread()
        # Step 3: Create a worker object
        self.worker_1 = PlotWorker(self.traced_data)
        # Step 4: Move worker to the thread
        self.worker_1.moveToThread(self.thread_1)
        # Step 5: Connect signals and slots
        self.thread_1.started.connect(self.worker_1.run)
        self.worker_1.finished.connect(self.thread_1.quit)
        self.worker_1.finished.connect(self.worker_1.deleteLater)
        self.thread_1.finished.connect(self.thread_1.deleteLater)
        self.worker_1.progress.connect(self.report_progress)
        self.worker_1.data.connect(self.report_plot_data)
        # Step 6: Start the thread
        self.thread_1.start()

        # Final resets
        self.thread_1.finished.connect(lambda: self.progressbar.setValue(0))
        self.thread_1.finished.connect(lambda: self.progressbar.hide())
        self.thread_1.finished.connect(lambda: self.fig_view.setHtml(create_plot(self.plot_x, self.plot_y)))

    def filter_wireshark(self):

        if self.project_tree.selectedItems():  # and self.check_if_item_is(self.project_tree.selectedItems()[0], "Dataset"):

            if self.test_mode == False:
                dataset_item = self.project_tree.selectedItems()[0]
            for p in self.workspace_object.project:
                for d in p.dataset:
                    if d.name == dataset_item.text(0):
                        ui = filter_gui.filter_window(d.mergeFilePath, self.project_tree, self.workspace_object)

    def display_classifier_options(self):
        results = pd.DataFrame()
        try:
            if self.project_tree.selectedItems():
                if type(self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Dataset:
                    dataset_item = self.project_tree.selectedItems()[0]
                    dataset = dataset_item.data(0, Qt.UserRole)
                    results = self.controller.classify_dataset(dataset.name)
        except:
            raise ''

        self.create_classifier_plot(results)
        self.classifier_window.show()
        return


if __name__ == "__main__":
    args = len(sys.argv)
    try:
        path = os.path.realpath(sys.argv[1])
        if args == 2:
            ui = WorkspaceWindow(path)
        elif args == 3:
            if sys.argv[2] == 'True':
                ui = WorkspaceWindow(path, True)
            else:
                ui = WorkspaceWindow(path)
        ui.run()
    except Exception:
        traceback.print_exc()
