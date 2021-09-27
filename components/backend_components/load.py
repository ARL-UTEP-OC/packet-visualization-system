from components.models.workspace import Workspace
from components.models.project import Project
from components.models.dataset import Dataset
from components.models.pcap import Pcap
import json, datetime, os, shutil

class Load:
    def __init__(self):
        self.desctiption = "Class used to load save files."

    def open_zip(self, path:str) -> str:
        try:
            if not os.path.isfile(path):
                raise Exception
            root, ext = os.path.splitext(path)
            if ext.lower() != ".zip":
                raise Exception
            head, tail = os.path.split(root)
            tail = "." + tail
            working_dir = os.path.join(head, tail)
            shutil.unpack_archive(path, working_dir)
            return self.load_workspace(working_dir)
        except Exception:
            print("Error while trying to read ZIP file.")
            return None

    def open_dir(self, path:str) -> str:
        try:
            if not os.path.isdir(path):
                raise Exception
            head, tail = os.path.split(path)
            tail = "." + tail
            working_dir = os.path.join(head, tail)
            if os.path.isdir(working_dir):
                shutil.rmtree(working_dir)
            shutil.copytree(path, working_dir)
            return self.load_workspace(working_dir)
        
        except Exception:
            print("Error while trying to read directory.")
            return None

    def load_workspace(self, path:str) -> Workspace:
        try: 
            head, tail = os.path.split(path)
            with open(os.path.join(path, 'save.json')) as f:
                data = f.read()
            js = json.loads(data)
            if tail[1:] == js['name']:
                w = Workspace(js['name'], head, open_existing=True)
                self.load_project(w, js['project'])
            else:
                w = None
            return w
        except FileNotFoundError:
            print("Specified ZIP or directory does not contain a save file.")
            shutil.rmtree(path)
            return None
        except Exception:
            print("Unable to read save file. File may be corrupted.")
            shutil.rmtree(path)
            return None

    def load_project(self, workspace:Workspace, projects:list) -> list:
        for p in projects:
            proj = Project(p['name'], p['c_time'])
            self.load_dataset(proj, p['dataset'])
            workspace.add_project(proj)
            
    def load_dataset(self, project:Project, datasets:list) -> list:
        for d in datasets:
            data = Dataset(d['name'], project.path)
            self.load_pcap(data, d['pcaps'])
            project.add_dataset(data)
   
    def load_pcap(self, dataset:Dataset, pcaps:list) ->  list:
        for a in pcaps:
            pcap = Pcap(a['name'], dataset.path, os.path.join(dataset.path, a['name']), a['m_data'])
            dataset.add_pcap(pcap)