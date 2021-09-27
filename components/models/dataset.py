from components.models.pcap import Pcap
import os, shutil

class Dataset:
    def __init__(self, name: str, parentPath: str) -> None:  # Not sure if we should pass entire Project object, need to ask team
        self.name = name
        self.pcaps = []
        self.path = os.path.join(parentPath, self.name)
        self.totalPackets = 0
        self.protocols = None
        self.create_folder()

    def add_pcap(self, new: Pcap) -> list:
        # print("Adding new PCAP")
        self.pcaps.append(new)
        # self.calculate_total_packets()
        return self.pcaps

    def del_pcap(self, old: Pcap):
        self.pcaps.remove(old)
        os.remove(old.path) # delete file in dir
        del old
        return self.pcaps

    def add_pcap_dir(self, location: str) -> list:  # when we receive directory w/PCAPs as user input
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

    def calculate_total_packets(self):
        for pcap in self.pcaps:
            self.totalPackets += pcap.total_packets

        print(self.totalPackets)
        return self.totalPackets

    def remove(self) -> bool:
        return self.__del__()

    def __del__(self) -> bool:
        try:
            shutil.rmtree(self.path)
            for p in self.pcaps:
                p.remove()
            self.pcaps = [] # unlink all pcaps
            return True
        except:
            return False

