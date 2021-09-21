import os
import shutil


class Pcap:

    def __init__(self, file) -> None:
        self.path = os.path.join(os.getcwd())  # Save location for PCAP File
        self.pcap_file = file  # Actual File itself
        shutil.copy(self.pcap_file, self.path)  # Copy user input into our directory

    def parse_pcap(self):
        print("Test")
        #go through file
        #parse neccessary data
        #wrtie data to csv


        # knows original PCAP names

        # knows protocols (Needs to be able to seperate by protocol type and number of occurances)

        # knows PCAP editable free text meta-data

        # knows where PCAP originated from
