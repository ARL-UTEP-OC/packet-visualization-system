
import os
import platform
import traceback

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

    def to_csv(self, output_file_in, input_file_in):
        """Convert PCAP file to CSV file
        """
        if platform.system() == "Windows":
            os.system(
                'cd "C:\Program Files\Wireshark" & tshark -r ' + input_file_in + ' -T fields -e frame.number -e '
                                                                              'ip.src -e ip.dst '
                                                                              '-e frame.len -e frame.time -e '
                                                                              'frame.time_relative -e _ws.col.Info '
                                                                              '-E header=y -E '
                                                                              'separator=, -E quote=d -E '
                                                                              'occurrence=f > ' + output_file_in)
        elif platform.system() == "Linux":
            os.system('tshark -r ' + input_file_in + ' -T fields -e frame.number -e '
                                                  'ip.src -e ip.dst '
                                                  '-e frame.len -e frame.time -e '
                                                  'frame.time_relative -e _ws.col.Info '
                                                  '-E header=y -E '
                                                  'separator=, -E quote=d -E '
                                                  'occurrence=f > ' + output_file_in)

    def to_json(self, output_file_in, input_file_in):
        """Converts PCAP file to JSON file
        """
        if platform.system() == "Windows":
            os.system(
                'cd "C:\Program Files\Wireshark" & tshark -r ' + input_file_in + ' -T json > ' + output_file_in)
        if platform.system() == "Linux":
            os.system('tshark -r ' + input_file_in + ' -T json > ' + output_file_in)

    def query_id(self, obj_in, db_in, list_in, test_mode: bool = False):
        """Queries the database via collection id's and return a cursor object that contains
        all collection items with the id's from list_in
        """

        obj = obj_in
        db = db_in
        data = None

        if type(obj) is Pcap:
            if test_mode:
                return True
            dataset_name = os.path.basename(obj.directory)
            collection = db[dataset_name]
            data = collection.find({"_id": {"$in": list_in}})
        elif type(obj) is Dataset:
            if test_mode:
                return True
            dataset_name = obj.name
            collection = db[dataset_name]
            data = collection.find({"_id": {"$in": list_in}})
        else:
            return False

        return data

    def query_pcap(self, obj_in, db_in, test_mode: bool = False):
        """Queries the database via collection parent_pcaps or parent_datasets and returns a cursor object that contains
        all collection items that contain the specified parent_pcap or parent_dataset
        """
        obj = obj_in
        db = db_in
        data = None

        if type(obj) is Pcap:
            if test_mode:
                return True
            dataset_name = os.path.basename(obj.directory)
            collection = db[dataset_name]
            query = {'parent_dataset': dataset_name, 'parent_pcap': obj.name}
            data = collection.find(query)
        elif type(obj) is Dataset:
            if test_mode:
                return True
            dataset_name = obj.name
            collection = db[dataset_name]
            query = {'parent_dataset': obj.name}
            data = collection.find(query)
        else:
            return False

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

    def gen_pcap_from_frames(self, frame_string_list_in, infile_in, progressbar, progress_sig):
        """Generates multiple pcaps using tshark's display filter and the frame string list generated from
        gen_frame_string. These pcaps are then merged together into tEmPmErGcap.pcap using tshark's mergecap. Finally
        the pcaps generated will be deleted from the system and teh temp_mergecap is returned.
        """
        try:
            value = (100 / (len(frame_string_list_in) + 1))
            progressbar_value = 0
            progressbar.show()
            temp_mergecap = os.path.join(os.getcwd(), "tEmPmErGeCaP.pcap")
            i = 0
            pcap_list = []

            for frame_string in frame_string_list_in:  # Create pcaps for merging
                output_file = os.path.join(os.getcwd(), "tEmPpCaP" + str(i) + ".pcap")
                if platform.system() == "Windows":
                    os.system(
                        'cd "C:\Program Files\Wireshark" & tshark -r ' + infile_in + ' -Y \"' + frame_string + '\" -w ' + output_file)
                elif platform.system() == "Linux":
                    os.system('tshark -r ' + infile_in + ' -Y \"' + frame_string + '\" -w ' + output_file)

                pcap_list.append(output_file)
                i += 1
                progressbar_value = progressbar_value + value
                progress_sig.emit(progressbar_value)

            if platform.system() == "Windows":  # Merge pcaps in pcap_list into tEmPmErGe.pcap
                os.system(
                    'cd "C:\Program Files\Wireshark" & mergecap -w ' + temp_mergecap + " " + (' '.join(pcap_list)))
            elif platform.system() == "Linux":
                os.system('mergecap -w ' + temp_mergecap + " " + (' '.join(pcap_list)))

            progress_sig.emit(0)
            progressbar.hide()

            for pcap in pcap_list:
                if os.path.exists(pcap):
                    os.remove(pcap)

            return temp_mergecap
        except:
            traceback.print_exc()

