from sqlalchemy.orm import relationship
from components.models.context.database_context import Base, session
from sqlalchemy import Column, Integer, String, Float, ForeignKey
"""
We are using sqlalchemy ORM
Table relationships: https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html
Bulk transactions: https://docs.sqlalchemy.org/en/14/orm/persistence_techniques.html#bulk-operations 
"""
class dataset(Base):
    __tablename__ = 'datasets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    merge_file_path = Column(String, nullable=False)
    total_packets = Column(Float, nullable=False)
    protocols = Column(String, nullable=False)
    pcaps = relationship("pcap")

    def __init__(self, name: str ,path: str, merge_file_path: str, pcap_data: str, total_packets: int, protocols: str) -> None:
        name = name
        path = path
        pcap_data = pcap_data
        merge_file_path = merge_file_path
        protocols = protocols
        total_packets = total_packets

class pcap(Base):
    __tablename__ = 'pcaps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    pcap_file = Column(String, nullable=False)
    pcap_data = Column(String, nullable=False)
    total_packets = Column(Integer, nullable=False)
    protocols = Column(String, nullable=False)
    m_data = Column(String, nullable=True)
    dataset_id = Column(ForeignKey('datasets.id'))

    def __init__(self, name: str ,path: str, pcap_file: str, pcap_data: str, total_packets: int, protocols: str, m_data = "") -> None:
        name = name
        path = path
        pcap_file = pcap_file
        pcap_data = pcap_data
        total_packets = total_packets
        protocols = protocols
        m_data = m_data

class EntityOperations():
    def bulk_insert_datasets(self, datasets_to_insert):
        """
        pcaps_to_insert = [
            dataset(...),
            dataset(...),
            dataset(...)
        ]
        """
        session.bulk_save_objects(datasets_to_insert)
        session.commit()

    def bulk_insert_pcaps(self, pcaps_to_insert):
        """
        pcaps_to_insert = [
            pcap(...),
            pcap(...),
            pcap(...)
        ]
        """
        session.bulk_save_objects(pcaps_to_insert)
        session.commit()
        # DON'T DELETE THIS CODE 
        # self.pcap.__table__.insert().execute([
        #     {
        #         'name': p.name,
        #         'path': p.path,
        #         'pcap_file': p.pcap_file,
        #         'pcap_data': p.pcap_data,
        #         'total_packets': p.total_packets,
        #         'protocols': p.protocols,
        #         'm_data': p.m_data
        #     } 
        #     for p in pcaps_to_insert
        # ])
        # session.commit()


        
    