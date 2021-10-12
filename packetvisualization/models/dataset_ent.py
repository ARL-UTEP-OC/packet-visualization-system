from sqlalchemy.orm import relationship
from packetvisualization.models.context.database_context import Base, session
from sqlalchemy import Column, Integer, String, Float, ForeignKey
import os

class Dataset(Base):
    __tablename__ = 'Datasets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    merge_file_path = Column(String, nullable=False)
    total_packets = Column(Float, nullable=False)
    protocols = Column(String, nullable=False)
    pcaps = relationship("Pcap")

    def __init__(self, name: str ,path: str) -> None:
        self.name = name
        self.path = os.path.join(path,self.name)
        self.merge_file_path = " " # Path where we will store the merged CAP in Dataset
        self.create_folder()
        self.create_merge_file()


        # self.pcap_data = None  # will probably remove, need to assess use at later stage
        self.protocols = "sample protocol"  # will need to assess at later date, will most likely be filter feature
        self.total_packets = 0  # will need to assess at later date, will most likely be filter feature

    def create_folder(self) -> str: # create save location
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        return self.path

    def create_merge_file(self) -> str:
        filename = self.name + ".pcap"
        path = os.path.join(self.path, filename)
        self.merge_file_path = path
        fp = open(path, 'a')
        fp.close()