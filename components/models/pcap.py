import os
import shutil
import pyshark

class Pcap:

    def __init__(self, name: str ,path: str, file: str, m_data = "") -> None:
        try:
            self.name = name
            self.path = os.path.join(path, self.name)  # Save location for PCAP File
            self.pcap_file = file  # pcap recieved from user
            self.pcap_data = None  # packet capture object (packets within pcap file)
            self.total_packets = 0
            self.protocols = {}
            self.m_data = m_data   # metadata 

            self.set_packet_data()
            #self.calculate_total_packets() 
            if not self.pcap_file == self.path:
                shutil.copy(self.pcap_file, self.path)  # Copy user input into our directory
        except:
            print("Error adding this pcap")
            self.name = None

    def set_packet_data(self):
        self.pcap_data = pyshark.FileCapture(self.pcap_file)
        return self.pcap_data

    def calculate_total_packets(self) -> int:
        count =[]

        def counter(*args):
            count.append(args[0])

        self.pcap_data.apply_on_packets(counter)
        self.total_packets = len(count)
        return len(count)

    #return lists
    #TODO:
    def calculate_protocols(self) -> dict:
        print("create dictionary from base file, traverse packets and create dictionary based on protocol/occurances")

    #TODO:
    def calculate_timespan(self) -> str:
        print("get last packet time, set as timespan")
        # knows original PCAP names
    #TODO:
    def get_pcap_name(self) -> str:
        print("# knows where PCAP originated from")

        # knows PCAP editable free text meta-data
    
    def save(self, f) -> None:
        f.write('{"name": "%s", "m_data": "%s"' % (self.name, self.m_data))
        f.write('}')

    def remove(self) -> bool:
        return self.__del__()

    def __del__(self) -> bool:
        try:
            shutil.rmtree(self.path)
            return True
        except:
            return False
