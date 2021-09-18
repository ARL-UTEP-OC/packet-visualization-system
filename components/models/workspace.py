from project import Project

class Workspace:
    def __init__(self, name: str, location: list, projects = []) -> None:
        self.name = name
        self.location = location  # split before passing to avaoid os path complications
        self.project = projects

    def add_project(self, new: Project) -> list:
        self.project.append(new)
        return self.project

    def del_project(self, rm: Project) -> list:
        self.project.remove(rm)
        return self.project