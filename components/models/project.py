from datetime import datetime
#from dataset import Dataset

class Project:
    def __init__(self, name: str, c_time = datetime.now(), size = 0, datasets = []) -> None:
        self.name = name
        self.c_time = c_time     # creation time
        self.size = size         # size in bytes
        self.dataset = datasets
'''
    def add_dataset(self, new: Dataset) -> list:
        self.dataset.append(new)
        return self.dataset

    def del_datset(self, rm: Dataset) -> list:
        self.dataset.remove(rm)
        return self.dataset
'''