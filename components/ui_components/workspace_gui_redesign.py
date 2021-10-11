import os
import shutil
import traceback
import webbrowser
import zipfile

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QIcon, QKeySequence
from PyQt5.QtWidgets import QMainWindow, QTreeWidget, QPushButton, QVBoxLayout, QProgressBar, QMenu, QWidget, QLabel, \
    QAction, QMessageBox, QDockWidget, QTextEdit, QInputDialog, QTreeWidgetItem, QFileDialog

from components.backend_components.load import Load
# from components.models.context.entities import EntityOperations
from components.models.dataset import Dataset
from components.models.pcap import Pcap
from components.models.project import Project
from components.models.workspace import Workspace
from components.backend_components import Wireshark
from components.backend_components.plot import Plot
from components.ui_components.table_gui import table_gui


class WorkspaceWindow(QMainWindow):
    def __init__(self, workspace_object: Workspace, test_mode: bool = False,
                 existing_flag: bool = False):
        # Workspace Constructor
        super().__init__()
        self.workspace_object = workspace_object
        self.test_mode = test_mode

        self.setWindowTitle("PacketVisualizer - " + self.workspace_object.name)
        self.resize(800, 600)
        # Docked widget for Project Tree
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabels(["Item Name", "Size", "DoC"])
        self.project_tree.setColumnWidth(0, 200)
        self.dock_project_tree = QDockWidget("Project Tree", self)
        self.dock_project_tree.setWidget(self.project_tree)
        self.dock_project_tree.setFloating(False)

        self.setCentralWidget(self.dock_project_tree)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_project_tree)

        self._create_actions()
        self._create_menu_bar()
        self._create_tool_bar()
        self._connect_actions()
        self._create_status_bar()

        if existing_flag:
            self.workspace_object = Load().open_zip(
                os.path.join(workspace_object.location, workspace_object.name + ".zip"))
            self.generate_existing_workspace()

        self.show()

    def _create_actions(self):
        # File Menu Actions
        self.newWorkspaceAction = QAction("New &Workspace", self)
        self.newWorkspaceAction.setStatusTip("Create a new workspace")
        self.newWorkspaceAction.setToolTip("Create a new workspace")

        self.newProjectAction = QAction(QIcon(os.path.join("images", "svg", "add.svg")), "New &Project", self)
        self.newProjectAction.setShortcut("Ctrl+N")
        self.newProjectAction.setStatusTip("Create a new project")
        self.newProjectAction.setToolTip("Create a new project")

        self.newDatasetAction = QAction("New &Dataset", self)
        self.newDatasetAction.setStatusTip("Create a new dataset")
        self.newDatasetAction.setToolTip("Create a new dataset")

        self.newPCAPAction = QAction("New P&CAP", self)
        self.newPCAPAction.setStatusTip("Create a new pcap")
        self.newPCAPAction.setToolTip("Create a new pcap")

        self.gen_table_action = QAction("View Packet Table", self)
        self.gen_table_action.setStatusTip("View Packets in a PCAP")
        self.gen_table_action.setToolTip("View Packets in a PCAP")

        self.openAction = QAction(QIcon(os.path.join("images", "svg", "folder-open.svg")), "&Open...", self)
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.setStatusTip("Open existing workspace")
        self.openAction.setToolTip("Open existing workspace")

        self.saveAction = QAction(QIcon(os.path.join("images", "svg", "save.svg")), "&Save", self)
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.setStatusTip("Save workspace")
        self.saveAction.setToolTip("Save workspace")

        self.deleteAction = QAction(QIcon(os.path.join("images", "svg", "trash.svg")), "&Delete", self)
        self.deleteAction.setShortcut("Del")
        self.deleteAction.setStatusTip("Remove selected item")
        self.deleteAction.setToolTip("Remove item")

        self.exitAction = QAction("&Exit", self)
        self.exitAction.setShortcut("Alt+F4")
        self.exitAction.setStatusTip("Exit workspace")
        self.exitAction.setToolTip("Exit workspace")

        # Edit Menu Actions
        self.cutAction = QAction(QIcon(os.path.join("images", "svg", "cut-outline.svg")), "Cu&t", self)
        self.cutAction.setShortcut(QKeySequence.Cut)

        self.copyAction = QAction(QIcon(os.path.join("images", "svg", "copy.svg")), "&Copy", self)
        self.copyAction.setShortcut(QKeySequence.Copy)

        self.pasteAction = QAction(QIcon(os.path.join("images", "svg", "clipboard.svg")), "&Paste", self)
        self.pasteAction.setShortcut(QKeySequence.Paste)

        # Window Window Actions
        self.openProjectTreeAction = QAction(QIcon(os.path.join("images", "svg", "git-branch.svg")),
                                             "&Project Tree Window", self)
        self.openProjectTreeAction.setStatusTip("Open project tree window")
        self.openProjectTreeAction.setToolTip("Open project tree window")

        # Help Menu Actions
        self.helpContentAction = QAction(QIcon(os.path.join("images", "svg", "help.svg")), "&Help Content", self)
        self.aboutAction = QAction("&About", self)

    def _connect_actions(self):
        # Connect File actions
        self.newWorkspaceAction.triggered.connect(self.new_workspace)
        self.newProjectAction.triggered.connect(self.new_project)
        self.newDatasetAction.triggered.connect(self.new_dataset)
        self.newPCAPAction.triggered.connect(self.new_pcap)
        self.gen_table_action.triggered.connect(self.gen_table)
        self.openAction.triggered.connect(self.open_workspace)
        self.saveAction.triggered.connect(self.save)
        self.deleteAction.triggered.connect(self.delete)
        self.exitAction.triggered.connect(self.exit)
        # Connect Edit actions
        self.cutAction.triggered.connect(self.cut_content)
        self.copyAction.triggered.connect(self.copy_content)
        self.pasteAction.triggered.connect(self.paste_content)
        # Connect Windows actions
        self.openProjectTreeAction.triggered.connect(self.open_project_tree)
        # Connect Help actions
        self.helpContentAction.triggered.connect(self.help_content)
        self.aboutAction.triggered.connect(self.about)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        # File Menu
        file_menu = menu_bar.addMenu("&File")
        new_menu = file_menu.addMenu("&New")
        new_menu.addAction(self.newWorkspaceAction)
        new_menu.addAction(self.newProjectAction)
        new_menu.addAction(self.newDatasetAction)
        new_menu.addAction(self.newPCAPAction)
        new_menu.addAction(self.gen_table_action)
        file_menu.addAction(self.openAction)
        file_menu.addAction(self.saveAction)
        file_menu.addAction(self.deleteAction)
        file_menu.addSeparator()
        file_menu.addAction(self.exitAction)
        # Edit Menu
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.cutAction)
        edit_menu.addAction(self.copyAction)
        edit_menu.addAction(self.pasteAction)
        # Window Menu
        windows_menu = menu_bar.addMenu('&Window')
        windows_menu.addAction(self.openProjectTreeAction)
        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction(self.helpContentAction)
        help_menu.addAction(self.aboutAction)

    def _create_tool_bar(self):
        file_tool_bar = self.addToolBar("File")
        file_tool_bar.addAction(self.newProjectAction)
        file_tool_bar.addAction(self.openAction)
        file_tool_bar.addAction(self.saveAction)
        file_tool_bar.addAction(self.deleteAction)

    def _create_status_bar(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Ready", 3000)

        self.progressbar = QProgressBar()
        self.progressbar.setFixedSize(250, 12)
        self.progressbar.setTextVisible(False)
        self.progressbar.setStyleSheet("QProgressBar::chunk "
                                       "{"
                                       "background-color: grey;"
                                       "}")
        self.statusbar.addPermanentWidget(self.progressbar)
        self.progressbar.hide()

    def contextMenuEvent(self, event):
        menu = QMenu(self.project_tree)

        separator = QAction(self)
        separator.setSeparator(True)

        try:
            # Right-click a project
            if type(self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Project:
                menu.addAction(self.newDatasetAction)
            # Right-click a pcap
            if type(self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Dataset:
                menu.addAction(self.newPCAPAction)
        except Exception:
            pass
        menu.addAction(self.newProjectAction)
        menu.addAction(separator)
        menu.addAction(self.cutAction)
        menu.addAction(self.copyAction)
        menu.addAction(self.pasteAction)
        menu.addAction(self.deleteAction)

        menu.exec(event.globalPos())

    def new_workspace(self, file=None):
        # Logic for creating a new workspace
        try:
            if not self.test_mode:
                file = QFileDialog.getSaveFileName(caption="Choose Workspace location")[0]

            if file != '':
                new_workspace_object = Workspace(name=os.path.basename(file), location=os.path.dirname(file))
                self.workspace = WorkspaceWindow(new_workspace_object)
                self.workspace.show()
                return True
        except Exception:
            traceback.print_exc()
            return False

    def new_project(self):
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
        except Exception:
            print("Error loading this pcap")
            traceback.print_exc()

    def open_workspace(self):
        # Logic for opening an existing project
        try:
            if not self.test_mode:
                file_filter = "zip(*.zip)"
                path = QFileDialog.getOpenFileName(caption="Open existing Workspace", filter=file_filter)[0]

                if path != "":
                    if not self.test_mode:
                        workspace_object = Workspace(name=os.path.basename(path.replace(".zip", "")),
                                                     location=os.path.dirname(path))
                        self.workspace = WorkspaceWindow(workspace_object, existing_flag=True)
                        self.workspace.show()
                        return True
        except Exception:
            traceback.print_exc()

    def save(self):
        # Logic for creating a new project
        self.workspace_object.save()

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
        else:
            return False

    def exit(self):
        # Logic for exiting the program
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

    def open_project_tree(self):
        self.dock_project_tree.show()

    def help_content(self):
        # Logic for help content
        webbrowser.open(os.path.join("documents", "Packet_Visualization.pdf"))

    def about(self):
        # Logic for about
        print("<b>Help > About<\b> clicked")

    def plot_reload(self):
        try:
            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0, Qt.UserRole)) is Dataset or self.test_mode:
                dataset_item = self.project_tree.selectedItems()[0]
                d = dataset_item.data(0, Qt.UserRole)
                self.plot_object.update_pcap(d.mergeFilePath)
            # self.text_label = QtWidgets.QLabel("Changed by replacing")
            # self.text_label.setText("Changed the display text")
        except Exception:
            traceback.print_exc()
            return False

    '''def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        remove_project_action = context_menu.addAction("Remove Project")
        remove_dataset_action = context_menu.addAction("Remove Dataset")
        remove_pcap_action = context_menu.addAction("Remove PCAP")
        context_menu.addSeparator()
        convert_to_csv_action = context_menu.addAction("Convert Dataset to CSV")
        convert_to_json_action = context_menu.addAction("Convert Dataset to JSON")
        context_menu.addSeparator()
        add_pcap_folder_action = context_menu.addAction("Add Folder of PCAP's")
        add_pcap_zip_action = context_menu.addAction("Add zip Folder of PCAP's")

        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action == remove_project_action:
            self.remove_project()
        elif action == remove_dataset_action:
            self.remove_dataset()
        elif action == remove_pcap_action:
            self.remove_pcap()
        elif action == convert_to_csv_action:
            self.convert_dataset_to_csv()
        elif action == convert_to_json_action:
            self.convert_dataset_to_json()
        elif action == add_pcap_folder_action:
            self.add_pcap_folder()
        elif action == add_pcap_zip_action:
            self.add_pcap_zip()'''

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Workspace Close", "Would you like to save this Workspace?",
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            self.workspace_object.save()
            self.workspace_object.__del__()
            event.accept()
        elif reply == QMessageBox.No:
            self.workspace_object.__del__()
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

                table = table_gui(pcap_obj, self.progressbar)
                self.dock_table = QDockWidget("Packet Table", self)
                self.dock_table.setWidget(table)
                self.dock_table.setFloating(False)
                self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_table)

            return
        except:
            traceback.print_exc()

    def open_in_wireshark(self, pcap_item=None, dataset_item=None, merge_flag=False):
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

    def convert_dataset_to_csv(self):
        try:
            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0,
                                                              Qt.UserRole)) is Dataset or self.test_mode == True:
                dataset_item = self.project_tree.selectedItems()[0]
                dataset = dataset_item.data(0, Qt.UserRole)
                dataset_file = dataset.mergeFilePath

                output_file = QFileDialog.getSaveFileName(caption="Choose Output location", filter=".csv (*.csv)")[0]

                os.system(
                    'cd "C:\Program Files\Wireshark" & tshark -r ' + dataset_file + ' -T fields -e frame.number -e '
                                                                                    'ip.src -e ip.dst '
                                                                                    '-e frame.len -e frame.time -e '
                                                                                    'frame.time_relative -e _ws.col.Info '
                                                                                    '-E header=y -E '
                                                                                    'separator=, -E quote=d -E '
                                                                                    'occurrence=f > ' + output_file)
                return True
        except Exception:
            traceback.print_exc()

    def convert_dataset_to_json(self):
        try:
            if self.project_tree.selectedItems() and type(
                    self.project_tree.selectedItems()[0].data(0,
                                                              Qt.UserRole)) is Dataset or self.test_mode == True:
                dataset_item = self.project_tree.selectedItems()[0]
                dataset = dataset_item.data(0, Qt.UserRole)
                dataset_file = dataset.mergeFilePath

                output_file = QFileDialog.getSaveFileName(caption="Choose Output location", filter=".json (*.json)")[0]

                os.system('cd "C:\Program Files\Wireshark" & tshark -r ' + dataset_file + ' > ' + output_file)
                return True
        except Exception:
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
