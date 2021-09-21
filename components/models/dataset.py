import os, shutil
from components.models.pcap import Pcap


class Dataset:
    def __init__(self, name: str, path: str, pcaps = []) -> None:  # Not sure if we should pass entire Project object, need to ask team
        self.name = name
        self.pcaps = pcaps
        self.path = os.path.join(path, self.name)
        self.totalPackets = 0
        self.protocols = None  # will write function to get list of protocols associated with packets (dictionary)
        # self.timeSpan = None #  Need further understanding of which time span is being referred to her
        self.create_folder()

    def add_pcap(self, new: Pcap, file) -> list:
        self.pcaps.append(Pcap(file, self))
        return self.pcaps

    def delete_pcap(self, old: Pcap) -> list:
        # old.remove()
        self.pcaps.remove(old)
        return self.pcaps

    def add_pcap_dir(self, location: str) -> list:  # when we receive directory w/PCAPs as user input
        for file in os.listdir(location):
            self.pcaps.append(Pcap(file, self))  # For each file, create instance of Packet
        return self.pcaps

    def create_folder(self) -> str: # create save location
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        return self.path

    def remove(self) -> bool:
        try:
            path = os.path.join(os.getcwd(), self.name)  # remove folder
            shutil.rmtree(path)
            return True
        except:
            return False

    def save(self, f) -> None: # Save file
        f.write('{"name": "%s", "total_packets": %s,"protocols": %s , "pcaps": [' % (self.name, self.totalPackets,self.protocols))
        f.write(']}')
