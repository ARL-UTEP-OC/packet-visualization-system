from sqlalchemy.orm import relationship
from components.models.context.database_context import Base, session
from sqlalchemy import Column, Integer, String, Float, ForeignKey

from components.models import pcap_ent as Pcap
from components.models import dataset_ent as Dataset



class EntityOperations():

    def insert_dataset(self, dataset):
        session.add(dataset)
        session.commit()

    def insert_pcap(self, pcap):
        session.add(pcap)
        session.commit()

    def add_and_commit(self, entity_type, entity_list):
        session.bulk_save_objects([entity_type() for _ in entity_list])
        session.commit()


    """
    Only Packet data will require a bulk insert, in our case the Dataset entity
    can only be added one at a time. 
    """
    # def bulk_insert_datasets(self, datasets_to_insert):
    #     """
    #     dataset_to_insert = [
    #         dataset(...),
    #         dataset(...),
    #         dataset(...)
    #     ]
    #     """
    #     self.add_and_commit(Dataset, datasets_to_insert)

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

    """
       Only Packet data will require a bulk insert, in our case adding a PCAP entity one at a time (Or a directory
       which is relitively small) will pass inserting one at a time
       """
    # def bulk_insert_pcaps(self, pcaps_to_insert):
    #     """
    #     pcaps_to_insert = [
    #         pcap(...),
    #         pcap(...),
    #         pcap(...)
    #     ]
    #     """
    #     self.add_and_commit(Pcap, pcaps_to_insert)

        # DON'T DELETE THIS CODE
        #We can use this code for the packet data

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