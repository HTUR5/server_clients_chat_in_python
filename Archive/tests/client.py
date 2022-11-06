import unittest
import time
import Archive.client_bl
from Archive import *

# from server_bl import ServerBL
# from threading import Thread


class MyTestCase(unittest.TestCase):
    # def run_server(self):
    #     server = ServerBL(port=50001)
    #     server.start()
    #
    # def setUp(self):
    #     thread = Thread(target=self.run_server(), args=())
    #     thread.start()

    def test_connect(self):
        nickname = "hodaya"
        self.client1 = client_bl.ClientBL(server_port=50001)
        self.client1.connect(nickname)
        message = self.client1.wait_for_message_from_server()
        self.client1.disconnect()
        self.assertEqual(message, f"{nickname} connected to the server!")

    def test_send_message_to_client(self):
        nickname_1 = "hodaya"
        nickname_2 = "sivan"
        nickname_3 = "not_exist"
        message_to_send = "hello"
        self.client_1 = client_bl.ClientBL(server_port=50001)
        self.client_1.connect(nickname_1)
        self.client_2 = client_bl.ClientBL(server_port=50001)
        self.client_2.connect(nickname_2)
        self.client_2.wait_for_message_from_server()  # client_2 connected message
        self.client_1.send_message_to(nickname_2,message_to_send)
        message = self.client_2.wait_for_message_from_server()
        print(message)
        self.assertEqual(message, f"{nickname_1}:hello")
        # send message to someone who is not exist
        self.client_2.send_message_to(nickname_3,message_to_send)
        message = self.client_2.wait_for_message_from_server()
        self.assertEqual(message, "ERROR: No client by nickname not_exist.")
        time.sleep(5)
        self.client_2.disconnect()
        self.client_1.disconnect()

    def test_send_message_to_all(self):
        nickname_1 = "hodaya"
        nickname_2 = "sivan"
        message_to_send = "hello"
        self.client_1 = client_bl.ClientBL(server_port=50001)
        self.client_1.connect(nickname_1)
        self.client_2 = client_bl.ClientBL(server_port=50001)
        self.client_2.connect(nickname_2)
        self.client_2.wait_for_message_from_server()  # client_2 connected message
        self.client_1.send_message_to_all(message_to_send)
        message = self.client_2.wait_for_message_from_server()
        print(message)
        time.sleep(5)
        self.client_2.disconnect()
        self.client_1.disconnect()
        self.assertEqual(message, f"{nickname_1}:hello")

    def test_get_list_of_users(self):
        nickname = "hodaya"
        self.client1 = client_bl.ClientBL(server_port=50001)
        self.client1.connect(nickname)
        message = self.client1.wait_for_message_from_server()
        self.assertEqual(message, f"{nickname} connected to the server!")
        self.client1.get_list_of_connected_users()
        message = self.client1.wait_for_message_from_server()
        self.assertEqual(message, "hodaya")
        self.client1.disconnect()

    def test_get_list_of_files(self):
        nickname = "hodaya"
        self.client1 = client_bl.ClientBL(server_port=50001)
        self.client1.connect(nickname)
        message = self.client1.wait_for_message_from_server()
        self.client1.get_list_of_files()
        message = self.client1.wait_for_message_from_server()
        self.assertEqual(message, "asdfadsf\ndata.txt\nfile.txt")
        self.client1.disconnect()

    def test_download(self):
        nickname = "hodaya"
        name_file = "file.txt"
        self.client1 = client_bl.ClientBL(server_port=50001)
        self.client1.connect(nickname)
        message = self.client1.wait_for_message_from_server()
        self.client1.send_request_to_download_file(name_file)
        message = self.client1.wait_for_message_from_server()
        time.sleep(10)
        self.client1.send_request_to_proceed(nickname)
        time.sleep(10)
        # message = self.client1.wait_for_message_from_server()
        # self.assertEqual(message, "asdfadsf\ndata.txt\nfile.txt")
        self.client1.disconnect()


