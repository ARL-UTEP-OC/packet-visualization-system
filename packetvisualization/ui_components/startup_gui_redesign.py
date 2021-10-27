import os
import subprocess
import sys
import traceback

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from packetvisualization.models.workspace import Workspace
from packetvisualization.ui_components.workspace_gui_redesign import WorkspaceWindow


class StartupWindow(QWidget):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    logo = os.path.join(os.path.dirname(__file__), "images", "logo.png")
    app.setWindowIcon(QIcon(logo))
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_window()
        self.workspace = None
        self.workspace_object = None

    def init_window(self):
        self.setWindowTitle("Welcome to PacketVisualizer")
        self.setWindowIcon(QIcon(self.logo))
        self.setFixedSize(600, 175)

        layout = QVBoxLayout()

        info_layout = QHBoxLayout()

        logo = QPushButton()
        logo.setFixedSize(100, 100)
        logo.setStyleSheet("border-image : url(%s);" % self.logo)
        info_layout.addWidget(logo)

        title_layout = QVBoxLayout()

        title = QLabel("Welcome to PacketVisualizer")
        title.setFont(QFont("Helvetica", 24, QFont.Bold))
        title.setAlignment(Qt.AlignHCenter)
        title_layout.addWidget(title)

        sub_text = QLabel("Create a new workspace to start from scratch\nOpen existing workspace from disk")
        sub_text.setAlignment(Qt.AlignHCenter)
        title_layout.addWidget(sub_text)

        info_layout.addLayout(title_layout)
        layout.addLayout(info_layout)

        button_layout = QHBoxLayout()

        new_button = QPushButton("New Workspace", self)
        new_button.clicked.connect(self.open_new_workspace)
        button_layout.addWidget(new_button)

        existing_button = QPushButton("Open Workspace", self)
        existing_button.clicked.connect(self.open_existing_workspace)
        button_layout.addWidget(existing_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def open_new_workspace(self, path=None):
        path = QFileDialog.getSaveFileName(caption="Choose Workspace location")[0]

        if path != '':
            self.workspace = WorkspaceWindow(path)
            self.close()
            self.workspace.show()

    '''def open_new_workspace(self):
        path = QFileDialog.getSaveFileName(caption="Choose Workspace location")[0]
        if path != "":
            gui_path = os.path.join('packetvisualization', 'ui_components', 'workspace_gui_redesign.py')
            subprocess.Popen(['python3', gui_path, path])
            self.close()'''

    def open_existing_workspace(self):
        file_filter = "zip(*.zip)"
        path = QFileDialog.getOpenFileName(caption="Open existing Workspace", filter=file_filter)[0]

        if path != "":
            self.workspace = WorkspaceWindow(path, existing_flag=True)
            self.close()
            self.workspace.show()
            return True

    '''def open_existing_workspace(self):
        file_filter = "zip(*.zip)"
        path = QFileDialog.getOpenFileName(caption="Open existing Workspace", filter=file_filter)[0]
        if path != "":
            gui_path = os.path.join('packetvisualization', 'ui_components', 'workspace_gui_redesign.py')
            subprocess.Popen(['python3', gui_path, path.replace(".zip", ""), 'True'])
            self.close()'''

    def run_program(self):
        self.show()
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    ui = StartupWindow()
    ui.run_program()
