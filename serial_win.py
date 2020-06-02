import serial
import sys
import time
import socket
from globalconfig import GlobalConfig
from webserver import MsgEnum

if sys.argv[1] == 'pi':
    host = socket.gethostbyname('raspberrypi.local')
else:
    host = socket.gethostbyname(socket.gethostname())


ser = serial.Serial('COM7', baudrate=115200, timeout=.5)

char_to_command = {
    'P': MsgEnum.POWER.value,
    '=': MsgEnum.PAUSE.value,
    'S': MsgEnum.STOP.value,
    'A': MsgEnum.UP.value,
    'V': MsgEnum.DOWN.value,
    'L': MsgEnum.LEFT.value,
    'W': MsgEnum.RIGHT.value,
    'R': MsgEnum.RESTART.value,
    '0': '0',
    '1': '1',
    '2': '2',
    '3': '3',
    '4': '4',
    '5': '5',
    '6': '6',
    '7': '7',
    '8': '8',
    '9': '9'
}


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1.0)
    addr = (
        host,
        GlobalConfig.server_port
    )

    while True:
        msg = ser.readline()
        if msg is None:
            continue
        msg = msg.decode('ascii').rstrip()
        if msg in char_to_command.keys():
            print(char_to_command[msg])
            client_socket.sendto(char_to_command[msg].encode('ascii'), addr)


if __name__ == '__main__':
    main()
