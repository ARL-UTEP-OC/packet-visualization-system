from components.models.project import Project
import os, shutil

class Workspace:
    def __init__(self, name:str, location:str, open_existing:bool = False) -> None:
        self.name = name
        if location == '':
            self.location = os.getcwd()
        else:
            self.location = location
        self.project = []
        self.cwd = os.getcwd()
        self.open_existing = open_existing
        self.path = self.work_dir()

    def add_project(self, new:Project) -> list:
        self.project.append(new)
        return self.project

    def del_project(self, old:Project) -> list:
        self.project.remove(old)
        old.remove()
        return self.project

    def find_project(self, name:str) -> Project:
        for p in self.project:
            if p.name == name:
                return p
        return None

    def work_dir(self) -> str:
        tail = "." + self.name # we want to work inside a temp, hidden folder
        path = os.path.join(self.location, tail)
        if not self.open_existing:
            if os.path.isdir(path):
                shutil.rmtree(path)
            os.mkdir(path)
        os.chdir(path)
        return path

    def save(self) -> bool:
        try:
            tail = "." + self.name
            src = os.path.join(self.location, tail)
            dst = os.path.join(self.location, self.name)
            # Create the JSON file that will contain important information
            save_file = ".save.json"
            with open(save_file, 'w') as f:
                f.write('{"name": "%s", "project": [' % (self.name))
                for p in self.project:
                    p.save(f)
                    if p != self.project[-1]:
                        f.write(',')
                f.write(']}')
            f.close()
            if os.path.isfile("save.json"):
                os.remove("save.json")
            os.rename(save_file, "save.json")
            # Zip everything in the working directory
            shutil.make_archive(dst,'zip', src)
            return True
        except Exception:
            return False

    def __del__(self) -> bool:
        try:
            tail = "." + self.name
            path = os.path.join(self.location, tail)
            os.chdir(self.cwd)
            shutil.rmtree(path)
            for p in self.project:
                p.remove()
            self.project = [] # unlink all projects
            return True
        except Exception:
            return False
