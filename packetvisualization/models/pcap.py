import os
import shutil

class Pcap:
    def __init__(self, name: str ,path: str, file: str, m_data = "") -> None:
        try:
            self.name = name
            self.directory = path
            self.path = os.path.join(path, self.name)  # Save location for PCAP File
            self.pcap_file = file  # pcap recieved from user
            self.total_packets = 0
            self.protocols = {}
            self.m_data = m_data   # metadata will go to packet
            self.json_file = None

            if not self.pcap_file == self.path:
                shutil.copy(self.pcap_file, self.path)  # Copy user input into our directory

            self.create_json_file() # create empty json
            self.toJson()
        except:
            print("Error adding this pcap")
            self.name = None

    def create_json_file(self):
        filename = self.name + ".json"
        path = os.path.join(self.directory, filename)
        self.json_file= path
        fp = open(path, 'a')
        fp.close()

    def toJson(self):
        os.system('cd "C:\Program Files\Wireshark" & tshark -r ' + self.pcap_file + ' -T json > ' + self.json_file)

    def clearJson(self):
        print("Test")
        # Remove json file after DB insert

    def save(self, f) -> None: # TODO: Rework
        f.write('{"name": "%s", "m_data": "%s"' % (self.name, self.m_data))
        f.write('}')

    def remove(self) -> bool: # Moved to entity operator
        return self.__del__()

    def __del__(self) -> bool:
        try:
            shutil.rmtree(self.path)
            return True
        except:
            return False
