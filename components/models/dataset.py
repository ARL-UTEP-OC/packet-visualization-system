from components.models.pcap import Pcap
import os, shutil


class Dataset:
    def __init__(self, name: str, parentPath: str) -> None:  # Not sure if we should pass entire Project object, need to ask team
        self.name = name
        self.pcaps = []
        self.path = os.path.join(parentPath, self.name)
        self.totalPackets = 0
        self.protocols = None  # will write function to get list of protocols associated with packets (dictionary)
        # self.timeSpan = None #  Need further understanding of which time span is being referred to her
        self.create_folder()

    def add_pcap(self, new: Pcap) -> list:
        self.pcaps.append(new)
        return self.pcaps

    def delete_pcap(self, old: Pcap) -> list:
        # old.remove()
        self.pcaps.remove(old)
        return self.pcaps

    def add_pcap_dir(self, location: str) -> list:  # when we recieve directory w/PCAPs as user input
        for file in os.listdir(location):
            self.pcaps.append(Pcap(file, self))  # For each file, create instance of Packet
        return self.pcaps

    def create_folder(self) -> str: # create save location
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        return self.path

    def save(self, f) -> None: # Save file
        f.write('{"name": "%s", "totalPackets": %s, "pcaps": [' % (self.name, self.totalPackets))
        f.write(']}')

    def __del__(self) -> bool:
        try:
            path = os.path.join(os.getcwd(), self.name)  # remove folder
            shutil.rmtree(path)
            return True
        except:
            return False