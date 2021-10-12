#
# from sqlalchemy.orm import relationship
# from packetvisualization.models.context.database_context import Base, session
# from sqlalchemy import Column, Integer, String, Float, ForeignKey
# """
# We are using sqlalchemy ORM
# Table relationships: https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html
# Bulk transactions: https://docs.sqlalchemy.org/en/14/orm/persistence_techniques.html#bulk-operations
# """
# class Dataset(Base):
#     __tablename__ = 'Datasets'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String, nullable=False)
#     path = Column(String, nullable=False)
#     merge_file_path = Column(String, nullable=False)
#     total_packets = Column(Float, nullable=False)
#     protocols = Column(String, nullable=False)
#     pcaps = relationship("Pcap")
#
#     def __init__(self, name: str ,path: str, merge_file_path: str, pcap_data: str, total_packets: int, protocols: str) -> None:
#         name = name
#         path = path
#         pcap_data = pcap_data
#         merge_file_path = merge_file_path
#         protocols = protocols
#         total_packets = total_packets
#
# class Pcap(Base):
#     __tablename__ = 'Pcaps'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String, nullable=False)
#     path = Column(String, nullable=False)
#     pcap_file = Column(String, nullable=False)
#     pcap_data = Column(String, nullable=False)
#     total_packets = Column(Integer, nullable=False)
#     protocols = Column(String, nullable=False)
#     m_data = Column(String, nullable=True)
#     packets = relationship("Packet")
#     dataset_id = Column(ForeignKey('Datasets.id'))
#
#     def __init__(self, name: str ,path: str, pcap_file: str, pcap_data: str, total_packets: int, protocols: str, m_data = "") -> None:
#         name = name
#         path = path
#         pcap_file = pcap_file
#         pcap_data = pcap_data
#         total_packets = total_packets
#         protocols = protocols
#         m_data = m_data
#
# class Packet(Base):
#     __tablename__ = 'Packets'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     packet_json = Column(String, nullable=False)
#     pcap_id = Column(ForeignKey('Pcaps.id'))
#
#     def __init__(self, packet_json: str) -> None:
#         self.packet_json = packet_json
#
#
# class EntityOperations():
#     def add_and_commit(self, entity_type, entity_list):
#         session.bulk_save_objects([entity_type() for _ in entity_list])
#         session.commit()
#
#     def bulk_insert_datasets(self, datasets_to_insert):
#         """
#         dataset_to_insert = [
#             dataset(...),
#             dataset(...),
#             dataset(...)
#         ]
#         """
#         self.add_and_commit(Dataset, datasets_to_insert)
#
#     def bulk_insert_packet(self, packets_to_insert):
#         """
#         packets_to_insert = [
#             packet(...),
#             packet(...),
#             packet(...)
#         ]
#         """
#         # session.bulk_save_objects(packets_to_insert)
#         self.add_and_commit(Packet, packets_to_insert)
#
#
#     def bulk_insert_pcaps(self, pcaps_to_insert):
#         """
#         pcaps_to_insert = [
#             pcap(...),
#             pcap(...),
#             pcap(...)
#         ]
#         """
#         self.add_and_commit(Pcap, pcaps_to_insert)
#
#         # DON'T DELETE THIS CODE
#         # self.pcap.__table__.insert().execute([
#         #     {
#         #         'name': p.name,
#         #         'path': p.path,
#         #         'pcap_file': p.pcap_file,
#         #         'pcap_data': p.pcap_data,
#         #         'total_packets': p.total_packets,
#         #         'protocols': p.protocols,
#         #         'm_data': p.m_data
#         #     }
#         #     for p in pcaps_to_insert
#         # ])
#         # session.commit()
#
#
#
#