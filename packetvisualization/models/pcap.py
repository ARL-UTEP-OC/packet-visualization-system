import os
import shutil
import subprocess
import platform
import traceback


class Pcap:
    def __init__(self, name: str, path: str, file: str) -> None:
        try:
            self.name = name
            self.directory = path
            self.path = os.path.join(path, self.name)  # Save location for PCAP File
            self.pcap_file = file  # pcap recieved from user
            self.total_packets = 0
            self.protocols = {}
            self.json_file = None
            self.file_size = os.path.getsize(self.pcap_file)
            self.split_dir = ""
            self.split_json_dir = ""
            self.large_pcap_flag = False

            if not self.pcap_file == self.path:
                shutil.copy(self.pcap_file, self.path)  # Copy user input into our directory

            if self.file_size > 20480000: #approx 20,000KB
                print("Large PCAP")
                self.large_pcap_flag = True
                self.create_pcap_split_dir()  # Create directory for split files to be placed
                self.split_large_pcap(self.pcap_file, self.split_dir)  # split pcap
                self.create_split_json_dir()  # create directory for jsons associated to split files to be placed

                # self.split_files_to_json(self.split_dir,self.split_json_dir)  # create json for each split
            else:
                self.create_json_file()  # create empty json
                self.toJson()

        except:
            print("Error adding this pcap")
            traceback.print_exc()
            self.name = None

    def create_file(self, file):
        fp = open(file, 'a')
        fp.close()

    def create_json_file(self):
        filename = self.name + ".json"
        path = os.path.join(self.directory, filename)
        self.json_file = path
        self.create_file(path)

    def toJson(self):
        if platform.system() == "Linux":
            os.system('tshark -r ' + self.pcap_file + ' -T json > ' + self.json_file)
        elif platform.system() == "Windows":
            os.system('cd "C:\Program Files\Wireshark" & tshark -r ' + self.pcap_file + ' -T json > ' + self.json_file)

    def cleanup(self):
        if self.large_pcap_flag:
            shutil.rmtree(self.split_json_dir)
            shutil.rmtree(self.split_dir)
        else:
            os.remove(self.json_file)

    def save(self, f) -> None:
        f.write('{"name": "%s"' % self.name)
        f.write('}')

    def remove(self) -> bool:  # Moved to entity operator
        return self.__del__()

    def __del__(self) -> bool:
        try:
            shutil.rmtree(self.path)
            return True
        except:
            return False

    def create_pcap_split_dir(self):
        name = self.name + "-splitdir"
        path = os.path.join(self.directory, name)
        self.split_dir = path
        os.mkdir(path)
        return

    def create_split_json_dir(self):
        name = self.name + "-splitjson"
        path = os.path.join(self.directory, name)
        self.split_json_dir = path
        os.mkdir(path)
        return

    def split_large_pcap(self, pcap_file, split_files_dir):  # create dir with original pcap name
        path = os.path.join(split_files_dir, "packetslice.pcap")
        os.system('cd "C:\Program Files\Wireshark" & editcap -c 10000 ' + pcap_file + " " + path)
        return

    def split_files_to_json(self, split_files_dir, json_files_dir):
        for dirpath, _, filenames in os.walk(split_files_dir):
            for f in filenames:
                json_name = f.replace('.pcap', '.json')
                file = os.path.abspath(os.path.join(dirpath, f))

                json_file = os.path.join(json_files_dir, json_name)
                self.create_file(json_file)

                os.system('cd "C:\Program Files\Wireshark" & tshark -r ' + file + ' -T json > ' + json_file)
