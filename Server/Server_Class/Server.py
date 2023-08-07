import socket
from .Server_Method import *
from .GUI import *


class Server(Server_Method):
    def __init__(self) -> None:
        self._SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._SOCKET.bind((self._HOST, self._PORT))
        self._SOCKET.listen()

        self._contactGUIApp()

        if self.DEBUG:
            print(f'Server listening on {self._HOST}:{self._PORT}')
        self._appendNotify(f'Server listening on {self._HOST}:{self._PORT}')

        self._thread = threading.Thread(target=self.listen, daemon=True)
        self._thread.start()
        threading.Thread(target=self._check_alive, daemon=True).start()

    def __del__(self):
        self.stop()  # stop the thread and close the socket when the object is deleted
        print("deleted object")
