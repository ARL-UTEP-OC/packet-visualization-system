from project import Project
import os, shutil

class Workspace:
    def __init__(self, name:str, location:str, project=[]) -> None:
        self.name = name
        self.location = location
        self.project = project
        self.cwd = os.getcwd()
        self.work_dir()

    # TODO: Ask Eyan what would be better
    #def add_project(self, new:Project) -> list:
        #self.project.append(new)
    def add_project(self, name:str) -> list:
        self.project.append(Project(name))
        return self.project

    def del_project(self, old:Project) -> list:
        old.remove()
        self.project.remove(old)
        return self.project

    def work_dir(self) -> str:
        path = os.path.join(self.location, self.name)
        os.mkdir(path)
        os.chdir(path)
        return path

    def close(self) -> bool:
        try:
            path = os.path.join(self.location, self.name)
            os.chdir(self.cwd)
            shutil.rmtree(path)
            return True
        except:
            return False

    def save(self) -> bool:
        try:
            path = os.path.join(self.location, self.name)
            shutil.make_archive(path,'zip', path)
            return True
        except:
            return False

