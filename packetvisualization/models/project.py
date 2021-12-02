from packetvisualization.models.analysis import Analysis
from packetvisualization.models.dataset import Dataset
from datetime import datetime
import os, shutil


class Project:
    def __init__(self, name: str, parent_path: str, c_time=datetime.now().timestamp()) -> None:
        self.name = name
        self.c_time = c_time  # creation time
        self.dataset = []
        self.analysis = []
        self.path = os.path.join(parent_path, self.name)
        self.create_folder()

    def add_dataset(self, new: Dataset) -> list:
        self.dataset.append(new)
        return self.dataset

    def add_analysis(self, new: Analysis) -> list:
        self.analysis.append(new)
        return self.analysis

    def del_dataset(self, old: Dataset) -> list:
        self.dataset.remove(old)
        old.remove()
        return self.dataset

    def del_analysis(self, old: Analysis) -> list:
        self.analysis.remove(old)
        old.remove()
        return self.analysis

    def find_dataset(self, name: str) -> Dataset:
        for d in self.dataset:
            if d.name == name:
                return d
        return None

    def create_folder(self) -> str:
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        return self.path

    def get_size(self):
        units = 0
        total_size = 0
        for path, dirs, filenames in os.walk(self.path):
            for f in filenames:
                fp = os.path.join(path, f)
                total_size += os.path.getsize(fp)

        while total_size > 1024:
            total_size /= 1024
            units += 1
        return self.switch(total_size, units)

    def switch(self, size, units):
        switcher = {
            0: str(size) + " B",
            1: str(round(size, 2)) + " KB",
            2: str(round(size, 2)) + " MB",
            3: str(round(size, 2)) + " GB",
            4: str(round(size, 2)) + " TB"
        }
        return switcher.get(units, "Invalid size")

    def save(self, f) -> None:
        f.write('{"name": "%s", "c_time": %s, "dataset": [' % (self.name, self.c_time))
        for d in self.dataset:
            d.save(f)
            if d != self.dataset[-1]:
                f.write(',')
        f.write('], ')

        f.write('"analysis": [')
        for a in self.analysis:
            a.save(f)
            if a != self.analysis[-1]:
                f.write(',')
        f.write(']}')

    def remove(self) -> bool:
        return self.__del__()

    def __del__(self) -> bool:
        try:
            shutil.rmtree(self.path)
            for d in self.dataset:
                d.remove()
            self.dataset = []  # unlink all datasets
            return True
        except Exception:
            return False
