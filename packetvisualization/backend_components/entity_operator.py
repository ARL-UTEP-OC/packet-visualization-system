from sqlalchemy.orm import relationship
from packetvisualization.models.context.database_context import Base, session
from sqlalchemy import Column, Integer, String, Float, ForeignKey

from packetvisualization.models import pcap_ent as Pcap
from packetvisualization.models import dataset_ent as Dataset



class EntityOperations():

    def insert_dataset(self, dataset):
        session.add(dataset)
        session.commit()

    def remove_dataset(self, dataset_entity):
        # print("Test")
        session.delete(dataset_entity)
        session.commit()

    def insert_pcap(self, pcap):
        session.add(pcap)
        session.commit()

    def remove_pcap(self, pcap_entity):
        print("test")
        session.delete(pcap_entity)
        session.commit()

    def add_and_commit(self, entity_type, entity_list):
        session.bulk_save_objects([entity_type() for _ in entity_list])
        session.commit()

    """
    We will need to bulk insert packet data
    """

    # def bulk_insert_packet(self, packets_to_insert):
    #     """
    #     packets_to_insert = [
    #         packet(...),
    #         packet(...),
    #         packet(...)
    #     ]
    #     """
    #     # session.bulk_save_objects(packets_to_insert)
    #     self.add_and_commit(Packet, packets_to_insert)
