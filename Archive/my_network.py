import socket


class MyServer_TCP:
    __INCOMING_MESSAGE_BUFFER_SIZE = 1024
    __ENCODING = 'utf-8'

    def __init__(self, host='localhost', port=50000):
        self.__host = host
        self.__port = port

        self.__create_server()

    def broadcast_message(self, clients, message):
        for client in clients:
            self.send_message_to_client(client, message)

    def get_host(self):
        return self.__host

    def wait_for_client_connection(self):
        client, _ = self.__server.accept()
        return client

    def send_UDP_port_to_client(self, client, message):
        client.send(self.__string_to_bytes(message))

    def send_message_to_client(self, client, message):
        client.send(self.__string_to_bytes(message))

    def get_message_from_client(self, client):
        message_as_bytes = client.recv(self.__INCOMING_MESSAGE_BUFFER_SIZE)
        return self.__bytes_to_string(message_as_bytes)

    def wait_for_client_connection_and_get_message_from_client(self):
        client = self.wait_for_client_connection()
        return self.get_message_from_client(client)

    def disconnect_from_client(self, client):
        client.close()

    def __create_server(self):
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind((self.__host, self.__port))

        self.__server.listen()

    def __string_to_bytes(self, message_as_string):
        return message_as_string.encode(self.__ENCODING)

    def __bytes_to_string(self, message_as_bytes):
        return message_as_bytes.decode(self.__ENCODING)


class MyClient_TCP:
    __INCOMING_MESSAGE_BUFFER_SIZE = 1024
    __ENCODING = 'utf-8'

    def __init__(self, server_host, server_port):
        self.__server_host = server_host
        self.__server_port = server_port

        self.__sock = None

    def connect(self):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.connect((self.__server_host, self.__server_port))

    def disconnect(self):
        self.__sock.close()

    def send_message(self, message):
        self.__sock.send(self.__string_to_bytes(message))

    def get_message_from_server(self):
        message_as_bytes = self.__sock.recv(self.__INCOMING_MESSAGE_BUFFER_SIZE)
        return self.__bytes_to_string(message_as_bytes)

    def __string_to_bytes(self, message_as_string):
        return message_as_string.encode(self.__ENCODING)

    def __bytes_to_string(self, message_as_bytes):
        return message_as_bytes.decode(self.__ENCODING)


class MyClient_UDP:
    __INCOMING_MESSAGE_BUFFER_SIZE = 1024
    __ENCODING = 'utf-8'

    def __init__(self, server_host, server_port):
        self.__server_host = server_host
        self.__server_port = server_port

        self.__sock = None
        self.connect()
        self.bind(self.__server_host, self.__server_port)

    def connect(self):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.__sock.connect((self.__host, self.__port))

    def bind(self, UDP_IP, UDP_PORT):
        self.__sock.bind((UDP_IP, UDP_PORT))

    def disconnect(self):
        self.__sock.close()

    def send_message(self, message):
        self.__sock.sendto(self.__string_to_bytes(message), (self.__server_host, self.__server_port))

    def get_message_from_server(self):
        message_as_bytes, _ = self.__sock.recvfrom(self.__INCOMING_MESSAGE_BUFFER_SIZE)
        return self.__bytes_to_string(message_as_bytes)

    def __string_to_bytes(self, message_as_string):
        return message_as_string.encode(self.__ENCODING)

    def __bytes_to_string(self, message_as_bytes):
        return message_as_bytes.decode(self.__ENCODING)

    def get_sock(self):
        return self.__sock

    def get_host(self):
        return self.__server_host

    def get_port(self):
        return self.__server_port


class MyServer_UDP:
    __INCOMING_MESSAGE_BUFFER_SIZE = 1024
    __ENCODING = 'utf-8'

    def __init__(self, host='localhost', port=19090):
        self.__host = host
        self.__port = port

        self.__create_server()

    def broadcast_message(self, clients, message):
        for client in clients:
            self.send_message_to_client(client, message)

    # def wait_for_client_connection(self):
    #     # client, _ = self.__server.accept()
    #     _thread.start_new_thread(self.userConnection, (clientAddr, SERVER_PORT + userCount))
    #
    #     return client

    def send_message_to_client(self, client, message):
        ## getting the IP address using socket.gethostbyname() method
        client.sendto(self.__string_to_bytes(message))

    def get_message_from_client(self, client):
        message_as_bytes = client.recvfrom(self.__INCOMING_MESSAGE_BUFFER_SIZE)
        return self.__bytes_to_string(message_as_bytes)

    def wait_for_client_connection_and_get_message_from_client(self):
        client = self.wait_for_client_connection()
        return self.get_message_from_client(client)

    def disconnect_from_client(self, client):
        client.close()

    def get_sock(self):
        return self.__server

    def __create_server(self):
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # self.__server.listen()

    def __bind(self):
        self.__server.bind(('', self.__port))

    def __string_to_bytes(self, message_as_string):
        return message_as_string.encode(self.__ENCODING)

    def __bytes_to_string(self, message_as_bytes):
        return message_as_bytes.decode(self.__ENCODING)
