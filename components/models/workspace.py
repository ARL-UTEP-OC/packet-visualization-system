from project import Project
import os, shutil

class Workspace:
    def __init__(self, name:str, location:str, project=[]) -> None:
        self.name = name
        self.location = location
        self.project = project
        self.cwd = os.getcwd()
        self.work_dir()

    def add_project(self, new:Project) -> list:
        self.project.append(new)
        return self.project

    def del_project(self, old:Project) -> list:
        old.remove()
        self.project.remove(old)
        return self.project

    def work_dir(self) -> str:
        tail = "." + self.name # we want to work inside a temp, hidden folder
        path = os.path.join(self.location, tail)
        if not os.path.isdir(path):
            os.mkdir(path)
        os.chdir(path)
        return path

    def close(self) -> bool:
        try:
            tail = "." + self.name
            path = os.path.join(self.location, tail)
            os.chdir(self.cwd)
            shutil.rmtree(path)
            return True
        except:
            return False

    def save(self) -> bool:
        try:
            tail = "." + self.name
            src = os.path.join(self.location, tail)
            dst = os.path.join(self.location, self.name)
            shutil.make_archive(dst,'zip', src)
            return True
        except:
            return False

