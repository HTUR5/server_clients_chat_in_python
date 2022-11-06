import copy
import os
import sys
import time

import select

0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3,


class TransmissionAlgorithms:
    def send_file(self, client, filename, addr):
        pass

    def get_file(self, filename, file_size):
        pass


class SelectiveRepeat(TransmissionAlgorithms):
    def __init__(self):
        self.last_pack = "hello"

    @staticmethod
    def create_packet(packet_number, frame_content):
        packet_number = str(packet_number)
        packet_number = '0' * (5 - len(packet_number)) + packet_number

        return packet_number.encode() + frame_content  # packet form: packet_number + frame_content

    def retransmit(self, udp_server, window, address):
        for packet in sorted(window):
            self.send_packet(udp_server, window[packet], address)

    def confirm_frame(self, udp_server, window, frame_size, address):
        print(f'Confirm frame: {min(window)}')
        try:
            udp_server.get_sock().settimeout(2)
            acknowledgement, _ = udp_server.get_sock().recvfrom(frame_size)
            status, packet_number = (acknowledgement.decode("utf-8")).split(":")
        except:
            self.retransmit(udp_server, window, address)
            return

        if status != "ACK" or min(window) != int(packet_number):
            print(f"Packet {packet_number} damaged or lost")
            self.retransmit(udp_server, window, address)
            return

        print(f'Packet {packet_number} confirmed!')
        del window[int(packet_number)]

    @staticmethod
    def send_packet(udp_server, packet, address):
        udp_server.get_sock().sendto(packet, address)

    def send_file(self, udp_server, filename, address, packets_in_file, window_size, frame_size,  file_offset=0):
        file = self.get_file_handler(filename, file_offset)

        window = {}
        current_packet = 0
        done = False

        while not done:
            if current_packet <= packets_in_file:
                packet = self.create_packet(current_packet, file.read(frame_size))
                self.send_packet(udp_server, packet, address)
                print(f'Send packet: {current_packet}')
                window[current_packet] = packet
                current_packet += 1

            if len(window) == window_size or current_packet > packets_in_file:
                self.confirm_frame(udp_server, window, frame_size, address)

                if len(window) == 0 and current_packet > packets_in_file:
                    done = True

        print(f"{current_packet - 1} packets sent")
        file.close()

        return frame_size * packets_in_file

    @staticmethod
    def get_file_handler(filename, file_offset):
        file = open(filename, "rb")
        file.read(file_offset)

        return file

    @staticmethod
    def parse_packet(packet, packet_size):
        INDEX_SIZE = 5
        packet_number = packet[:INDEX_SIZE].decode("utf-8")
        print(f"pack num:{packet_number}")

        try:
            packet_number = int(packet_number)
        except ValueError:
            print("there is a problem in the packet!")
            return None, None

        data = packet[INDEX_SIZE:packet_size]

        return packet_number, data

    def receive_packet(self, udp_server, frame_size, current_packet):
        try:
            udp_server.get_sock().settimeout(2)

            data, server_address = udp_server.get_sock().recvfrom(frame_size * 2)  # limitation of 64 kBytes
            packet_size = sys.getsizeof(data)

            packet_number, data = self.parse_packet(data, packet_size)
            if current_packet != packet_number:
                udp_server.get_sock().sendto(f"NACK:{current_packet}".encode(), server_address)

            udp_server.get_sock().sendto("ACK:".encode() + str(packet_number).encode(), server_address)
            print("ACK:{} sent to {}".format(str(packet_number), server_address))

            return data
        except:
            # udp_server.get_sock().sendto(f"NACK:{current_packet}".encode(), server_address)
            # print(f"NACK:{current_packet} sent to {server_address}")
            pass

    def get_file(self, filename, udp_server, packets_in_file, frame_size):
        filename = f"new_{filename}"
        file = open(sys.path[0] + f"/Recieved_files/{filename}", 'wb')
        current_packet = 0  # counter of packages received
        packets = {}

        # self.receive_packet(udp_server, frame_size, current_packet)
        # time.sleep(0.1)
        while current_packet <= packets_in_file:
            data = self.receive_packet(udp_server, frame_size, current_packet)

            packets[current_packet] = data
            self.last_pack = str(data)

            current_packet += 1

        print('Write to file')
        for packet_number in packets:
            print(f'Write packet: {packet_number}')
            file.write(packets[packet_number])

        # client_udp.get_sock().close()
        return "finish", self.get_last_byte(packets)

    @staticmethod
    def get_last_byte(packets):
        last_packet = ''
        current_packet = max(packets)

        while len(last_packet) == 0:
            last_packet = packets[current_packet]
            current_packet -= 1

        print(f'Last packet: {last_packet}')

        return last_packet[-1]

class Simple(TransmissionAlgorithms):
    def close_resources(self, server):
        server.get_sock().close()
        self.f.close()

    def send_file_second_half(self, server, filename, address):
        data = self.f.read(1024)
        while data:
            if server.get_sock().sendto(bytearray(data, "utf-8"), address):
                data = self.f.read(1024)  # print(data)
                time.sleep(0.02)  # Give receiver a bit time to save

        server.get_sock().close()
        self.f.close()

    def send_file_first_half(self, server, filename, address):
        self.fileSize = os.path.getsize(filename)
        buff_size = min(1024, int(self.fileSize / 2))
        counter_reading = 0
        self.f = open(filename, "r")
        data = self.f.read(buff_size)
        counter_reading += buff_size
        while (counter_reading <= 0.5 * self.fileSize):
            if (server.get_sock().sendto(bytearray(data, "utf-8"), address)):
                data = self.f.read(buff_size)
                counter_reading += buff_size
                time.sleep(0.02)  # Give receiver a bit time to save

        # server.get_sock().close()
        # self.f.close()
        print("finish to send half of the file")
        return "half completed"

    def send_file(self, server, filename, addr):
        self.fileSize = os.path.getsize(filename)
        counter_reading = 0
        f = open(filename, "r")
        data = f.read(1024)
        counter_reading += 1024
        while (data):
            if (server.get_sock().sendto(bytearray(data, "utf-8"), addr)):
                data = f.read(1024)
                counter_reading += 1024
                # print(data)
                time.sleep(0.02)  # Give receiver a bit time to save

        server.get_sock().close()
        f.close()
        print("finish")

    def get_file(self, filename, client_udp, file_size):
        filename = "new_{}".format(filename)
        f = open(sys.path[0] + "/Recieved_files/{}".format(filename), 'w')
        timeout = 3
        while True:

            ready = select.select([client_udp.get_sock()], [], [], timeout)
            if ready[0]:
                data, _ = (client_udp.get_sock()).recvfrom(1024)
                print(data)
                last_byte = bytearray(str(data), 'utf-8')[-1]
                data = data.decode('utf-8')
                f.write(data)
                print(data)


            else:
                f.close()
                print("finish")
                break
        print("finish")
        client_udp.get_sock().close()
        return "finish", last_byte
