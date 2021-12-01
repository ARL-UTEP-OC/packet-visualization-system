import os
import shutil

from packetvisualization.models.project import Project


class Workspace:
    def __init__(self, name: str, location: str, open_existing: bool = False) -> None:
        self.name = name
        if location == '':
            self.location = os.getcwd()
        else:
            self.location = location
        self.project = []
        self.open_existing = open_existing
        self.path = self.work_dir()

        self.dump_path = self.get_dump_path()
        # self.create_dump_dir(self.dump_path)

    def add_project(self, new: Project) -> list:
        self.project.append(new)
        return self.project

    def del_project(self, old: Project) -> list:
        self.project.remove(old)
        old.remove()
        return self.project

    def find_project(self, name: str) -> Project:
        for p in self.project:
            if p.name == name:
                return p
        return None

    def work_dir(self) -> str:
        tail = "." + self.name  # we want to work inside a temp, hidden folder
        path = os.path.join(self.location, tail)
        if os.path.isdir(path):
            shutil.rmtree(path)
        if not self.open_existing:
            os.mkdir(path)
        return path

    def save(self) -> bool:
        try:
            tail = "." + self.name
            src = os.path.join(self.location, tail)
            dst = os.path.join(self.location, self.name)
            # Create the JSON file that will contain important information
            save_file = os.path.join(self.path, ".save.json")
            with open(save_file, 'w') as f:
                f.write('{"name": "%s", "project": [' % (self.name))
                for p in self.project:
                    p.save(f)
                    if p != self.project[-1]:
                        f.write(',')
                f.write(']}')
            f.close()
            old_save = os.path.join(self.path, "save.json")
            if os.path.isfile(old_save):
                os.remove(old_save)
            os.rename(save_file, old_save)
            # Zip everything in the working directory
            shutil.make_archive(dst, 'zip', src)
            return True
        except Exception:
            return False

    def get_dump_path(self):
        dir_name = self.name + "_dump"
        dump_path = os.path.join(self.path, dir_name)
        return dump_path

    def create_dump_dir(self, path):
        os.mkdir(path)

    def __del__(self) -> bool:
        try:
            tail = "." + self.name
            path = os.path.join(self.location, tail)
            shutil.rmtree(path)
            for p in self.project:
                p.remove()
            self.project = []  # unlink all projects
            return True
        except Exception:
            return False
