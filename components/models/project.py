
from datetime import datetime
import os, shutil

from components.models.dataset import Dataset

class Project:
    def __init__(self, name:str, c_time=datetime.now().timestamp(), datasets=[], size=0) -> None:
        self.name = name
        self.c_time = c_time     # creation time
        self.size = size         # size in bytes
        self.dataset = datasets
        self.path = os.path.join(os.getcwd(), self.name)
        self.create_folder()

    def add_dataset(self, new:Dataset) -> list:
        self.dataset.append(new)
        self.size = os.path.getsize(self.path)
        return self.dataset

    def del_datset(self, old:Dataset) -> list:
        old.remove()
        self.dataset.remove(old)
        self.size = os.path.getsize(self.path)
        return self.dataset

    def create_folder(self) -> str:
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        self.size = os.path.getsize(self.path)
        return self.path
    
    def remove(self) -> bool:
        try:
            path = os.path.join(os.getcwd(), self.name)
            shutil.rmtree(path)
            return True
        except:
            return False
    
    def save(self, f) -> None:
        f.write('{"name": "%s", "c_time": %s, "dataset": [' % (self.name, self.c_time))
        f.write(']}')