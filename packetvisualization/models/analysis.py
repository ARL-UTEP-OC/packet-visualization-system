import os
import shutil


class Analysis:

    def __init__(self, name: str, df, features: list, path: str, origin: str, m_data: str = ''):
        self.name = name
        self.df = df
        self.features = features
        self.path = path
        self.origin = origin
        self.m_data = m_data

    def remove(self) -> bool:
        return self.__del__()

    def save(self, f):
        self.df.to_csv(os.path.join(self.path, self.name + ".csv"))
        m_data = self.m_data.replace("\n", "\\n")
        temp = '{"name": "%s", "features": %s, "origin": "%s", "m_data": "%s"}' % (self.name, self.features, self.origin, m_data)
        temp = temp.replace("'", '"')
        f.write(temp)

    def __del__(self) -> bool:
        csv_path = os.path.join(self.path, self.name + ".csv")
        if os.path.isfile(csv_path):
            os.remove(csv_path)
