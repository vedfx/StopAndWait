import logging
import sys
from os import getcwd


# ---------- TEST/DEBUG ----------
SIMULATE_ACK_LOSS_PCT = 0.5
SIMULATE_PACKET_LOSS_PCT = 0.1
SIMULATE_FILE_CORRUPTION_PCT = 0.1
# --------------------------------


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s SERVER [%(levelname)s] %(message)s', )
log = logging.getLogger()


workingDir = format(getcwd())


def read_args(file_name):
    args = {}
    with open(file_name) as input:
        for line in input:
            (key, val) = line.strip().split('=')
            args[key] = val
    return args


def print_line():
    print(f"{color.BLACK}{color.UNDERLINE}                                               {color.END}", file=sys.stderr)


def print_star_line():
    print(f"{color.BLACK}{color.BOLD}***********************************************{color.END}", file=sys.stderr)


def msg_packet_sent(sequence_number, server_port, client_port):
    log.info(f"{color.OKGREEN}{color.BOLD}[SEQ={sequence_number}] Packet Sent {color.END}"
             f"{color.OKBLUE}({server_port}) ➞ ({client_port}){color.END}")

def msg_resend_packet(sequence_number):
    log.info(f"{color.HEADER}{color.BOLD}[SEQ={sequence_number}]{color.END} "
             f"{color.OKBLUE}{color.BOLD}[RETRANSMISSION]{color.END} "
             f"{color.OKBLUE}Resending Packet{color.END}")

def msg_invalid_ack(sequence_number):
    log.info(f"{color.HEADER}{color.BOLD}[SEQ={sequence_number}]{color.END} "
             f"{color.FAIL}{color.BOLD}ACK Invalid{color.END}")

def msg_ack_received(sequence_number):
    log.info(f"{color.HEADER}{color.BOLD}[ACK={sequence_number}]{color.END} "
             f"{color.OKBLUE}{color.BOLD}[ACK Received]{color.END}")

def msg_packet_received(sequence_number, server_port, client_port):
    print(f"{color.OKGREEN}{color.BOLD}[SEQ={sequence_number}] Packet Received {color.END}"
          f"{color.OKBLUE}({server_port}) ➞ ({client_port}){color.END}", file=sys.stderr)

def msg_ack_lost(sequence_number):
    log.error(f"{color.FAIL}{color.BOLD}[ACK={sequence_number}]{color.END} "
              f"{color.FAIL}ACK Lost{color.END}")

def msg_simulating_ack_loss(sequence_number):
    print(
        f"{color.FAIL}{color.BOLD}[SIMULATION] Simulating ACK Loss for [ACK={sequence_number}]{color.END}"
        , file=sys.stderr)

def msg_simulating_packet_loss(sequence_number):
    print(
        f"{color.FAIL}{color.BOLD}[SIMULATION] Simulating Packet Loss for [ACK={sequence_number}]{color.END}"
        , file=sys.stderr)

def msg_simulating_packet_corruption(sequence_number):
    print(
        f"{color.FAIL}{color.BOLD}[SIMULATION] Simulating Packet Corruption for [ACK={sequence_number}]{color.END}"
        , file=sys.stderr)

def msg_client_connected(client_ip, client_port):
    print(f"{color.BLACK}{color.BOLD}[Client] {color.END}"
          f"{color.OKGREEN}{color.BOLD}Connection Established{color.END} "
          f"{color.BLACK}({client_ip}:{client_port}){color.END}"
          , file=sys.stderr)

def msg_client_disconnected(client_ip, client_port):
    print(f"{color.BLACK}{color.BOLD}[Client] {color.END}"
          f"{color.FAIL}{color.BOLD}Client Disconnected{color.END} "
          f"{color.BLACK}({client_ip}:{client_port}){color.END}"
          , file=sys.stderr)

def msg_connected(ip, port):
    log.info(f"{color.OKGREEN}{color.BOLD}Connected Established {color.END}"
             f"{color.OKGREEN}({ip}:{port}){color.END}")

def msg_disconnected(ip, port):
    log.info(f"{color.FAIL}{color.BOLD}Disconnected {color.END}"
             f"{color.FAIL}({ip}:{port}){color.END}")

class color:
    BLACK = '\u001b[30m'
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


server_settings = read_args(workingDir + "\\server.in")
server_port = int(server_settings['server_port'])

client_settings = read_args(workingDir + "\\client.in")
server_ip = client_settings['server_ip']
server_port = int(client_settings['server_port'])
client_ip = "127.0.0.1"
client_port = int(client_settings['client_port'])
file_name = client_settings['file_name']



time_out_sec = 2
SERVER_FOLDER = 'server/'
CLIENT_FOLDER = 'client/'
client_timeout_trials = 50000

packet_size = 32768
chunk_size = 4096
