import time

from storage import Storage
from server import Server


class MemCache:
    def __init__(self, storages_instance: int = 16) -> None:
        self.__storages_instance = storages_instance
        self.__storages:  list[Storage] = []
        self.__server: Server or None = None

        for i in range(self.__storages_instance):
            self.__storages.append(Storage(index=i))
    
    def __call__(self, storage_index: int = 0) -> Storage:
        
        if not isinstance(storage_index, int):
            raise TypeError ('Wrong storage index type')
        if storage_index >= self.__storages_instance:
            raise ValueError ('Non-existent storage')
        self.selected_storage = storage_index
        return self.__storages[storage_index]

    def with_server(self, port):
        self.__server = Server(self, port)
        return self


def create():
    return MemCache()


a = create().with_server(6000)
for i in range(10):
    a(0).SET('ASD'+str(i), "asdasdasasdasdasdasdasdasdasdsadasdasdasdasd")
    a(0).SET('BSD' + str(i), "asdasdasasdasdasdasdasdasdasdsadasdasdasdasd")
print('START', a(0).KEYS(start='A').value)


while True:
    time.sleep(1)