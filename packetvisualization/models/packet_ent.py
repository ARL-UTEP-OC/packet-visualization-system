from sqlalchemy.orm import relationship
from packetvisualization.models.context.database_context import Base, session
from sqlalchemy import Column, Integer, String, Float, ForeignKey

class Packet(Base):
    __tablename__ = 'Packets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    packet_json = Column(String, nullable=False)
    # pcap_id = Column(ForeignKey('Pcaps.id'))

    def __init__(self, packet_json: str) -> None:
        self.packet_json = packet_json