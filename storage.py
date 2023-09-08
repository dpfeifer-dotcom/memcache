from threading import Lock, Thread
import time

class Storage:
    def __init__(self, index) -> None:
        self.__storage_lock = Lock()
        self.__items: dict[str, Item] = {}
        self.__index = index
        Thread(target=self.__expiry_check, daemon=True).start()

    def SET(self, key: str, value: any, expiration: int = -1):
        if not isinstance(key, str):
            raise TypeError('Wrong key type')
        if not isinstance(expiration, int):
            raise TypeError('Wrong expiration type')
        if expiration == 0:
            raise ValueError('Expiration must be greater then 0')
        item = Item(value, expiration)
        with self.__storage_lock:
            self.__items[key] = item
        return CachedItem()

    def DEL(self, key: str):
        if not isinstance(key, str):
            raise TypeError ('Wrong key type')
        
        with self.__storage_lock:
            try:
                del self.__items[key]
                return CachedItem()
            except Exception as err:
                return CachedItem(error=err.__repr__())

    def GET(self, key):
        if not isinstance(key, str):
            raise TypeError ('Wrong key type')
        
        item = self.__items.get(key)
        if item:
            return CachedItem(value=item.value)
        return CachedItem(error='No data')
    
    def GETEXP(self, key: str) -> (any):
        if not isinstance(key, str):
            raise TypeError ('Wrong key type')
        
        with self.__storage_lock:
            item = self.__items.get(key)
            if item:
                return CachedItem(value=item.expiration)
        return CachedItem(error='No data')
    
    def SETEXP(self, key: str, expiration: int):
        if not isinstance(key, str):
            raise TypeError ('Wrong key type')
        if not isinstance(expiration, int):
            raise TypeError ('Wrong expiration type')
        if expiration < -1 :
            raise ValueError('The expiration cannot be less than -1')
        
        with self.__storage_lock:
            item = self.__items.get(key)
            if item:
                item.expiration = expiration
                return CachedItem()
        return CachedItem(error='No data')
    
    def MOD(self, key: str, new_value: any):
        if not isinstance(key, str):
            raise TypeError('Wrong key type')
        item = self.__items.get(key)
        if item:    
            item.value = new_value
            return CachedItem()
        return CachedItem(error='No data')
    
    def POP(self, key:str) -> (any):
        if not isinstance(key, str):
            raise TypeError('Wrong key type')
        with self.__storage_lock:
            try: 
                item = self.__items.pop(key)
                return CachedItem(value=item.value)
            except KeyError:
                return CachedItem(error='No data')

    def KEYS(self, start: str = ""):
        if not isinstance(start, str):
            raise TypeError('Wrong key type')
        return CachedItem(value=list((key for key in self.__items if key.startswith(start))))

    def LEN(self):
        return CachedItem(value=len(self.__items))
    
    def __expiry_check(self):
        while True:
            for key in set(self.__items.keys()):
                with self.__storage_lock:
                    item = self.__items[key]
                    if item.expiration == -1:
                        continue

                    item.expiration -= 1
                    if item.expiration == 0:
                        del self.__items[key]
                        continue
            time.sleep(1)


class Item:
    def __init__(self, value: any, expiration) -> None:
        self.value: any = value
        self.expiration: int = expiration


class CachedItem:
    def __init__(self, error=None, value=None):
        self.error = error
        self.value = value
