import threading
import tkinter  # graphical user interface library
import tkinter.scrolledtext
from tkinter import simpledialog

from client_bl import ClientBL

from TransmissionAlgorithms import Simple, SelectiveRepeat

FRAME_SIZE = 1024


class ClientGUI:

    def __init__(self):
        self.__bl = ClientBL(server_port=50001)
        self.__window = None
        self.__nickname = ''

        self.__create_gui()

        self.__server_messages_thread.join(1000)

    def __ask_for_nickname(self):
        self.__nickname = simpledialog.askstring("Nickname", "please choose a nickname", parent=self.__window)

        if self.__nickname is None:
            self.close_window()
        else:
            self.__bl.connect(self.__nickname)

    def __listen_to_messages_from_server(self):
        self.__server_messages_thread = threading.Thread(target=self.__update_chat_with_messages_from_server)
        self.__server_messages_thread.start()

    def __add_message_to_chat(self, message):
        message = f'{message}\n'
        self.text_area.config(state='normal')
        self.text_area.insert('end', message)
        self.text_area.yview('end')
        self.text_area.config(state='disabled')

    def __update_chat_with_messages_from_server(self):
        while True:
            message = self.__bl.wait_for_message_from_server()
            self.__add_message_to_chat(message)

    def __create_chat_area(self):
        self.chat_label = tkinter.Label(self.__window, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.__window, height=10)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

    def __download(self):
        # recipient = self.recipient_input_download.get('1.0', 'end')
        # recipient = recipient.strip()

        transmission_Algorithm = SelectiveRepeat()
        message = self.input_area_download.get('1.0', 'end')
        filename = message.strip()

        response = self.__bl.send_request_to_download_file(filename)
        # print(f'Download response: {response}')
        # if response == 'File not exist':
        #     self.__add_message_to_chat(f'No file: {filename}')
        #     return

        while True:
            self.client_udp, self.file_size, self.file_all_size = self.__bl.wait_for_UDP_port_from_server()
            print((self.client_udp).get_sock())
            flg, last_byte = transmission_Algorithm.get_file(filename, self.client_udp, self.file_size, FRAME_SIZE)
            if flg == "finish":
                self.__add_message_to_chat(
                    "User {} downloaded 50% out of the file. Last byte is: {}".format(self.__nickname, last_byte))
                self.proceed_button.config(state="active")
                self.no_proceed_button.config(state="active")
                if self.file_size == self.file_all_size:
                    self.client_udp.get_sock().close()

                # self.get_button.configure(text="Proceed")

                break
        self.input_area.delete('1.0', 'end')

    def __proceed(self):
        transmission_Algorithm = SelectiveRepeat()
        message = self.input_area_download.get('1.0', 'end')
        filename = message.strip()
        # recipient = self.recipient_input_download.get('1.0', 'end')
        # recipient = recipient.strip()

        self.__bl.send_request_to_proceed(self.__nickname)

        while True:
            flg, last_byte = transmission_Algorithm.get_file(filename, self.client_udp,
                                                             int(self.file_all_size - self.file_size), FRAME_SIZE)
            if flg == "finish":
                self.__add_message_to_chat(
                    "User {} downloaded 100% out of the file. Last byte is: {}".format(self.__nickname, last_byte))
                self.client_udp.get_sock().close()

                self.proceed_button.config(state="active")
                self.no_proceed_button.config(state="active")

                # self.get_button.configure(text="Proceed")

                break

        self.input_area.delete('1.0', 'end')

    def __no_proceed(self):
        # recipient = self.recipient_input_download.get('1.0', 'end')
        # recipient = recipient.strip()
        message = self.input_area_download.get('1.0', 'end')
        message = message.strip()

        self.__bl.send_request_to_no_proceed(self.__nickname)

        while True:
            flg = Simple().get_file(message, self.client_udp)
            if flg == "finish":
                # self.get_button.configure(text="Proceed?")

                break
        self.input_area.delete('1.0', 'end')
        self.input_area.delete('1.0', 'end')

    def __create_get_file_area(self):
        self.msg_label_download = tkinter.Label(self.__window, text="Server File Name:", bg="lightgray")
        self.msg_label_download.config(font=("Arial", 12))
        self.msg_label_download.pack(padx=5, pady=5)

        # self.recipient_input_download = tkinter.Text(self.__window, height=2, width=10)
        # self.recipient_input_download.pack(padx=5, pady=5)

        self.input_area_download = tkinter.Text(self.__window, height=3)
        self.input_area_download.pack(padx=5, pady=5)

        self.get_button = tkinter.Button(self.__window, text="Download", command=self.__download)
        self.get_button.config(font=("Arial", 12))
        self.get_button.pack(padx=10, pady=5)
        self.proceed_button = tkinter.Button(self.__window, text="Proceed", command=self.__proceed)
        self.proceed_button.config(font=("Arial", 12))
        self.proceed_button.pack(padx=10, pady=5)
        self.proceed_button.config(state="disabled")

        self.no_proceed_button = tkinter.Button(self.__window, text="No Proceed", command=self.__no_proceed)
        self.no_proceed_button.config(font=("Arial", 12))
        self.no_proceed_button.pack(padx=10, pady=5)
        self.no_proceed_button.config(state="disabled")

    def __create_message_area(self):
        self.msg_label = tkinter.Label(self.__window, text="Recipient:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.recipient_input = tkinter.Text(self.__window, height=2, width=10)
        self.recipient_input.pack(padx=5, pady=5)

        self.input_area = tkinter.Text(self.__window, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.__window, text="Send", command=self.__send_message)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        self.list_button = tkinter.Button(self.__window, text="get list of users", command=self.__get_list_of_users)
        self.list_button.config(font=("Arial", 12))
        self.list_button.pack(padx=20, pady=5)

        self.list_files_button = tkinter.Button(self.__window, text="get list of files",
                                                command=self.__get_list_of_files)
        self.list_files_button.config(font=("Arial", 12))
        self.list_files_button.pack(padx=20, pady=5)

    def __create_gui(self):
        self.__window = tkinter.Tk()
        scrollbar = tkinter.Scrollbar(self.__window)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        self.__window.configure(bg="lightgray")  # background

        self.__create_chat_area()

        self.__create_message_area()
        self.__create_get_file_area()
        self.__window.protocol("WM_DELETE_WINDOW", self.stop)

        self.__ask_for_nickname()

        self.__listen_to_messages_from_server()

        self.__window.mainloop()

    def __send_message(self):
        recipient = self.recipient_input.get('1.0', 'end')
        recipient = recipient.strip()
        message = self.input_area.get('1.0', 'end')
        message = message.strip()

        if recipient == '':
            self.__bl.send_message_to_all(message)
        else:
            self.__bl.send_message_to(recipient, message)

        self.input_area.delete('1.0', 'end')

    def __get_list_of_users(self):
        self.__bl.get_list_of_connected_users()

    def __get_list_of_files(self):
        self.__bl.get_list_of_files()

    def stop(self):
        self.__bl.disconnect()
        self.__server_messages_thread.join(1000)
        self.close_window()

    def close_window(self):
        self.__window.destroy()
        exit(0)


if __name__ == '__main__':
    client = ClientGUI()
