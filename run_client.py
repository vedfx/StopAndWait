from run_server import *
from socket import timeout
from random import randint

from _shared_functions import *


class Client:
    def __init__(self,
                 client_ip="127.0.0.1",
                 client_port=800):
        self.server_ip = server_ip
        self.client_ip = client_ip
        self.client_port = client_port
        self.server_address = (self.client_ip, self.client_port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def request(self, file):
        self.socket.connect(self.server_address)
        self.socket.settimeout(time_out_sec)
        msg_connected(server_ip, server_port)

        timeout_trials = client_timeout_trials
        while timeout_trials:
            packet = Packet(file=file)
            self.socket.send(packet.serialize())

            try:
                res = self.socket.recv(packet_size)

                if not res:
                    msg_disconnected(server_ip, server_port)
                    break

                packet = Packet(pickled=res)
                packet.__print__()

                if packet.__get__('status') == 'found':
                    break
                elif packet.__get__("status") == 'not_found':
                    print("File Not Found")
                    break
                else:
                    print("Bad Response")
                    break
            except timeout:
                print("File Request Timeout")
                timeout_trials -= 1

        if timeout_trials:
            self.receive_file(file)

    def receive_file(self, file):
        self.socket.settimeout(None)

        received_file = CLIENT_FOLDER + file
        open(file=received_file, mode="wb").close()
        f = open(file=received_file, mode="ab")

        while True:
            try:
                res = self.socket.recv(packet_size)
                if not res:
                    msg_disconnected(server_ip, server_port)
                    break

                packet = Packet(pickled=res)
                packet.__print__()
                seq_num = packet.__get__("seq_num")

                if randint(1, 100) > SIMULATE_FILE_CORRUPTION_PCT * 100:
                    f.write(packet.__get__("data"))
                    ack = Packet(seq_num=seq_num, ack="+")
                    self.socket.send(ack.serialize())
                    log.info(f"[SEQ={seq_num}] ACK Sent")
                else:
                    msg_simulating_packet_corruption(seq_num)
                    ack = Packet(seq_num=seq_num, ack='-')
                    self.socket.send(ack.serialize())

            except Exception as e:
                print(e)
                break
        f.close()
        log.info("File Transfer Complete")
        self.socket.close()


requested_file = file_name
client = Client(client_ip="127.0.0.1", client_port=531)
client.request(requested_file)
