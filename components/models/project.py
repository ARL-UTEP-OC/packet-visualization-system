
from components.models.dataset import Dataset
from datetime import datetime
import os, shutil


class Project:
    def __init__(self, name:str, c_time=datetime.now().timestamp()) -> None:
        self.name = name
        self.c_time = c_time     # creation time
        self.size = 0            # size in bytes
        self.dataset = []
        self.path = os.path.join(os.getcwd(), self.name)
        self.create_folder()

    def add_dataset(self, new:Dataset) -> list:
        self.dataset.append(new)
        self.size = os.path.getsize(self.path)
        return self.dataset

    def del_datset(self, old:Dataset) -> list:
        del old
        self.dataset.remove(old)
        self.size = os.path.getsize(self.path)
        return self.dataset

    def create_folder(self) -> str:
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        self.size = os.path.getsize(self.path)
        return self.path

    def save(self, f) -> None:
        f.write('{"name": "%s", "c_time": %s, "dataset": [' % (self.name, self.c_time))
        for d in self.dataset:
            d.save(f)
            if d != self.dataset[-1]:
                f.write(',')
        f.write(']}')

    def __del__(self) -> bool:
        try:
            path = os.path.join(os.getcwd(), self.name)
            shutil.rmtree(path)
            for d in self.dataset:
                del d
            return True
        except:
            return False