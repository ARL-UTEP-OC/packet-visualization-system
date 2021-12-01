import os
import shutil


class Analysis:

    def __init__(self, name, df, features, path):
        self.name = name
        self.df = df
        self.features = features
        self.path = path

    def remove(self) -> bool:
        return self.__del__()

    def save(self, f):
        self.df.to_csv(os.path.join(self.path, self.name + ".csv"))
        temp = '{"name": "%s", "features": %s}' % (self.name, self.features)
        temp = temp.replace("'", '"')
        f.write(temp)

    def __del__(self) -> bool:
        shutil.rmtree(self.path)
