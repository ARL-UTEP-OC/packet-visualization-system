import json
import os
import platform

from packetvisualization.models.dataset import Dataset
from packetvisualization.models.pcap import Pcap


class TableBackend:

    def gen_frame_string(self, list_in):
        """Generates a list of frame number filters for the use in a tshark display filter. Iterates through
        250 items in the list, and then creates a new frame string in order to not overload the command line.
        """
        frame_string_list = []
        frame_string = ""
        for i in range(len(list_in)):
            if frame_string == "":
                frame_string += "frame.number==" + str(list_in[i])
            else:
                frame_string += " || frame.number==" + str(list_in[i])

            if i % 250 == 0 and i != 0:
                frame_string_list.append(frame_string)
                frame_string = ""

        frame_string_list.append(frame_string)

        return frame_string_list

    def query_id(self, obj_in, db_in, list_in):
        """Queries the database via collection id's and return a cursor object that contains
        all collection items with the id's from list_in
        """

        obj = obj_in
        db = db_in
        data = None

        if type(obj) is Pcap:
            dataset_name = os.path.basename(obj.directory)
            collection = db[dataset_name]
            data = collection.find({"_id": {"$in": list_in}})
        elif type(obj) is Dataset:
            dataset_name = obj.name
            collection = db[dataset_name]
            data = collection.find({"_id": {"$in": list_in}})

        return data

    def query_pcap(self, obj_in, db_in):
        """Queries the database via collection parent_pcaps or parent_datasets and returns a cursor object that contains
        all collection items that contain the specified parent_pcap or parent_dataset
        """
        obj = obj_in
        db = db_in
        data = None

        if type(obj) is Pcap:
            dataset_name = os.path.basename(obj.directory)
            collection = db[dataset_name]
            query = {'parent_dataset': dataset_name, 'parent_pcap': obj.name}
            data = collection.find(query)
        elif type(obj) is Dataset:
            dataset_name = obj.name
            collection = db[dataset_name]
            query = {'parent_dataset': obj.name}
            data = collection.find(query)

        return data

    def convert_to_raw(self, text_in):
        """Converts text_in to a raw hex string
        """
        raw_text = ':'.join(hex(ord(x))[2:] for x in text_in)
        return raw_text

    def convert_to_ascii(self, text_in):
        """Converts text_in to an ASCII string
        """
        ascii = ""
        for char in text_in:
            ascii += str(ord(char)) + " "
        return ascii

    def gen_pcap_from_frames(self, frame_string_list_in, infile_in):
        """Generates multiple pcaps using tshark's display filter and the frame string list generated from
        gen_frame_string. These pcaps are then merged together into tEmPmErGcap.pcap using tshark's mergecap. Finally
        the pcaps generated will be deleted from the system and teh temp_mergecap is returned.
        """
        temp_mergecap = os.path.join(os.getcwd(), "tEmPmErGeCaP.pcap")
        i = 0
        pcap_list = []
        for frame_string in frame_string_list_in:  # Create pcaps for merging
            if platform.system() == "Windows":
                output_file = os.path.join(os.getcwd(), "tEmPpCaP" + str(i) + ".pcap")
                os.system(
                    'cd "C:\Program Files\Wireshark" & tshark -r ' + infile_in + ' -Y \"' + frame_string + '\" -w ' + output_file)
            elif platform.system() == "Linux":
                os.system('tshark -r ' + infile_in + ' -Y \"' + frame_string + '\" -w ' + output_file)

            pcap_list.append(output_file)
            i += 1

        if platform.system() == "Windows":  # Merge pcaps in pcap_list into tEmPmErGe.pcap
            os.system(
                'cd "C:\Program Files\Wireshark" & mergecap -w ' + temp_mergecap + " " + (' '.join(pcap_list)))
        elif platform.system() == "Linux":
            os.system('mergecap -w ' + temp_mergecap + " " + (' '.join(pcap_list)))

        for pcap in pcap_list:
            if os.path.exists(pcap):
                os.remove(pcap)

        return temp_mergecap

    # def reformat_json(self, packet_in):
    #     new = {}
    #     for k, v in packet_in.items():
    #         if isinstance(v, dict):
    #             v = self.reformat_json(v)
    #         new[k.replace('-', '.')] = v
    #     return new
    #
    # def gen_json_file(self, dict_list_in):
    #     temp_json = os.path.join(os.getcwd(), "tEmPjSoN.json")
    #     with open(temp_json, "w") as outfile:
    #         json.dump(dict_list_in, outfile, indent=2)
    #     outfile.close()
    #     return temp_json
    #
    # def convert_json_to_pcap(self, json_in):
    #     if (platform.system()=="Windows"):
    #         os.system("C:\Program Files\Wireshark\tools\json2pcap python json2pcap.py -p " + json_in)
    #     elif(platform.system()=="Linux"):
    #         print()
