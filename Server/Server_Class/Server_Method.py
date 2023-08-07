from .Server_Info import *
from .Client import *
import socket
import zmq


class Server_Method(Server_Info, Client):
    def __init__(self) -> None:
        super().__init__()

    def stop(self):
        self._STOP.set()  # set the stop event to stop the thread
        # self._SOCKET.close()  # close the socket to stop the thread
        for client in self._CLIENT:
            client.destroy()

    def listen(self):
        self.accept_client()

    def accept_client(self):
        while not self._STOP.is_set():
            conn, addr = self._SOCKET.accept()
            client = Client(conn, addr, self.DEBUG)
            thread = threading.Thread(target=client.response, daemon=True)
            thread.start()

            if self.DEBUG:
                print(f"Request to connect from {addr}")
            self._appendNotify(f"Request to connect from {addr}")

            self._LOCK.acquire()
            self._WATING_CLIENT.append(client)
            self._sendCommandToGui(UPDATE_WAITING_CLIENT)
            self._LOCK.release()

    def _check_alive(self):
        while not self._STOP.is_set():
            # Make a copy of the clients list to avoid concurrent modification
            with self._LOCK:
                _CLIENT_COPY = self._CLIENT.copy()
                _WAITING_CLIENT_COPY = self._WATING_CLIENT.copy()
            for client in _WAITING_CLIENT_COPY:
                try:
                    client.get_connection().getpeername()
                except OSError:
                    # Connection is closed or has error, remove it from clients list
                    self._appendNotify(
                        f"""Connection from {client.get_address()} has been lost, removing"""
                    )
                    with self._LOCK:
                        self._WATING_CLIENT.remove(client)
                        client.destroy()
                        self._sendCommandToGui(UPDATE_WAITING_CLIENT)
                        continue
                if client.connected() and client._ACCEPT_TO_CONNECT:
                    self._appendNotify(
                        f"Connected from {client.get_connection().getpeername()} -> {client.get_info()[0]}"
                    )
                    with self._LOCK:
                        self._CLIENT.append(client)
                        self._WATING_CLIENT.remove(client)
                        self._sendCommandToGui(UPDATE_WAITING_CLIENT)
                        self._sendCommandToGui(UPDATE_CLIENT)

            # Check each client connection
            for client in _CLIENT_COPY:
                if client.get_connection()._closed:
                    # Connection is closed or has error, remove it from clients list
                    self._appendNotify(
                        f"Disconnected from {client.get_info()[0]}"
                    )
                    with self._LOCK:
                        self._CLIENT.remove(client)
                        client.destroy()
                        self._sendCommandToGui(UPDATE_CLIENT)

            # Delay time
            # time.sleep(self._DELAY_TIME)

    def _contactGUIApp(self):
        self.context = zmq.Context()
        self.contactSocket = self.context.socket(zmq.PUB)
        self.contactSocket.bind(self._contactGUIApplicationAddress)

    def _appendNotify(self, notify):
        self._NOTIFY.append(notify)
        self.contactSocket.send_string(UPDATE_NOTIFY)

    def _sendCommandToGui(self, command):
        self.contactSocket.send_string(command)

    def printNotify(self):
        for i in self._NOTIFY:
            print(i)
