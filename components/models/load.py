from workspace import Workspace
from project import Project
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
                w = Workspace(js['name'], head)
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
            workspace.add_project(Project(p['name'],p['c_time'],p['dataset']))