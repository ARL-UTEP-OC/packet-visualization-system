from PyQt5.QtCore import pyqtSignal, QObject

from packetvisualization.backend_components.mongo_manager import MongoManager
from packetvisualization.models.workspace import Workspace


class SaveWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(list)

    def __init__(self, workspace: Workspace):
        super().__init__()
        self.workspace = workspace
        self.eo = MongoManager()

    def run(self):
        self.progress.emit([5, "Dumping database data..."])
        self.eo.dump_db(self.workspace.name, self.workspace.dump_path)
        self.progress.emit([50, "Zipping file. This make take a few minutes..."])
        self.workspace.save()
        self.progress.emit([100, "Finished saving workspace."])
        self.finished.emit()
