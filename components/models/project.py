#from dataset import Dataset
from datetime import datetime
import os, shutil

class Project:
    def __init__(self, name: str, c_time = datetime.now(), size = 0, datasets = []) -> None:
        self.name = name
        self.c_time = c_time     # creation time
        self.size = size         # size in bytes
        self.dataset = datasets
        self.create_folder()
    '''
    def add_dataset(self, new: Dataset) -> list:
        self.dataset.append(new)
        return self.dataset

    def del_datset(self, rm: Dataset) -> list:
        rm.remove()
        self.dataset.remove(rm)
        return self.dataset
    '''
    def create_folder(self) -> str:
        path = os.path.join(os.getcwd(), self.name)
        os.mkdir(path)
        return path
    
    def remove(self) -> bool:
        try:
            path = os.path.join(os.getcwd(), self.name)
            shutil.rmtree(path)
            return True
        except:
            return False