import os

from PyQt5.QtCore import pyqtSignal, QObject

from packetvisualization.backend_components.entity_operator import EntityOperations
from packetvisualization.backend_components.load import Load
from packetvisualization.models.workspace import Workspace


class LoadWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(list)
    data = pyqtSignal(list)

    def __init__(self, workspace_object: Workspace):
        super().__init__()
        self.eo = EntityOperations()
        self.workspace_object = workspace_object

    def load_workspace(self):
        self.progress.emit([0, "Getting zip..."])
        zip_path = os.path.join(self.workspace_object.location, self.workspace_object.name + ".zip")
        self.progress.emit([5, "Loading zip file to system..."])
        l = Load(self.workspace_object)
        l.open_zip(zip_path)
        self.progress.emit([65, "Loading files to database..."])
        restore_path = os.path.join(self.workspace_object.dump_path, self.workspace_object.name)
        self.eo.restore_db(self.workspace_object.name, restore_path)
        db = self.eo.set_db(self.workspace_object.name)
        self.data.emit([db])
        self.progress.emit([100, "Finished loading zip to system."])
        self.finished.emit()

