import datetime
import socket
import threading
import json
import time
from storage import CachedItem


class Client:
    def __init__(self, host: str, port: int, storage: int = 0):
        self.__host = host
        self.__port = port
        self.__secret: str or None = None
        self.__storage = storage
        self.__connected = False
        self.__socket: socket.socket or None = None
        self.__create_connection()

    def __create_connection(self):
        while True:
            try:
                self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__socket.connect((self.__host, self.__port))
                self.__connected = True
                break
            except Exception as e:
                print(e)
                time.sleep(3)

    def __get_cached_item(self, message_json):
        try:
            self.__send_message(message_json)
            response = self.__socket.recv(1024).decode()
        except Exception as err:
            return CachedItem(error=err)
        response_json = json.loads(response)
        cached_item = CachedItem(error=response_json['payload']['error'], value=response_json['payload']['value'])
        return cached_item

    def __create_message_json(self, msg_type: str, key: str = None, value=None):
        message = ServerMessage()
        message.storage = self.__storage
        message.type = msg_type
        payload = ServerMessagePayload()
        payload.key = key
        payload.value = value
        message.payload = payload.__dict__
        message.secret = self.__secret
        message.encrypted = False
        message_json = json.dumps(message.__dict__, indent=6)
        return message_json

    def __send_message(self, message_json):
        try:
            self.__socket.send(message_json.encode())
        except ConnectionResetError:
            print("Connection reset")
            self.__socket.close()
            self.__connected = False
            while True:
                try:
                    self.__create_connection()
                    self.__socket.send(message_json.encode())
                    break
                except Exception as e:
                    print("Trying connection error:", e)
                    time.sleep(3)

    def SET(self, key: str, value):
        if not isinstance(key, str):
            return CachedItem(error='Wrong key type: ' + str(type(key).__name__))
        message_json = self.__create_message_json(msg_type="SET", key=key, value=value)
        cached_item = self.__get_cached_item(message_json)
        return cached_item

    def GET(self, key: str):
        if not isinstance(key, str):
            return CachedItem(error='Wrong key type: ' + str(type(key).__name__))
        message_json = self.__create_message_json(msg_type="GET", key=key)
        cached_item = self.__get_cached_item(message_json)
        return cached_item

    def DEL(self, key: str):
        if not isinstance(key, str):
            return CachedItem(error='Wrong key type: ' + str(type(key).__name__))
        message_json = self.__create_message_json(msg_type="DEL", key=key)
        cached_item = self.__get_cached_item(message_json)
        return cached_item

    def MOD(self, key, value):
        if not isinstance(key, str):
            return CachedItem(error='Wrong key type: ' + str(type(key).__name__))

        message_json = self.__create_message_json(msg_type="MOD", key=key, value=value)
        cached_item = self.__get_cached_item(message_json)
        return cached_item

    def GETEXP(self, key: str):
        if not isinstance(key, str):
            return CachedItem(error='Wrong key type: ' + str(type(key).__name__))

        message_json = self.__create_message_json(msg_type="GETEXP", key=key)
        cached_item = self.__get_cached_item(message_json)
        return cached_item

    def SETEXP(self, key: str, value):
        if not isinstance(key, str):
            return CachedItem(error='Wrong key type: ' + str(type(key).__name__))

        message_json = self.__create_message_json(msg_type="SETEXP", key=key, value=value)
        cached_item = self.__get_cached_item(message_json)
        return cached_item

    def POP(self, key):
        if not isinstance(key, str):
            return CachedItem(error='Wrong key type: ' + str(type(key).__name__))

        message_json = self.__create_message_json(msg_type="POP", key=key)
        cached_item = self.__get_cached_item(message_json)
        return cached_item

    def KEYS(self, key=""):
        if not isinstance(key, str):
            return CachedItem(error='Wrong key type: ' + str(type(key).__name__))

        message_json = self.__create_message_json(msg_type="KEYS", key=key)
        cached_item = self.__get_cached_item(message_json)
        return cached_item

    def LEN(self):
        message_json = self.__create_message_json(msg_type="LEN")
        cached_item = self.__get_cached_item(message_json)
        return cached_item


class Server:
    def __init__(self, mem_cache, port: int):
        self.__host = socket.gethostbyname(socket.gethostname())
        self.__port = port
        self.__mem_cache = mem_cache
        self.__secret: str or None = None
        self.__SSL: bool = False
        self.__clients: list[ClientConnection] = []
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind((self.__host, self.__port))

        threading.Thread(target=self.__start_server, daemon=True).start()
        threading.Thread(target=self.__start_health_check, daemon=True).start()

    def __start_server(self):
        self.__socket.listen(2)
        print('Server running in', self.__host + ':', self.__port)
        while True:
            connection, address = self.__socket.accept()  # accept new connection
            print("accept connection")
            client_connection = ClientConnection(connection=connection, address=address, mem_cache=self.__mem_cache)
            self.__clients.append(client_connection)

    def __start_health_check(self):
        while True:
            for client in self.__clients:
                print(client.address,
                      "keep alive:",
                      str(client.connection_keep_alive)+"/"+str(client.connection_keep_alive_init))
                client.connection_keep_alive -= 1
                if client.connection_keep_alive <= 0:
                    print("client time out")
                    client.connection.close()
                    self.__clients.remove(client)
                    del client
            time.sleep(1)

    def with_secret(self, secret: str):
        if not isinstance(secret, str):
            raise TypeError('Wrong secret type')
        self.__secret = secret
        return self

    def with_SSL(self):
        self.__SSL = True
        return self


class ClientConnection:
    def __init__(self,
                 connection: socket.socket,
                 address: str,
                 mem_cache,
                 storage: int = 0,
                 connection_keep_alive: int = 10):
        self.connected: datetime.datetime.now()
        self.connection = connection
        self.connection_keep_alive_init = connection_keep_alive
        self.connection_keep_alive = connection_keep_alive
        self.address: str = address
        self.mem_cache = mem_cache
        self.mem_cache_storage = storage
        threading.Thread(target=self.__listen_connection, daemon=True).start()

    def __listen_connection(self):
        while True:
            try:
                print("listen")
                request = self.connection.recv(1024).decode()
            except Exception as e:
                print("listen error", e)
                self.connection.close()
                break
            if not request:
                print("not req")
                break
            data = json.loads(request)
            print("from connected user: " + str(data))
            self.connection_keep_alive = self.connection_keep_alive_init
            cached_item: CachedItem

            if data['type'] == 'GET':
                cached_item = self.mem_cache(data['storage']).GET(data['payload']['key'])
                response_json = self.__create_server_response(cached_item)
                self.connection.send(response_json.encode())
            elif data['type'] == 'SET':
                cached_item = self.mem_cache(data['storage']).SET(data['payload']['key'], data['payload']['value'])
                response_json = self.__create_server_response(cached_item)
                self.connection.send(response_json.encode())
            elif data['type'] == 'DEL':
                cached_item = self.mem_cache(data['storage']).DEL(data['payload']['key'])
                response_json = self.__create_server_response(cached_item)
                self.connection.send(response_json.encode())
            elif data['type'] == 'POP':
                cached_item = self.mem_cache(data['storage']).POP(data['payload']['key'])
                response_json = self.__create_server_response(cached_item)
                self.connection.send(response_json.encode())
            elif data['type'] == 'MOD':
                cached_item = self.mem_cache(data['storage']).MOD(data['payload']['key'], data['payload']['value'])
                response_json = self.__create_server_response(cached_item)
                self.connection.send(response_json.encode())
            elif data['type'] == 'GETEXP':
                cached_item = self.mem_cache(data['storage']).GETEXP(data['payload']['key'])
                response_json = self.__create_server_response(cached_item)
                self.connection.send(response_json.encode())
            elif data['type'] == 'SETEXP':
                cached_item = self.mem_cache(data['storage']).SETEXP(data['payload']['key'], data['payload']['value'])
                response_json = self.__create_server_response(cached_item)
                self.connection.send(response_json.encode())
            elif data['type'] == 'KEYS':
                cached_item = self.mem_cache(data['storage']).KEYS(data['payload']['key'])
                response_json = self.__create_server_response(cached_item)
                self.connection.send(response_json.encode())
            elif data['type'] == 'LEN':
                cached_item = self.mem_cache(data['storage']).LEN()
                response_json = self.__create_server_response(cached_item)
                self.connection.send(response_json.encode())

    def __create_server_response(self, cached_item):
        response = ServerMessage()
        payload = ServerMessagePayload()
        payload.value = cached_item.value
        payload.error = cached_item.error
        response.payload = payload.__dict__
        return json.dumps(response.__dict__)


class ServerMessagePayload:
    key: str = None
    value: str = None
    error: str = None


class ServerMessage:
    type: str = None
    storage: int = None
    secret: str = None
    encrypted: bool = False
    payload: ServerMessagePayload = ServerMessagePayload()

