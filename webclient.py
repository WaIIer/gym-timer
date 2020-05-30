import time
import socket
from globalconfig import GlobalConfig

host = socket.gethostbyname(socket.gethostname())


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1.0)
    addr = (
        host,
        GlobalConfig.server_port
    )

    while True:
        msg = input()
        if not msg:
            return

        client_socket.sendto(msg.encode('ascii'), addr)


if __name__ == '__main__':
    main()
