import os
import sys
import threading

import numpy as np

from TransmissionAlgorithms import TransmissionAlgorithms, Simple, SelectiveRepeat
from my_network import *

WINDOW_SIZE = 10
FRAME_SIZE = 1024


class ClientsManager:
    def __init__(self):
        self.__nicknames_to_clients = {}
        self.__clients_to_nicknames = {}

    def add(self, nickname, client):
        self.__clients_to_nicknames[client] = nickname
        self.__nicknames_to_clients[nickname] = client

    def get_client_by_nickname(self, nickname):
        return self.__nicknames_to_clients.get(nickname, None)

    def get_nickname_by_client(self, client):
        return self.__clients_to_nicknames.get(client, None)

    def get_all_nicknames(self):
        return self.__nicknames_to_clients.keys()

    def get_all_clients(self):
        return self.__clients_to_nicknames.keys()

    def remove_by_nickname(self, nickname):
        client = self.__nicknames_to_clients.get(nickname, None)
        if client is None:
            return

        del self.__clients_to_nicknames[client]
        del self.__nicknames_to_clients[nickname]

    def remove_by_client(self, client):
        nickname = self.__clients_to_nicknames.get(client, None)
        if nickname is None:
            return

        del self.__clients_to_nicknames[client]
        del self.__nicknames_to_clients[nickname]

    def get_number_of_clients(self):
        return len(list(self.__nicknames_to_clients.keys()))


class ServerBL:
    def __init__(self, host='localhost', port=50000, files_dir='.\downloads'):
        self.__host = host
        self.__port = port
        self.__files_dir = files_dir
        self.__active = True

        self.__server_TCP = None

        self.__clientsManager_TCP = ClientsManager()
        self.__clientsManager_UDP = ClientsManager()

    def start(self):
        self.__init_files_dir()

        self.__server_TCP = MyServer_TCP(self.__host, self.__port)
        self.__server_UDP = MyServer_UDP(self.__host, 19090)
        print("Server running...")

        while True:
            client = self.__server_TCP.wait_for_client_connection()
            self.__handle_client_requests(client)

    def __init_files_dir(self):
        # TODO: handle exceptions
        os.makedirs(self.__files_dir, exist_ok=True)

    def __handle_client_requests(self, client):
        thread = threading.Thread(target=self.__handle_request, args=(client,))
        thread.start()

    def __handle_request(self, client):
        while True:
            message = self.__server_TCP.get_message_from_client(client)
            try:
                command, params = message.split(maxsplit=1)
            except ValueError:
                command, params = message, ''

            dispatch = {
                'connect': self.__handle_connect,
                'get_users': self.__handle_get_users,
                'disconnect': self.__handle_disconnect,
                'send_msg': self.__handle_send_msg,
                'send_msg_all': self.__handle_send_msg_all,
                'get_list_file': self.__handle_get_list_file,
                'download': self.__handle_download,
                'proceed': self.__handle_proceed,
                'no_proceed': self.__handle_no_proceed
            }

            callback = dispatch.get(command, None)
            if callback is None:
                print('Got invalid message from client')
            else:
                callback(client, params)

    def __handle_connect(self, client, params):
        nickname = params  # connect <nickname>

        self.__clientsManager_TCP.add(nickname, client)

        self.__broadcast_message(f"{nickname} connected to the server!")

    def __handle_disconnect(self, client, params):
        nickname = self.__clientsManager_TCP.get_nickname_by_client(client)
        self.__clientsManager_TCP.remove_by_client(client)

        self.__broadcast_message(f"{nickname} disconnected from the server!")

        self.__server_TCP.disconnect_from_client(client)

        sys.exit()

    def __handle_get_users(self, client, params):
        nicknames = self.__clientsManager_TCP.get_all_nicknames()

        self.__server_TCP.send_message_to_client(client, ', '.join(nicknames))

    def __handle_send_msg(self, client, params):
        nickname, message = params.split(maxsplit=1)

        if self.__clientsManager_TCP.get_client_by_nickname(nickname) is None:
            self.__server_TCP.send_message_to_client(client, f"ERROR: No client by nickname {nickname}.")
        else:
            self.__server_TCP.send_message_to_client(self.__clientsManager_TCP.get_client_by_nickname(nickname),
                                                     f'{self.__clientsManager_TCP.get_nickname_by_client(client)}:{message}')

    def __handle_send_msg_all(self, client, params):
        message = params
        self.__broadcast_message(f'{self.__clientsManager_TCP.get_nickname_by_client(client)}:{message}')

    def __handle_get_list_file(self, client, params):
        files_names = os.listdir(self.__files_dir)
        message = 'No files available' if not files_names else '\n'.join(files_names)
        self.__server_TCP.send_message_to_client(client, message)

    def __handle_download(self, client, params):  # params contain the name of the file.
        nickname = params
        self.clientFileName = sys.path[0] + f"\downloads\{params}"

        transmission_algorithm = SelectiveRepeat()

        # Checking if the file exist in server
        if not os.path.isfile(self.clientFileName):
            self.__server_TCP.send_message_to_client(client=client, message="File not exist")
            return
        # the file exists in server
        else:
            new_port = int(19091 + self.__clientsManager_UDP.get_number_of_clients())
            self.file_size = int(str(os.stat(self.clientFileName).st_size // 1024 + 1))

            # self.__server_TCP.send_UDP_port_to_client(client=client,message="PORT:{}".format(new_port))
            print(f"Check file exist :{self.clientFileName}")
            self.__server_TCP.send_message_to_client(client=client,
                                                     message=f"The file exist.\n Start to send to port:{new_port}")
            self.sending_now = int(np.ceil(self.file_size * 0.5))

            self.__server_TCP.send_UDP_port_to_client(client=client,
                                                      message=f"SIZE:{self.sending_now},ALL_SIZE:{self.file_size},PORT:{new_port}")

            self.addr = (self.__server_TCP.get_host(), new_port)
            self.server_UDP = MyServer_UDP(self.addr[0], self.addr[1])
            self.__clientsManager_UDP.add(nickname, (self.server_UDP, self.clientFileName, self.addr))
            print(f"We will send {self.sending_now} packets ")
            self.file_buffer = transmission_algorithm.send_file(self.server_UDP, self.clientFileName, self.addr,
                                                                self.sending_now, WINDOW_SIZE, FRAME_SIZE)

            if self.sending_now == self.file_size:
                self.__server_UDP.disconnect_from_client(self.server_UDP.get_sock())

                self.__clientsManager_UDP.remove_by_nickname(nickname)

            # Simple().send_file_first_half(server_UDP, clientFileName, addr)
            self.__server_TCP.send_message_to_client(client=client,
                                                     message="50% downloaded! Do U want to Continue? Proceed/No_Proceed".format(
                                                         new_port))

    def __handle_proceed(self, client, params):
        if self.sending_now == self.file_size:
            return
        nickname = params

        transmission_Algorithm = SelectiveRepeat()

        # (server_UDP, clientFileName, addr)=self.__clientsManager_UDP.get_client_by_nickname(nickname)
        _ = transmission_Algorithm.send_file(self.server_UDP, self.clientFileName, self.addr,
                                             self.file_size - self.sending_now, WINDOW_SIZE, FRAME_SIZE,
                                             file_offset=self.file_buffer)
        self.__server_TCP.send_message_to_client(client=client,
                                                 message="File downloading finished!")

        self.__server_UDP.disconnect_from_client(self.server_UDP.get_sock())
        self.__clientsManager_UDP.remove_by_nickname(nickname)

    def __handle_no_proceed(self, client, params):
        nickname = params
        (server_UDP, clientFileName, addr) = self.__clientsManager_UDP.get_client_by_nickname(nickname)
        Simple().close_resources(server_UDP)
        self.__clientsManager_UDP.remove_by_nickname(nickname)

    def __broadcast_message(self, message):
        self.__server_TCP.broadcast_message(self.__clientsManager_TCP.get_all_clients(),
                                            message)
