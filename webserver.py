import socket
import threading
from globalconfig import GlobalConfig

host = ''

def default_on_update(msg: str) -> None:
    ServerController.last_message = msg


class ServerController:
    server_thread: threading.Thread = None
    run_server = True
    last_message: str = ''
    on_update = default_on_update

    @staticmethod
    def update(msg: str) -> None:
        if ServerController.on_update:
            ServerController.on_update(msg)


def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, GlobalConfig.server_port))
    server_socket.settimeout(1)

    print(f'Starting server on {host}:{GlobalConfig.server_port}')

    while ServerController.run_server:
        try:
            message, address = server_socket.recvfrom(1024)
            if message is not None:
                ServerController.update(
                    str(message, encoding=GlobalConfig.encoding))
        except socket.timeout:
            pass


def run_server() -> None:
    ServerController.server_thread = threading.Thread(target=server)
    ServerController.server_thread.start()


def stop_server():
    if not ServerController.server_thread:
        return
    ServerController.run_server = False
    ServerController.server_thread.join()


if __name__ == '__main__':
    ServerController.on_update = lambda msg: print(msg)
    run_server()
    input()
    stop_server()
