import os

from PyQt5.QtCore import pyqtSignal, QObject

from packetvisualization.backend_components.entity_operator import EntityOperations
from packetvisualization.models.workspace import Workspace


class LoadWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    data = pyqtSignal(list)

    def __init__(self, workspace_object: Workspace):
        super().__init__()
        self.eo = EntityOperations()
        self.workspace_object = workspace_object

    def load_workspace(self):
        restore_path = os.path.join(self.workspace_object.dump_path, self.workspace_object.name)
        print(restore_path)
        self.eo.restore_db(self.workspace_object.name, restore_path)
        db = self.eo.set_db(self.workspace_object.name)
        self.data.emit([db])
        self.finished.emit()

