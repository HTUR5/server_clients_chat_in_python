from constants import CommandConstants
from my_network import MyClient_TCP, MyClient_UDP, MyServer_UDP


class ClientBL:
    def __init__(self, server_host='localhost', server_port=50000):
        self.__client = MyClient_TCP(server_host, server_port)

        self.__nickname = None

    def wait_for_message_from_server(self):
        return self.__client.get_message_from_server()

    def wait_for_UDP_port_from_server(self):
        msg = str(self.__client.get_message_from_server())
        print(msg)
        file_size = int((msg.split(",")[0]).split("SIZE:")[1])
        file_all_size = int((msg.split(",")[1]).split("ALL_SIZE:")[1])
        port = int(msg.split(",")[-1].split("PORT:")[1])
        self.__client_UDP = MyClient_UDP('127.0.0.1', port)
        print("file size is: {}".format(file_size))
        return self.__client_UDP, file_size, file_all_size

    def connect(self, nickname):
        self.__client.connect()
        self.__nickname = nickname
        self.__client.send_message(f'connect {nickname}')

    def disconnect(self):
        self.__client.send_message('disconnect')
        self.__client.disconnect()

    def send_message_to(self, username, message):
        self.__client.send_message(f'send_msg {username} {message}')

    def send_message_to_all(self, message):
        self.__client.send_message(f'send_msg_all {message}')

    def get_list_of_connected_users(self):
        self.__client.send_message(f'get_users')

    def get_list_of_files(self):
        self.__client.send_message(CommandConstants.GET_LIST_FILE)

    def send_request_to_download_file(self, filename):
        self.__client.send_message(f'download {filename}')

        # return self.wait_for_message_from_server()

    def send_request_to_proceed(self, nickname):
        self.__client.send_message(f'proceed {nickname}')

    def send_request_to_no_proceed(self, nickname):
        self.__client.send_message(f'no_proceed {nickname}')
