import threading


class Server_Info:
    DEBUG = True
    _HOST = '0.0.0.0'
    _PORT = 13044
    _WATING_CLIENT = []
    _CLIENT = []
    _CLIENT_INFO = []
    _SOCKET = None
    _NOTIFY = []
    _STOP = threading.Event()
    _LOCK = threading.Lock()

    def __init__(self) -> None:
        super().__init__()
