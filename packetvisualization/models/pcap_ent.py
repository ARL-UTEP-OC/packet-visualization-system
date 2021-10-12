import os.path

from sqlalchemy.orm import relationship
from packetvisualization.models.context.database_context import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
import shutil
import json

class Pcap(Base):
    __tablename__ = 'Pcaps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    pcap_file = Column(String, nullable=False)
    pcap_data = Column(String, nullable=False)
    total_packets = Column(Integer, nullable=False)
    protocols = Column(String, nullable=False)
    m_data = Column(String, nullable=True)
    # packets = relationship("Packet")
    dataset_id = Column(ForeignKey('Datasets.id'))

    def __init__(self, name: str, path: str, pcap_file: str, parentKey: int) -> None:
        try:
            self.name = name
            self.path = path
            self.pcap_file = pcap_file
            self.pcap_data = self.toJSON()
            self.total_packets = 0
            self.protocols = "protocols"
            self.m_data = "m data"
            self.dataset_id = parentKey

            if not self.pcap_file == self.path:
                shutil.copy(self.pcap_file, self.path)  # Copy user input into our directory
        except:
            print("Corrupt PCAP")
            self.name = " "


        self.toJSON()

    def toJSON(self):
        name = self.name
        name = name.strip('.pcap')
        name = name + ".json"

        json_file = os.path.join(self.path, name)
        fp = open(json_file, 'a')
        fp.close()

        os.system('cd "C:\Program Files\Wireshark" & tshark -r ' + self.pcap_file + ' -T json > ' + json_file)

        f = open(json_file)
        data = json.load(f)
        self.total_packets = len(data)
        f.close()

        string_data = json.dumps(data)
        return string_data

