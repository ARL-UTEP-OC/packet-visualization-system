# from packetvisualization.backend_components.entity_operator import EntityOperator
import os
import platform
import shutil

from packetvisualization.models.pcap import Pcap


class Dataset:
    def __init__(self, name: str, parent_path: str, m_data: str = '') -> None:
        self.name = name
        self.pcaps = [] # will use children key instead
        self.m_data = m_data
        self.mergeFilePath = None
        self.jsonFilePath = None
        self.path = os.path.join(parent_path, self.name)
        self.totalPackets = 0
        self.protocols = None
        self.create_folder()
        self.create_merge_file()
        self.packet_data = None
        self.has_changed = False
        self.s_time = ''
        self.e_time = ''
        # self.create_json_file()

    def add_pcap(self, new: Pcap) -> list:
        self.pcaps.append(new)
        self.merge_pcaps()
        self.has_changed = True
        return self.pcaps

    def del_pcap(self, old: Pcap): # Replace with DB Query
        self.pcaps.remove(old)
        if self.pcaps != []: # must have at least one pcap to merge
            self.merge_pcaps()
        os.remove(old.path) # delete file in dir
        old.remove()
        self.has_changed = True
        return self.pcaps

    def print_pcaps(self):
        result = ''
        for p in self.pcaps:
            result += p.name
            result += '\n'
        return result[:-1]

    def print_protocols(self):
        result = ''
        for p in self.protocols:
            result += '%s: %s' % (p[0], p[1])
            result += '\n'
        return result[:-1]

    def add_pcap_dir(self, location: str) -> list:  # when we receive directory w/PCAPs as user input
        for file in os.listdir(location):
            self.pcaps.append(Pcap(file, self))  # For each file, create instance of Packet
        return self.pcaps

    def create_folder(self) -> str: # create save location
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        return self.path

    def create_merge_file(self):
        filename = self.name + ".pcap"
        path = os.path.join(self.path, filename)
        self.mergeFilePath = path
        fp = open(path, 'a')
        fp.close()

    def save(self, f) -> None: # Save file
        f.write('{"name": "%s", "m_data": "%s", "pcaps": [' % (self.name, self.m_data))
        for a in self.pcaps:
            a.save(f)
            if a != self.pcaps[-1]:
                f.write(',')
        f.write(']}')

    def merge_pcaps(self):  # Need to update Linux still
        pcapPaths = ""

        if platform.system() == 'Windows':
            for pcap in self.pcaps:
                if pcap.large_pcap_flag:
                    for dirpath, _, filenames in os.walk(pcap.split_dir):
                        for f in filenames:
                            file = os.path.abspath(os.path.join(dirpath,f))
                            pcapPaths += file + " "
                else:
                    pcapPaths += pcap.path + " "

            os.system('cd "C:\\Program Files\\Wireshark\\" & mergecap -w %s %s' % (self.mergeFilePath, pcapPaths))
        elif platform.system() == 'Linux':
            for pcap in self.pcaps:
                pcapPaths += pcap.path + " "

            os.system('mergecap -w %s %s' % (self.mergeFilePath, pcapPaths))

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
