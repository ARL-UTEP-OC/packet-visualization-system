from typing import List, TypeVar, Generic

T = TypeVar('T')

class DataBaseOperations(Generic[T]):
    def __init__(self) -> None:
        # Create an empty list with items of type T
        self.items: List[T] = []
        self.entity = T

    def insert(self, records):
        # self.Pcap.__table__.insert().execute([{'bar': 1}, {'bar': 2}, {'bar': 3}])
        self.entity.__table__.insert().execute([{'bar': 1}, {'bar': 2}, {'bar': 3}])

