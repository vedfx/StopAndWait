import os
import pickle
import socket

from _shared_functions import *
from datetime import datetime
from hashlib import sha1
from random import randint
from threading import Thread


class Server:
    def __init__(self,
                 server_ip='127.0.0.1',
                 server_port=server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.address = (self.server_ip, self.server_port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.server_ip, self.server_port))
        self.threads = []
        self.thread_count = 0

    def listen(self):
        print_star_line()

        print(f"{color.BLACK}Opening UDP Socket on "
              f"{client_ip}:{client_port}{color.END}", file=sys.stderr)
        self.socket.listen()
        log.info("Success")
        print(f"{color.BLACK}Awaiting Incoming Connections...{color.END}", file=sys.stderr)

        while True:
            try:
                client, address = self.socket.accept()
                msg_client_connected(client_ip, client_port)
                client.settimeout(time_out_sec)

                thread = Thread(target=self.serve_client, args=(client, address))
                self.threads.append(thread)
                thread.start()
                self.thread_count += 1

                print(f"Client ID: {str(self.thread_count)}", file=sys.stderr)

            except KeyboardInterrupt:
                log.info("Server Terminated, Waiting for Threads")
                break

    def send_packet(self, packet, client):
        seq_num = packet.__get__('seq_num')
        client_timeout_count = client_timeout_trials

        while client_timeout_count:
            if randint(1, 100) > SIMULATE_PACKET_LOSS_PCT * 100:
                client.sendto(packet.serialize(), (client_ip, client_port))
            else:
                msg_simulating_packet_loss(seq_num)
                msg_ack_lost(seq_num)

            try:
                res = client.recv(packet_size)

                if not res:
                    msg_client_disconnected(client_ip, client_port)
                    return 0

                pkt = Packet(pickled=res)
                pkt.__print__()

                if pkt.__get__('ack') == '+':
                    return 1
                else:
                    msg_invalid_ack(seq_num)
                    msg_resend_packet(seq_num)

            except socket.timeout:
                msg_resend_packet(seq_num)
                client_timeout_count -= 1
        return 0

    def wait_for_request(self, client, address):
        client_timeout_count = client_timeout_trials

        while client_timeout_count:
            try:
                request = client.recv(packet_size)
                if request:
                    packet = Packet(pickled=request)
                    packet.__print__()
                    return packet
                else:
                    msg_client_disconnected(client_ip, client_port)
                    break
            except socket.timeout:
                client_timeout_count -= 1
        return 0

    def serve_client(self, client, address):
        total_time = datetime.now()
        packet = self.wait_for_request(client, address)

        if not packet:
            return 1

        file = SERVER_FOLDER + packet.__get__('file')

        if os.path.isfile(file):
            packet = Packet(status='found')
            client.sendto(packet.serialize(), (client_ip, client_port))
            seq_num = 0
            bits = 0

            f = open(file=file, mode='rb')
            data = f.read(chunk_size)

            while data:
                bits += 8 * len(data)
                packet = Packet(data=data, seq_num=seq_num)

                if not self.send_packet(packet, client):
                    break
                else:
                    msg_packet_sent(seq_num, server_port, client_port)

                seq_num += 1
                data = f.read(chunk_size)

            log.info("File Transfer Complete")
            total_time = (datetime.now() - total_time).total_seconds()
            print(f"{color.BLACK}Sent {str(bits)} Bits in {str(total_time)} Seconds{color.END}", file=sys.stderr)

        else:
            packet = Packet(status='not_found')
            client.sendto(packet.serialize(), (client_ip, client_port))

        msg_client_disconnected(client_ip, client_port)
        client.close()


class Packet:
    def __init__(self,
                 pickled=None,
                 seq_num=0,
                 data=b'',
                 ack='',
                 file='',
                 status=''):

        if pickled is not None:
            self.packet = pickle.loads(pickled)
        else:
            self.packet = {
                "status":   status,
                "file":     file,
                "ack":      ack,
                "seq_num":  seq_num,
                "checksum": sha1(data).hexdigest() if data else '',
                "data":     data
            }

    def serialize(self):
        return pickle.dumps(self.packet)

    def validate_checksum(self):
        return self.packet['checksum'] == sha1(self.packet['data']).hexdigest()

    def __get__(self, field):
        if field == 'seq_num':
            return str(self.packet[field])
        else:
            return self.packet[field]

    def __print__(self):
        status = self.__get__('status')
        file = self.__get__('file')
        ACK = self.__get__('ack')
        seq_num = str(self.__get__('seq_num'))
        checksum = self.validate_checksum()

        if ACK == '+':
            msg_ack_received(seq_num)
        elif ACK == '-':
            pass
        elif file:
            print(f"{color.BLACK}{color.BOLD}[Client]{color.END} Requesting File: " + file)
        elif status == 'not_found':
            log.error(f"{color.FAIL}{color.BOLD}File Not Found{color.END}")
        else:
            msg_packet_received(seq_num, server_port, client_port)


if __name__ == '__main__':
    Server().listen()
