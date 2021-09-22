import os
import shutil
import pyshark


class Pcap:

    def __init__(self, file) -> None:
        self.path = os.path.join(os.getcwd())  # Save location for PCAP File
        self.pcap_file = file  # pcap file path location
        self.pcap_data = None  # packet capture object (packets within pcap file)
        self.total_packets = 0
        self.protocols = {}

        self.set_packet_data()
        self.calculate_total_packets()
        shutil.copy(self.pcap_file, self.path)  # Copy user input into our directory


    def set_packet_data(self):
        self.pcap_data = pyshark.FileCapture(self.pcap_file)
        return self.pcap_data

    def calculate_total_packets(self) -> int:
        for pkt in self.pcap_data:
            self.total_packets += 1
        return self.total_packets

    #TODO:
    def calculate_protocols(self) -> dict:
        print("create dictionary from base file, traverse packets and create dictionary based on protocol/occurances")

    #TODO:
    def calculate_timespan(self) -> str:
        print("get last packet time, set as timespan")
        # knows original PCAP names
    #TODO:
    def get_pcap_name(self) -> str:
        print("get ")
        # knows PCAP editable free text meta-data

        # knows where PCAP originated from
