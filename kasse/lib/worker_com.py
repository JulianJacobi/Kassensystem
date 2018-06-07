import socket
from kassensystem.settings import WORKER_SOCKET
import datetime


def send_message(message: str):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(WORKER_SOCKET)

    sock.send(message.encode())

    sock.close()


def set_time(new_time: datetime.datetime):
    send_message('time {}'.format(int(new_time.timestamp())))


def deactivate_interface():
    send_message('interface deactivate')


def set_interface(ip, netmask):
    send_message('interface set {} {}'.format(ip, netmask))
