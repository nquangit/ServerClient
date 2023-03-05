import re
import base64
from threading import Event


class Client:
    __client_socket = None
    __client_address = None
    DEBUG = False
    _NOTIFY = []
    _INFO = []
    _CONNECTED = False
    _COMMAND_RESPONSE = []
    _RESPONSED = False
    _clientInteraction = None
    _STOP = Event()

    def __init__(self, client_socket, client_address, DEBUG) -> None:
        super().__init__()
        self.__client_socket = client_socket
        self.__client_address = client_address
        self.DEBUG = DEBUG

    def response(self):
        # handle the client connection here
        while not self._STOP.is_set():
            # receive data from the client
            try:
                data = self.__client_socket.recv(1024)
                if self.DEBUG:
                    print(
                        f"Received data from {self.__client_address}: {data}")
            except OSError:
                return
            if not data:
                break
            keep_connection = self.__handle_response(data.decode())
            if not keep_connection:
                break

        # close the client socket
        self.__client_socket.close()
        if self.DEBUG:
            print(f"Client disconnected from {self.__client_address}")
        self._NOTIFY.append(
            f"Client disconnected from {self.__client_address}")

    def __handle_response(self, data):
        if not self._CONNECTED:
            if self.__is_valid_ip(data):
                # print(f"Connected from {data}")
                self._NOTIFY.append(f"Connected from {data}")
                self._INFO.append(data)
                self._CONNECTED = True
                return True
            else:
                self.send_message("", "Hello, this is a socket server.")
                self.disconnect()
                return False
        else:
            data = data.split("|")
            if len(data) < 3:
                return True
            if data[0] == "command":
                command = base64.b64decode(data[1].encode()).decode()
                res = data[2]
                # Calculate the number of padding characters needed
                padding = 4 - len(res) % 4
                # Add the padding characters
                res += "=" * padding
                res = res.encode()
                res = base64.b64decode(res).decode()
                self._COMMAND_RESPONSE.append({command: res})
                self._RESPONSED = True
            return True

    def __is_valid_ip(self, ip_address):
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return re.match(pattern, ip_address) is not None

    def get_info(self):
        return self._INFO

    def get_connection(self):
        return self.__client_socket

    def get_address(self):
        return self.__client_address

    def connected(self):
        return self._CONNECTED

    def disconnect(self):
        self._STOP.set()
        self.__client_socket.close()

    def send_message(self, command, message):
        if command == "":
            self.__client_socket.sendall(message.encode())
        elif command == "command":
            message = base64.b64encode(message.encode())
            message = f"{command}|{message.decode()}"
            self.__client_socket.sendall(message.encode())

    def get_command_response(self):
        # print(self._COMMAND_RESPONSE)
        return self._COMMAND_RESPONSE

    def responsed(self):
        return self._RESPONSED

    def reset_responsed(self):
        self._RESPONSED = False

    def set_client_interaction(self, clientInteraction):
        self._clientInteraction = clientInteraction

    def get_client_interaction(self):
        return self._clientInteraction
