from .Server_Info import *
from .Client import *
import socket


class Server_Method(Server_Info, Client):
    def __init__(self) -> None:
        super().__init__()

    def stop(self):
        self._STOP.set()  # set the stop event to stop the thread
        # self._SOCKET.close()  # close the socket to stop the thread
        for client in self._CLIENT:
            client.disconnect()

    def listen(self):
        threading.Thread(target=self._check_alive, daemon=True).start()
        self.accept_client()

    def accept_client(self):
        while not self._STOP.is_set():
            conn, addr = self._SOCKET.accept()
            client = Client(conn, addr, self.DEBUG)
            thread = threading.Thread(target=client.response, daemon=True)
            thread.start()

            if self.DEBUG:
                print(f"Request to connect from {addr}")
            self._NOTIFY.append(f"Request to connect from {addr}")

            self._LOCK.acquire()
            self._WATING_CLIENT.append(client)
            self._LOCK.release()

    def show_clients(self):
        self._LOCK.acquire()
        print("Connected clients:")
        for i, client in enumerate(self._CLIENT):
            print("  {}. {}".format(i+1, client.get_connection().getpeername()))
        self._LOCK.release()

    def _check_alive(self):
        while not self._STOP.is_set():
            # Make a copy of the clients list to avoid concurrent modification
            with self._LOCK:
                _CLIENT_COPY = self._CLIENT.copy()
                _WAITING_CLIENT_COPY = self._WATING_CLIENT.copy()
            # Check each client connection
            for client in _CLIENT_COPY:
                if client.get_connection()._closed:
                    # Connection is closed or has error, remove it from clients list
                    self._NOTIFY.append(
                        f"Disconnected from {client.get_info()[0]}")
                    with self._LOCK:
                        self._CLIENT.remove(client)

            for client in _WAITING_CLIENT_COPY:
                if client.get_connection()._closed:
                    # Connection is closed or has error, remove it from clients list
                    self._NOTIFY.append(
                        f"""Connection from {client.get_address()} has been lost, removing""")
                    with self._LOCK:
                        self._WATING_CLIENT.remove(client)

                if client.connected():
                    self._NOTIFY.append(
                        f"Connected from {client.get_connection().getpeername()} -> {client.get_info()[0]}")
                    with self._LOCK:
                        self._WATING_CLIENT.remove(client)
                        self._CLIENT.append(client)

    def printNotify(self):
        for i in self._NOTIFY:
            print(i)
